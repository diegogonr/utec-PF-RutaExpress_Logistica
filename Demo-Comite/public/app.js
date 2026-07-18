const state = { lastOrderId: null, busy: false, deliveryOpenSeq: 0, activeDeliveryId: null, activeOrderId: null };

const SKU_CATALOG = {
  "SKU-001": {
    label: "Caja retail estándar",
    cd: "CD Lima Sur",
    stock: 100,
    note: "Mercadería del cliente depositada en CD — disponible para despacho.",
  },
  "SKU-002": {
    label: "Kit promocional temporada",
    cd: "CD Lima Norte",
    stock: 0,
    note: "Sin unidades libres en almacén (demo rechazo E3).",
  },
  "SKU-003": {
    label: "Insumo farmacia (cadena frío)",
    cd: "CD Callao",
    stock: 0,
    note: "Sin posición libre en almacén frío.",
  },
  "SKU-004": {
    label: "Electro mediano (marketplace)",
    cd: "CD Arequipa",
    stock: 0,
    note: "Unidades ya comprometidas en otro pedido del mismo cliente.",
  },
  "SKU-005": {
    label: "Bebida pack ×24",
    cd: "CD Lima Sur",
    stock: 0,
    note: "Reposición del cliente en tránsito — aún no despachable.",
  },
};

function skuLabel(sku) {
  const item = SKU_CATALOG[sku];
  return item ? `${sku} — ${item.label}` : sku;
}

function formatOrderId(orderId) {
  if (!orderId) return "—";
  if (orderId.length <= 16) return orderId;
  return `${orderId.slice(0, 8)}…${orderId.slice(-6)}`;
}

function updateSkuHint() {
  const sku = document.getElementById("sku").value;
  const item = SKU_CATALOG[sku];
  const el = document.getElementById("skuHint");
  if (!item || !el) return;
  const tone = item.stock > 0 ? "ok" : "warn";
  el.className = `field-hint ${tone}`;
  el.textContent = `${item.cd} · ${item.stock > 0 ? `${item.stock} uds. disponibles` : "Sin stock disponible"}. ${item.note}`;
}

const views = document.querySelectorAll(".view");
const roleNav = document.getElementById("roleNav");

function showView(name) {
  document.body.dataset.app = name;
  views.forEach((v) => v.classList.toggle("active", v.id === `view-${name}`));
  roleNav.querySelectorAll("button").forEach((b) => {
    b.classList.toggle("active", b.dataset.view === name);
  });
}

roleNav.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-view]");
  if (btn) {
    showView(btn.dataset.view);
    if (btn.dataset.view === "mobile") refreshMobileStatus();
    if (btn.dataset.view === "ops") refreshOpsOverview();
    if (btn.dataset.view === "gcp") refreshGcpMetrics();
    if (btn.dataset.view === "inventory") refreshInventory();
  }
});

function formatInvTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return "";
  }
}

function renderInventory(data) {
  const inv = data.inventory;
  if (!inv) return;
  document.getElementById("invWithStock").textContent = inv.totals.withStock;
  document.getElementById("invUnits").textContent = inv.totals.units;
  document.getElementById("invReserved").textContent = inv.totals.reservedOpen;
  const src = document.getElementById("invSource");
  if (src) src.textContent = inv.source;

  const body = document.getElementById("invTableBody");
  const maxSeed = Math.max(...inv.items.map((i) => i.seed || 1), 1);
  body.innerHTML = inv.items
    .map((item) => {
      const pct = Math.min(100, Math.round((item.available / maxSeed) * 100));
      const stateLabel = item.available > 0 ? "Disponible" : "Sin stock";
      const rowClass = item.available > 0 ? "" : "empty-row";
      return `<tr class="${rowClass}">
        <td class="sku">${item.sku}</td>
        <td>${item.label}</td>
        <td>${item.cd}</td>
        <td>
          <div class="qty">${item.available}</div>
          <div class="stock-bar" aria-hidden="true"><i style="width:${pct}%"></i></div>
        </td>
        <td><span class="status-pill ${item.available > 0 ? "ok" : "warn"}">${stateLabel}</span></td>
      </tr>`;
    })
    .join("");

  const mov = document.getElementById("invMovements");
  if (!inv.movements.length) {
    mov.innerHTML = '<li class="empty">Aún no hay movimientos. Confirma un pedido en Portal B2B.</li>';
  } else {
    mov.innerHTML = inv.movements
      .map((m) => {
        const oid = m.orderId ? formatOrderId(m.orderId) : "—";
        return `<li class="${m.tone || "info"}">
          <div class="mv-top">
            <span class="mv-label">${m.label}</span>
            <span class="mv-time">${formatInvTime(m.at)}</span>
          </div>
          <div class="mv-meta">${oid}</div>
        </li>`;
      })
      .join("");
  }

  // Sync portal SKU hints with live session stock
  inv.items.forEach((item) => {
    if (SKU_CATALOG[item.sku]) SKU_CATALOG[item.sku].stock = item.available;
  });
  updateSkuHint();
}

async function refreshInventory() {
  try {
    const data = await api("GET", "/api/inventory/overview");
    renderInventory(data);
  } catch {
    /* ignore */
  }
}

async function refreshOpsOverview() {
  try {
    const data = await api("GET", "/api/ops/overview");
    const sb = document.getElementById("opsSbStatus");
    if (sb) {
      sb.textContent = data.serviceBusOk ? "Conectado" : "Revisar";
      sb.className = `status-pill ${data.serviceBusOk ? "ok" : "warn"}`;
    }
    const chip = document.getElementById("opsLiveChip");
    if (chip) {
      chip.textContent = data.serviceBusOk ? "Bus conectado" : "Bus con alerta";
      chip.className = `chip ${data.serviceBusOk ? "chip-ok" : ""}`;
    }
    const last = document.getElementById("opsLastOrder");
    if (last) {
      last.textContent = data.lastOrderId ? formatOrderId(data.lastOrderId) : "Ninguno aún";
      last.title = data.lastOrderId || "";
    }
    const del = document.getElementById("opsDeliveries");
    if (del) {
      const total = (data.deliveriesDone || 0) + (data.deliveriesInTransit || 0);
      if (!total) del.textContent = "Ninguna asignada";
      else del.textContent = `${data.deliveriesInTransit} en ruta · ${data.deliveriesDone} entregadas`;
    }
  } catch {
    /* ignore */
  }
}

async function refreshGcpMetrics() {
  try {
    const data = await api("GET", "/api/analytics/summary");
    renderAnalytics(data);
  } catch {
    /* ignore */
  }
}

function renderAnalytics(data) {
  const m = data.metrics || {};
  const grid = document.getElementById("gcpMetrics");
  if (grid) {
    grid.querySelector('[data-metric="ordersConfirmed"]').textContent = m.ordersConfirmed ?? 0;
    grid.querySelector('[data-metric="inTransit"]').textContent = m.inTransit ?? 0;
    grid.querySelector('[data-metric="delivered"]').textContent = m.delivered ?? 0;
  }

  renderAnalyticsChart(data.chart || []);

  const feed = document.getElementById("gcpActivity");
  if (feed) {
    const rows = data.activity || [];
    if (!rows.length) {
      feed.innerHTML = '<li class="empty">Sin actividad aún. Confirma un pedido en Portal B2B.</li>';
    } else {
      feed.innerHTML = rows
        .map((a) => {
          const time = formatInvTime(a.at);
          return `<li class="${a.kind || ""}">
            <div class="mv-top">
              <span class="mv-label">${a.title}</span>
              <span class="mv-time">${time}</span>
            </div>
            <div class="mv-meta">${a.detail || ""}</div>
          </li>`;
        })
        .join("");
    }
  }

  const br = document.getElementById("gcpBreakdown");
  if (br && data.breakdown) {
    br.innerHTML = data.breakdown
      .map((row) => `<li><span>${row.label}</span><em class="ok">${row.value}</em></li>`)
      .join("");
  }
}

function renderAnalyticsChart(series) {
  const host = document.getElementById("gcpChart");
  if (!host) return;
  if (!series.length) {
    host.innerHTML = '<p class="chart-empty">Sin datos para graficar.</p>';
    return;
  }

  const max = Math.max(...series.map((s) => Number(s.value) || 0), 1);
  const w = 640;
  const h = 220;
  const padL = 36;
  const padR = 16;
  const padT = 18;
  const padB = 48;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;
  const gap = 12;
  const barW = (plotW - gap * (series.length - 1)) / series.length;

  const bars = series
    .map((s, i) => {
      const val = Number(s.value) || 0;
      const bh = Math.max(val > 0 ? 8 : 0, (val / max) * plotH);
      const x = padL + i * (barW + gap);
      const y = padT + plotH - bh;
      const label = s.label.length > 11 ? `${s.label.slice(0, 10)}…` : s.label;
      return `
        <g class="chart-bar">
          <rect x="${x}" y="${y}" width="${barW}" height="${bh}" rx="8" fill="${s.color || "#059669"}">
            <title>${s.label}: ${val}</title>
          </rect>
          <text x="${x + barW / 2}" y="${y - 6}" text-anchor="middle" class="chart-val">${val}</text>
          <text x="${x + barW / 2}" y="${h - 16}" text-anchor="middle" class="chart-lbl">${label}</text>
        </g>`;
    })
    .join("");

  host.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" class="ops-chart" role="presentation">
      <line x1="${padL}" y1="${padT + plotH}" x2="${w - padR}" y2="${padT + plotH}" class="chart-axis" />
      ${bars}
    </svg>`;
}

function toast(el, ui) {
  if (!ui) return;
  el.className = `toast show ${ui.tone || "info"}`;
  el.innerHTML = `<strong>${ui.title}</strong>${ui.message || ""}`;
}

function setBusy(on) {
  state.busy = on;
  document.querySelectorAll(".btn").forEach((b) => {
    b.disabled = on;
  });
}

async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  return res.json();
}

function updateOrderSummary(order, ui) {
  const box = document.getElementById("orderSummary");
  const tl = document.getElementById("portalTimeline");
  if (!order?.orderId) {
    box.innerHTML = '<p class="empty">Todavía no hay pedidos en esta sesión.</p>';
    return;
  }
  state.lastOrderId = order.orderId;
  const ok = order.httpStatus === 201;
  const line = order.body?.items?.[0];
  const skuText = line ? skuLabel(line.sku) : "";
  const qtyText = line ? ` · ${line.quantity} uds.` : "";
  box.innerHTML = `
    <div>
      <div class="label">Número de orden</div>
      <div class="oid">${order.orderId}</div>
      ${skuText ? `<div class="order-line">${skuText}${qtyText}</div>` : ""}
      <span class="status-pill ${ok ? "ok" : "warn"}">${ok ? "Confirmado" : ui?.title || "Procesado"}</span>
    </div>
  `;
  const steps = [];
  if (ok) {
    steps.push("Pedido recibido", "Stock reservado", "Listo para despacho", "Asignado a ruta", "En tránsito");
  } else if (ui?.scenario === "E3") {
    steps.push("Pedido recibido", "Sin stock — detenido");
  } else if (ui?.scenario === "E4") {
    steps.push("Reserva iniciada", "Almacén no disponible", "Reserva liberada");
  } else if (ui?.scenario === "E2") {
    steps.push("Reenvío detectado", "Misma orden devuelta");
  }
  tl.innerHTML = steps.map((s) => `<li class="done">${s}</li>`).join("");
}

document.getElementById("sku").addEventListener("change", updateSkuHint);
updateSkuHint();

// Portal — nuevo pedido
document.getElementById("orderForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (state.busy) return;
  setBusy(true);
  const quantity = Number(document.getElementById("quantity").value);
  const customerId = document.getElementById("customerId").value.trim() || "B2B-CLIENTE";
  const sku = document.getElementById("sku").value;
  const wmsFailure = document.getElementById("wmsFailure").checked;

  // E3: cantidad altísima
  const qty = quantity >= 9999 ? quantity : quantity;

  try {
    const data = await api("POST", "/api/portal/orders", {
      customerId,
      sku,
      quantity: qty,
      wmsFailure,
    });
    toast(document.getElementById("portalToast"), data.ui);
    updateOrderSummary(data.order, data.ui);
    refreshOpsOverview();
    refreshInventory();
    refreshGcpMetrics();
    if (data.order?.httpStatus === 201) refreshMobileStatus();
  } catch {
    toast(document.getElementById("portalToast"), {
      title: "Sin conexión",
      message: "¿Está corriendo npm start?",
      tone: "error",
    });
  } finally {
    setBusy(false);
  }
});

document.getElementById("btnRetry").addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    const data = await api("POST", "/api/portal/orders/retry");
    toast(document.getElementById("portalToast"), data.ui);
  } finally {
    setBusy(false);
  }
});

document.getElementById("btnTrack").addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    const id = state.lastOrderId || "ORD-123";
    const data = await api("GET", `/api/portal/tracking/${id}`);
    toast(document.getElementById("portalToast"), data.ui);
    if (data.tracking?.steps?.length) {
      const tl = document.getElementById("portalTimeline");
      tl.innerHTML = data.tracking.steps
        .map((s) => `<li class="done">${s}</li>`)
        .join("");
      const box = document.getElementById("orderSummary");
      if (data.tracking.label) {
        const pill = box.querySelector(".status-pill");
        if (pill) pill.textContent = data.tracking.label.slice(0, 28);
      }
    }
  } finally {
    setBusy(false);
  }
});

// Hint E3
document.getElementById("quantity").addEventListener("change", (e) => {
  if (Number(e.target.value) >= 9999) {
    toast(document.getElementById("portalToast"), {
      title: "Cantidad de prueba",
      message: "Con 9999+ unidades simularás escenario sin stock (E3).",
      tone: "info",
      scenario: "E3",
    });
  }
});

// Mobile — lista de entregas y cierre en campo
const STATUS_LABEL = {
  IN_TRANSIT: { text: "En tránsito", cls: "transit" },
  AT_DESTINATION: { text: "En destino", cls: "dest" },
  POD_OK: { text: "POD OK", cls: "pod" },
  DELIVERED: { text: "Entregado", cls: "done" },
};

function showMobileList() {
  document.getElementById("mobileList").classList.remove("hidden");
  document.getElementById("mobileDetail").classList.add("hidden");
}

function showMobileDetail() {
  document.getElementById("mobileList").classList.add("hidden");
  document.getElementById("mobileDetail").classList.remove("hidden");
}

function renderDeliveryList(deliveries) {
  const list = document.getElementById("deliveryList");
  const sub = document.getElementById("mobileListSub");
  const visible = deliveries.filter((d) => Boolean(d.orderId));
  const inTransit = visible.filter((d) => d.status === "IN_TRANSIT" && d.orderId);
  sub.textContent =
    inTransit.length > 0
      ? `${inTransit.length} parada(s) en tránsito — toca para atender`
      : visible.length > 0
        ? "Sin paradas pendientes en tránsito"
      : "Confirma un pedido en Portal B2B para ver paradas";

  if (!visible.length) {
    list.innerHTML = '<p class="mobile-empty">Aún no hay entregas asignadas a tu ruta.</p>';
    return;
  }

  list.innerHTML = visible
    .map((d) => {
      const st = STATUS_LABEL[d.status] || { text: d.status, cls: "empty" };
      const action =
        d.status === "IN_TRANSIT" && d.orderId
          ? "Atender →"
          : d.status === "DELIVERED"
            ? "Ver"
            : "Continuar →";
      const orderLine = `Pedido ${formatOrderId(d.orderId)}`;
      return `<button type="button" class="delivery-item" data-delivery-id="${d.id}" data-order-id="${d.orderId}">
        <div class="row">
          <span class="id">Parada #${d.id}</span>
          <span class="status-chip ${st.cls}">${st.text}</span>
        </div>
        <div class="cust">${d.customer}</div>
        <div class="addr-sm">${d.address}</div>
        <div class="addr-sm order-ref">${orderLine} · ${action}</div>
      </button>`;
    })
    .join("");

  list.querySelectorAll(".delivery-item").forEach((btn) => {
    btn.addEventListener("click", () => openDelivery(btn.dataset.deliveryId, btn.dataset.orderId));
  });
}

function syncMobileDetail(d) {
  if (!d) return;
  document.getElementById("mobileDeliveryId").textContent = `#${d.id}`;
  document.getElementById("mobileCustomer").textContent = d.customer;
  document.getElementById("mobileAddress").textContent = d.address;
  const orderEl = document.getElementById("mobileOrderRef");
  if (d.orderId) {
    orderEl.textContent = d.orderId;
    orderEl.title = d.orderId;
  } else {
    orderEl.textContent = "—";
    orderEl.removeAttribute("title");
  }
  if (d.orderId) state.lastOrderId = d.orderId;
  state.activeOrderId = d.orderId || null;

  const btnPhotoOk = document.getElementById("btnPhotoOk");
  const btnPhotoBad = document.getElementById("btnPhotoBad");
  const btnComplete = document.getElementById("btnComplete");
  const photoAdv = document.getElementById("photoAdv");
  const hint = document.getElementById("mobileHint");

  [btnPhotoOk, btnComplete, photoAdv].forEach((b) => b && b.classList.add("hidden"));

  const j = d.journey;
  if (d.status === "DELIVERED") {
    mobileStep(4);
    hint.textContent = "Entrega cerrada. El cliente ya puede ver el seguimiento.";
    return;
  }
  if (!d.orderId) {
    mobileStep(1);
    hint.textContent = "Esta parada aún no tiene pedido asociado.";
    return;
  }
  if (j.evidenceValid === true) {
    mobileStep(3);
    btnComplete.classList.remove("hidden");
    btnComplete.disabled = false;
    hint.textContent = "Evidencia lista. Confirma la entrega.";
    return;
  }
  if (j.evidenceValid === false) {
    mobileStep(2);
    btnPhotoOk.classList.remove("hidden");
    photoAdv.classList.remove("hidden");
    hint.textContent = "La foto no fue aceptada. Vuelve a capturarla.";
    return;
  }
  mobileStep(2);
  btnPhotoOk.classList.remove("hidden");
  photoAdv.classList.remove("hidden");
  hint.textContent = "Captura la foto de entrega y confirma.";
}

function mobileStep(n) {
  [1, 2, 3].forEach((i) => {
    const el = document.getElementById(`step${i}`);
    if (!el) return;
    el.classList.remove("active", "done");
    if (i < n) el.classList.add("done");
    if (i === n) el.classList.add("active");
  });
}

async function refreshMobileList() {
  const data = await api("GET", "/api/mobile/deliveries");
  renderDeliveryList(data.deliveries || []);
  return data;
}

async function openDelivery(id, orderId) {
  const deliveryId = String(id);
  const openSeq = ++state.deliveryOpenSeq;
  state.activeDeliveryId = deliveryId;
  state.activeOrderId = orderId || null;
  showMobileDetail();
  document.getElementById("mobileDeliveryId").textContent = `#${deliveryId}`;
  document.getElementById("mobileCustomer").textContent = "…";
  document.getElementById("mobileAddress").textContent = "…";
  document.getElementById("mobileOrderRef").textContent = orderId || "Cargando…";

  try {
    const qs = new URLSearchParams({ deliveryId });
    if (orderId) qs.set("orderId", orderId);
    let data = await api("GET", `/api/mobile/status?${qs}`);
    if (openSeq !== state.deliveryOpenSeq) return;

    if (!data.delivery) {
      toast(document.getElementById("mobileToast"), {
        title: "Parada no encontrada",
        message: `No existe la entrega #${deliveryId} en esta sesión.`,
        tone: "error",
      });
      showMobileList();
      return;
    }

    if (
      data.delivery.status === "IN_TRANSIT" &&
      data.delivery.orderId &&
      !data.delivery.journey?.accepted
    ) {
      data = await api("POST", `/api/mobile/deliveries/${encodeURIComponent(deliveryId)}/accept`);
      if (openSeq !== state.deliveryOpenSeq) return;
    }

    if (!data.delivery) {
      showMobileList();
      return;
    }

    state.activeDeliveryId = String(data.delivery.id);
    state.activeOrderId = data.delivery.orderId || null;
    syncMobileDetail(data.delivery);
  } catch {
    if (openSeq !== state.deliveryOpenSeq) return;
    toast(document.getElementById("mobileToast"), {
      title: "Error al abrir parada",
      message: "No se pudo cargar la entrega. Intenta de nuevo.",
      tone: "error",
    });
    showMobileList();
  }
}

document.getElementById("btnBackList").addEventListener("click", () => {
  showMobileList();
  refreshMobileList();
});

document.getElementById("btnComplete").addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    const data = await api("POST", "/api/mobile/complete", {
      deliveryId: state.activeDeliveryId,
      orderId: state.activeOrderId,
    });
    toast(document.getElementById("mobileToast"), data.ui);
    syncMobileDetail(data.delivery);
    refreshOpsOverview();
  } finally {
    setBusy(false);
  }
});

document.getElementById("btnPhotoOk").addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    const data = await api("POST", "/api/mobile/evidence", {
      valid: true,
      deliveryId: state.activeDeliveryId,
      orderId: state.activeOrderId,
    });
    toast(document.getElementById("mobileToast"), data.ui);
    syncMobileDetail(data.delivery);
  } finally {
    setBusy(false);
  }
});

document.getElementById("btnPhotoBad").addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    const data = await api("POST", "/api/mobile/evidence", {
      valid: false,
      deliveryId: state.activeDeliveryId,
      orderId: state.activeOrderId,
    });
    toast(document.getElementById("mobileToast"), data.ui);
    syncMobileDetail(data.delivery);
  } finally {
    setBusy(false);
  }
});

async function refreshMobileStatus() {
  try {
    showMobileList();
    await refreshMobileList();
  } catch {
    /* ignore */
  }
}

// Ops DLQ
document.getElementById("btnDlq").addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  const stepsEl = document.getElementById("opsSteps");
  stepsEl.innerHTML = "<li>Ejecutando simulación…</li>";
  try {
    const data = await api("POST", "/api/ops/dlq");
    toast(document.getElementById("opsToast"), data.ui);
    if (data.ui?.steps) {
      stepsEl.innerHTML = data.ui.steps
        .map((s) => `<li class="${s.ok ? "ok" : ""}">${s.label}</li>`)
        .join("");
    }
    if (data.ui?.deadLetterPreview) {
      stepsEl.innerHTML += `<li class="ok">DLQ: mensaje ${data.ui.deadLetterPreview.orderId} listo para replay</li>`;
    }
  } finally {
    setBusy(false);
  }
});

// GCP
document.getElementById("btnGcpRefresh").addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    const data = await api("GET", "/api/analytics/summary");
    toast(document.getElementById("gcpToast"), data.ui);
    renderAnalytics(data);
  } finally {
    setBusy(false);
  }
});

// Init
fetch("/api/health")
  .then((r) => r.json())
  .then((h) => {
    if (h.lastOrder?.orderId) {
      state.lastOrderId = h.lastOrder.orderId;
      updateOrderSummary({ orderId: h.lastOrder.orderId, httpStatus: 201 }, null);
      refreshOpsOverview();
    }
  })
  .catch(() => {});

refreshMobileStatus();
refreshInventory();
document.body.dataset.app = "portal";

document.getElementById("btnInvRefresh")?.addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    await refreshInventory();
  } finally {
    setBusy(false);
  }
});

document.getElementById("btnInvReset")?.addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true);
  try {
    const data = await api("POST", "/api/inventory/reset");
    toast(document.getElementById("invToast"), data.ui);
    renderInventory(data);
  } finally {
    setBusy(false);
  }
});
