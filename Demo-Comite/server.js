const express = require("express");
const path = require("path");
const fs = require("fs");
const https = require("https");
const crypto = require("crypto");
const config = require("./lib/config");
const { runDlqDemo } = require("./lib/dlq-demo");

const {
  emptyJourney,
  initDeliveries,
  formatDelivery,
  findDelivery,
  findDeliveryByOrderId,
  getActiveDelivery,
  assignOrderToRoute,
  bindDeliveriesSession,
  normalizeDeliveryIds,
} = require("./lib/deliveries");

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const session = {
  lastOrder: null,
  lastIdempotencyKey: null,
  activeDeliveryId: null,
  deliveries: initDeliveries(),
};

bindDeliveriesSession(session);
normalizeDeliveryIds();

function resetJourney() {
  return emptyJourney();
}

async function proxyJson(url, options = {}) {
  const timeoutMs = Number(options.timeoutMs) || 20000;
  const { timeoutMs: _drop, ...fetchOptions } = options;
  try {
    const res = await fetch(url, {
      ...fetchOptions,
      signal: AbortSignal.timeout(timeoutMs),
    });
    const text = await res.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { raw: text };
    }
    return { status: res.status, data, networkError: false, url };
  } catch (err) {
    let host = url;
    try {
      host = new URL(url).host;
    } catch {
      /* ignore */
    }
    console.warn(`[proxy] ${host}: ${err.message}`);
    return {
      status: 503,
      networkError: true,
      url,
      data: {
        error: `Sin conexión con ${host}`,
        detail: err.cause?.code || err.message,
      },
    };
  }
}

function upstreamUi(result, cloud) {
  if (!result.networkError) return null;
  return userMessage("upstream_down", 503, result.data, { cloud });
}

function apimHeaders(extra = {}) {
  return {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": config.apimKey,
    ...extra,
  };
}

function guid() {
  return crypto.randomUUID();
}

function formatOrderIdForUi(orderId) {
  if (!orderId) return "—";
  if (orderId.length <= 16) return orderId;
  return `${orderId.slice(0, 8)}…${orderId.slice(-6)}`;
}

function userMessage(type, httpStatus, data, extra = {}) {
  const orderId = data?.orderId || session.lastOrder?.orderId;
  const map = {
    order_created: {
      title: "¡Pedido confirmado!",
      message: `Tu orden ${orderId} fue registrada. Reservamos unidades en almacén y el WMS confirmó el despacho.`,
      tone: "success",
      scenario: "E1",
    },
    order_duplicate: {
      title: "Pedido ya registrado",
      message: `Detectamos el mismo envío (${orderId}). No se duplicó la reserva ni el cobro.`,
      tone: "warning",
      scenario: "E2",
    },
    order_no_stock: {
      title: "Sin unidades en almacén",
      message: "No hay cantidad suficiente de esa referencia en el CD para despachar. Ajusta la cantidad o el SKU.",
      tone: "warning",
      scenario: "E3",
    },
    order_wms_down: {
      title: "Almacén no disponible",
      message: `El WMS no respondió. Liberamos la reserva automáticamente (Saga). Ref: ${orderId || "—"}`,
      tone: "error",
      scenario: "E4",
    },
    tracking: {
      title: "Estado del envío",
      message: extra.trackingMessage || `Tu pedido está ${data?.status === "IN_TRANSIT" ? "en tránsito" : data?.status || "en proceso"}.`,
      tone: "info",
      scenario: "E8",
    },
    delivery_done: {
      title: "Entrega completada",
      message: "El conductor confirmó la entrega en ruta. Cliente notificado.",
      tone: "success",
      scenario: "E6",
    },
    evidence_ok: {
      title: "Evidencia aceptada",
      message: "Foto de entrega verificada. Integridad del hash correcta.",
      tone: "success",
      scenario: "E7",
    },
    evidence_bad: {
      title: "Evidencia rechazada",
      message: "La foto no pasó validación de integridad. Se solicita nueva captura.",
      tone: "warning",
      scenario: "E7",
    },
    dlq_ok: {
      title: "Pedido detenido — revisar y reprocesar",
      message: extra.narrative || "El aviso de inventario no se procesó. Transporte puede solicitar reproceso auditado.",
      tone: "warning",
      scenario: "E5",
    },
    gcp_info: {
      title: "Dashboards actualizados",
      message:
        "Indicadores desde Plataforma de Analítica (GCP batch) (APP-22) hacia Dashboards Operativos (APP-23). El cliente sigue en Portal B2B (Trazabilidad) (APP-18).",
      tone: "info",
      scenario: "Lectura CQRS",
    },
    upstream_down: {
      title: "Servicio no disponible",
      message:
        extra.upstreamMessage ||
        "No hay conexión con el backend en la nube. Revisa red/VPN o que el despliegue MVP esté activo.",
      tone: "error",
    },
  };
  const base = map[type] || {
    title: "Resultado",
    message: data?.error || "Operación finalizada.",
    tone: httpStatus >= 400 ? "error" : "info",
    scenario: "?",
  };
  return {
    ...base,
    orderId,
    httpStatus,
    cloud: extra.cloud,
    steps: extra.steps,
    deadLetterPreview: extra.deadLetterPreview,
    portalHint: extra.portalHint,
    trackingStatus: extra.trackingStatus,
    trackingSteps: extra.trackingSteps,
  };
}

const TRACKING_LABELS = {
  CONFIRMED: "Confirmado — preparando despacho",
  IN_TRANSIT: "En tránsito hacia el cliente",
  AT_DESTINATION_POD: "En destino — evidencia capturada",
  POD_REJECTED: "Evidencia rechazada",
  DELIVERED: "Entregado",
  CANCELLED_NO_STOCK: "Cancelado — sin unidades en almacén",
  CANCELLED_WMS: "Cancelado — almacén no disponible",
  NOT_FOUND: "Orden no encontrada",
  DEMO_SAMPLE: "En tránsito (orden de ejemplo)",
};

function resolveTracking(orderId) {
  const last = session.lastOrder;
  const delivery = findDeliveryByOrderId(orderId);
  const j = delivery?.journey || { deliveryCompleted: false, evidenceValid: null, accepted: false };

  if (!last?.orderId || orderId !== last.orderId) {
    if (orderId === "ORD-123") {
      return {
        status: "DEMO_SAMPLE",
        message: "Orden de ejemplo del mock APIM. Crea un pedido en el portal para ver tu flujo real.",
        steps: ["Pedido de demo", "En tránsito"],
      };
    }
    return {
      status: "NOT_FOUND",
      message: "No encontramos esa orden en esta sesión. Usa el número de tu último pedido confirmado.",
      steps: ["Orden no localizada"],
    };
  }

  if (last.scenario === "E3") {
    return {
      status: "CANCELLED_NO_STOCK",
      message: "El pedido no se confirmó: no hay unidades disponibles en almacén para despachar.",
      steps: ["Pedido recibido", "Reserva rechazada", "Cancelado"],
    };
  }
  if (last.scenario === "E4") {
    return {
      status: "CANCELLED_WMS",
      message: "El almacén no confirmó. La Saga liberó la reserva; el envío no siguió.",
      steps: ["Reserva en almacén", "WMS falló", "Compensado — cancelado"],
    };
  }
  if (j.deliveryCompleted && j.evidenceValid === true) {
    return {
      status: "DELIVERED",
      message: "Entrega cerrada con foto POD validada (hash SHA-256 correcto).",
      steps: ["Despachado", "En tránsito", "Foto POD OK", "Entregado"],
    };
  }
  if (j.evidenceValid === true && !j.deliveryCompleted) {
    return {
      status: "AT_DESTINATION_POD",
      message: "El conductor capturó evidencia válida. Falta confirmar cierre de entrega en app.",
      steps: ["Despachado", "En tránsito", "En destino", "Evidencia capturada"],
    };
  }
  if (j.accepted && j.evidenceValid === null && !j.deliveryCompleted) {
    return {
      status: "AT_DESTINATION_POD",
      message: "Conductor en destino atendiendo la parada. Pendiente foto POD.",
      steps: ["Despachado", "En tránsito", "En destino"],
    };
  }
  if (j.evidenceValid === false) {
    return {
      status: "POD_REJECTED",
      message: "La foto no pasó validación de integridad. El conductor debe capturar de nuevo.",
      steps: ["Despachado", "En tránsito", "Evidencia rechazada"],
    };
  }
  if (last.scenario === "E1" || last.httpStatus === 201) {
    return {
      status: "IN_TRANSIT",
      message: "Tu pedido salió del almacén y va en camino. El conductor puede confirmar en la app móvil.",
      steps: ["Confirmado", "Reserva en almacén", "Despachado", "En tránsito"],
    };
  }
  return {
    status: "CONFIRMED",
    message: "Pedido registrado. Pronto iniciará preparación en almacén.",
    steps: ["Confirmado"],
  };
}

app.get("/api/health", (_req, res) => {
  res.json({
    ok: true,
    config: config.status(),
    lastOrder: session.lastOrder
      ? { orderId: session.lastOrder.orderId, status: session.lastOrder.status }
      : null,
  });
});

app.post("/api/portal/orders", async (req, res) => {
  if (!config.apimKey) {
    return res.status(503).json({ error: "Configura APIM_SUBSCRIPTION_KEY en .env" });
  }

  const customerId = req.body?.customerId || "B2B-CLIENTE";
  const sku = req.body?.sku || "SKU-001";
  const quantity = Number(req.body?.quantity || 1);
  const wmsFailure = Boolean(req.body?.wmsFailure);

  const idempotencyKey = guid();
  const body = { customerId, items: [{ sku, quantity }] };
  const headers = apimHeaders({ "Idempotency-Key": idempotencyKey });
  if (wmsFailure) headers["X-Mock-Wms-Status"] = "503";

  const result = await proxyJson(`${config.apimBaseUrl}/api/v1/orders`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const { status, data, networkError } = result;

  if (networkError) {
    return res.status(503).json({
      ui: upstreamUi(result, "Azure APIM"),
      order: null,
    });
  }

  session.lastIdempotencyKey = idempotencyKey;
  let scenario = "E1";
  if (status === 409 && data?.error?.includes("E3")) scenario = "E3";
  else if (status === 503 || data?.error?.includes("E4")) scenario = "E4";
  else if (status !== 201) scenario = "OTHER";

  if (scenario === "E1") {
    assignOrderToRoute(data?.orderId, customerId);
  }

  session.lastOrder = {
    idempotencyKey,
    body,
    orderId: data?.orderId,
    status: data?.status,
    httpStatus: status,
    scenario,
  };

  let type = "order_created";
  if (status === 409 && data?.error?.includes("E2")) type = "order_duplicate";
  else if (status === 409 && data?.error?.includes("E3")) type = "order_no_stock";
  else if (status === 503 || data?.error?.includes("E4")) type = "order_wms_down";
  else if (status === 201) type = "order_created";

  res.status(status).json({
    ui: userMessage(type, status, data, { cloud: "Azure" }),
    order: session.lastOrder,
  });
});

app.post("/api/portal/orders/retry", async (_req, res) => {
  if (!session.lastIdempotencyKey || !session.lastOrder?.body) {
    return res.status(400).json({
      ui: {
        title: "Nada que reenviar",
        message: "Crea un pedido primero y luego usa «Reenviar mismo pedido».",
        tone: "warning",
      },
    });
  }

  const result = await proxyJson(`${config.apimBaseUrl}/api/v1/orders`, {
    method: "POST",
    headers: apimHeaders({ "Idempotency-Key": session.lastIdempotencyKey }),
    body: JSON.stringify(session.lastOrder.body),
  });
  if (result.networkError) {
    return res.status(503).json({
      ui: upstreamUi(result, "Azure APIM"),
      order: session.lastOrder,
    });
  }
  const { status, data } = result;

  res.status(status).json({
    ui: userMessage("order_duplicate", status, data, { cloud: "Azure" }),
    order: session.lastOrder,
  });
});

app.get("/api/portal/tracking/:orderId?", async (req, res) => {
  const orderId = req.params.orderId || session.lastOrder?.orderId || "ORD-123";
  const resolved = resolveTracking(orderId);

  // Llamada E8 a APIM (contrato mock); la UI usa estado de la sesión demo
  const apimTrack = await proxyJson(`${config.apimBaseUrl}/mock/portal/v1/tracking/${orderId}`, {
    headers: apimHeaders(),
  });
  const apimUnreachable = apimTrack.networkError;

  const label = TRACKING_LABELS[resolved.status] || resolved.status;
  res.json({
    ui: userMessage(
      "tracking",
      200,
      { orderId, status: resolved.status, label },
      {
        cloud: "Azure (+ sesión demo)",
        trackingMessage: resolved.message,
        trackingStatus: resolved.status,
        trackingSteps: resolved.steps,
      }
    ),
    tracking: {
      orderId,
      status: resolved.status,
      label,
      steps: resolved.steps,
      apimNote: apimUnreachable
        ? "APIM no alcanzable; tracking mostrado desde sesión demo local."
        : "APIM mock E8 siempre responde IN_TRANSIT; la demo enriquece según tu flujo.",
    },
  });
});

app.get("/api/mobile/deliveries", (_req, res) => {
  normalizeDeliveryIds();
  const inTransit = session.deliveries.filter((d) => formatDelivery(d).status === "IN_TRANSIT");
  res.json({
    activeDeliveryId: session.activeDeliveryId,
    deliveries: session.deliveries.map(formatDelivery),
    inTransitCount: inTransit.length,
  });
});

app.post("/api/mobile/deliveries/:id/accept", (req, res) => {
  const d = findDelivery(req.params.id);
  if (!d) {
    return res.status(404).json({ ui: { title: "No encontrada", message: "Entrega inexistente.", tone: "error" } });
  }
  if (!d.orderId) {
    return res.status(400).json({
      ui: {
        title: "Sin pedido",
        message: "Esta parada aún no tiene orden del portal B2B.",
        tone: "warning",
      },
    });
  }
  if (d.journey.deliveryCompleted) {
    return res.json({
      ui: { title: "Ya entregada", message: "Esta parada ya fue cerrada.", tone: "info" },
      delivery: formatDelivery(d),
    });
  }
  d.journey.accepted = true;
  session.activeDeliveryId = d.id;
  res.json({
    ui: {
      title: "Parada en atención",
      message: `Atiendes la entrega #${d.id} · ${d.customer}. Captura la foto y confirma.`,
      tone: "success",
      scenario: "E6",
      cloud: "AWS",
    },
    delivery: formatDelivery(d),
  });
});

app.get("/api/mobile/status", (req, res) => {
  const id = req.query.deliveryId || session.activeDeliveryId;
  const orderId = req.query.orderId || null;
  const d = orderId || id ? findDelivery(id, orderId) : getActiveDelivery();
  if (!d) {
    return res.json({ activeDeliveryId: null, delivery: null, deliveries: session.deliveries.map(formatDelivery) });
  }
  session.activeDeliveryId = d.id;
  const f = formatDelivery(d);
  res.json({
    activeDeliveryId: d.id,
    delivery: f,
    deliveries: session.deliveries.map(formatDelivery),
  });
});

function resolveActiveDelivery(req) {
  const id = req.body?.deliveryId || req.query?.deliveryId || session.activeDeliveryId;
  const orderId = req.body?.orderId || req.query?.orderId || null;
  const d = id || orderId ? findDelivery(id, orderId) : getActiveDelivery();
  if (d) session.activeDeliveryId = d.id;
  return d;
}

app.post("/api/mobile/complete", async (req, res) => {
  const d = resolveActiveDelivery(req);
  if (!d) {
    return res.status(400).json({
      ui: { title: "Elige una entrega", message: "Abre una parada de tu ruta primero.", tone: "warning" },
    });
  }
  if (!d.journey.accepted) {
    return res.status(400).json({
      ui: {
        title: "Abre la parada",
        message: "Selecciona la entrega en la lista antes de cerrarla.",
        tone: "warning",
        scenario: "E6",
      },
    });
  }
  if (d.journey.evidenceValid !== true) {
    return res.status(400).json({
      ui: {
        title: "Falta evidencia POD",
        message: "Primero toma la foto de entrega (validación hash). Luego confirma el cierre.",
        tone: "warning",
        scenario: "E6",
      },
    });
  }
  if (d.journey.deliveryCompleted) {
    return res.json({
      ui: {
        title: "Ya entregado",
        message: "Esta entrega ya fue confirmada.",
        tone: "info",
        scenario: "E6",
      },
      delivery: formatDelivery(d),
    });
  }

  const result = await proxyJson(`${config.awsAlbBaseUrl}/deliveries/${d.id}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  if (result.networkError) {
    return res.status(503).json({
      ui: upstreamUi(result, "AWS mobile-api"),
      delivery: formatDelivery(d),
    });
  }
  const { status, data } = result;
  if (status === 200) d.journey.deliveryCompleted = true;
  res.status(status).json({
    ui: userMessage("delivery_done", status, data, { cloud: "AWS" }),
    delivery: formatDelivery(d),
    api: data,
  });
});

app.post("/api/mobile/evidence", async (req, res) => {
  const d = resolveActiveDelivery(req);
  if (!d || !d.journey.accepted) {
    return res.status(400).json({
      ui: { title: "Elige la entrega", message: "Abre una parada de la lista primero.", tone: "warning" },
    });
  }
  if (d.journey.deliveryCompleted) {
    return res.status(400).json({
      ui: {
        title: "Entrega ya cerrada",
        message: "No puedes cambiar la evidencia después de confirmar la entrega.",
        tone: "warning",
        scenario: "E7",
      },
    });
  }

  const valid = req.body?.valid !== false;
  const sha = valid
    ? "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
    : "invalid";
  const result = await proxyJson(`${config.awsAlbBaseUrl}/deliveries/${d.id}/evidence`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sha256: sha }),
  });
  if (result.networkError) {
    return res.status(503).json({
      ui: upstreamUi(result, "AWS mobile-api"),
      delivery: formatDelivery(d),
    });
  }
  const { status, data } = result;
  const type = valid && status === 200 ? "evidence_ok" : "evidence_bad";
  d.journey.evidenceValid = valid && status === 200;
  res.status(status).json({
    ui: userMessage(type, status, data, { cloud: "AWS" }),
    delivery: formatDelivery(d),
  });
});

app.post("/api/ops/dlq", async (_req, res) => {
  const conn = config.getServiceBusConnectionString();
  if (!conn) {
    return res.status(503).json({
      ui: {
        title: "Bus no disponible",
        message: "Configura Service Bus o ejecuta az login.",
        tone: "error",
        scenario: "E5",
      },
    });
  }
  const orderId = session.lastOrder?.orderId || `ORD-E5-${Date.now().toString(36).toUpperCase()}`;
  try {
    const result = await runDlqDemo(conn, config.serviceBusQueue, orderId);
    res.json({
      ui: userMessage("dlq_ok", 200, null, {
        cloud: "Azure Service Bus",
        narrative: result.success
          ? `El aviso de inventario del pedido ${formatOrderIdForUi(orderId)} agotó reintentos y quedó en dead-letter para reproceso auditado.`
          : "La simulación ejecutó los reintentos pero no se confirmó el mensaje en dead-letter. Revisa la cola en Azure Portal o vuelve a intentar.",
        steps: result.steps,
        deadLetterPreview: result.deadLetterPreview,
        portalHint: result.portalHint,
      }),
      result,
    });
  } catch (err) {
    res.status(500).json({
      ui: { title: "Error", message: err.message, tone: "error", scenario: "E5" },
    });
  }
});

app.get("/api/ops/overview", (_req, res) => {
  const delivered = session.deliveries.filter((d) => formatDelivery(d).status === "DELIVERED").length;
  const inTransit = session.deliveries.filter((d) => formatDelivery(d).status === "IN_TRANSIT").length;
  res.json({
    serviceBusOk: Boolean(config.getServiceBusConnectionString()),
    lastOrderId: session.lastOrder?.orderId || null,
    deliveriesTotal: session.deliveries.length,
    deliveriesInTransit: inTransit,
    deliveriesDone: delivered,
  });
});

app.get("/api/analytics/summary", (_req, res) => {
  const delivered = session.deliveries.filter((d) => formatDelivery(d).status === "DELIVERED").length;
  const inTransit = session.deliveries.filter((d) => {
    const s = formatDelivery(d).status;
    return s === "IN_TRANSIT" || s === "AT_DESTINATION" || s === "POD_OK";
  }).length;
  const ordersToday = session.lastOrder?.httpStatus === 201 ? 1 : 0;
  res.json({
    ui: userMessage("gcp_info", 200, null, { cloud: "GCP" }),
    metrics: {
      ordersToday: ordersToday + delivered,
      inTransit,
      dataset: "rutaexpress_mvp_tracking",
      projector: "Cloud Run (fase 3)",
      table: "tracking_projection",
    },
  });
});

const port = Number(process.env.PORT) || config.port;
const tlsPort = Number(process.env.TLS_PORT) || 3443;
const tlsKey = path.join(__dirname, "tls.key");
const tlsCrt = path.join(__dirname, "tls.crt");

function logReady(proto, listenPort) {
  const s = config.status();
  const host = process.env.PUBLIC_HOST || process.env.WEBSITE_HOSTNAME || `localhost:${listenPort}`;
  console.log(`RutaExpress demo → ${proto}://${host}`);
  console.log(`  APIM: ${s.apim ? "OK" : "falta key"} | AWS: ${s.aws ? "OK" : "—"} | Bus: ${s.serviceBus ? "OK" : "falta"}`);
}

const server = app.listen(port, "0.0.0.0", () => logReady("http", port));

if (fs.existsSync(tlsKey) && fs.existsSync(tlsCrt)) {
  https
    .createServer(
      { key: fs.readFileSync(tlsKey), cert: fs.readFileSync(tlsCrt) },
      app
    )
    .listen(tlsPort, "0.0.0.0", () => logReady("https", tlsPort));
}

server.on("error", (err) => {
  if (err.code === "EADDRINUSE") {
    console.error(`Puerto ${port} en uso. taskkill /PID <pid> /F  o cambia PORT`);
    process.exit(1);
  }
  throw err;
});

process.on("unhandledRejection", (err) => {
  console.error("[demo] unhandledRejection:", err);
});
