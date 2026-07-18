const { ServiceBusClient } = require("@azure/service-bus");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** En este namespace, subQueue:'deadLetter' no entrega mensajes; la ruta explícita sí. */
function deadLetterPath(queueName) {
  return `${queueName}/$deadletterqueue`;
}

function getBody(msg) {
  let b = msg?.body;
  if (Buffer.isBuffer(b)) {
    try {
      b = JSON.parse(b.toString("utf8"));
    } catch {
      b = {};
    }
  } else if (typeof b === "string") {
    try {
      b = JSON.parse(b);
    } catch {
      b = {};
    }
  }
  return b && typeof b === "object" ? b : {};
}

function matchesOrder(msg, orderId) {
  if (!orderId) return false;
  if (msg.messageId === orderId || msg.correlationId === orderId) return true;
  const b = getBody(msg);
  return b.order_id === orderId;
}

async function drainQueue(receiver, maxBatches = 40) {
  let drained = 0;
  for (let i = 0; i < maxBatches; i++) {
    const batch = await receiver.receiveMessages(20, { maxWaitTimeInMs: 1200 });
    if (!batch.length) break;
    drained += batch.length;
  }
  return drained;
}

async function findInDeadLetter(client, queueName, orderId) {
  const path = deadLetterPath(queueName);

  // 1) Peek (no consume)
  const peekRx = client.createReceiver(path);
  try {
    const peeked = await peekRx.peekMessages(100);
    const ours = peeked.find((m) => matchesOrder(m, orderId));
    if (ours) {
      return {
        deadLetterCount: peeked.length,
        deadLetterPreview: {
          orderId: getBody(ours).order_id || orderId,
          deliveryCount: ours.deliveryCount,
          enqueued: ours.enqueuedTimeUtc?.toISOString?.() || null,
        },
      };
    }
  } finally {
    await peekRx.close();
  }

  // 2) Recibir peekLock y buscar (abandon para no borrar el mensaje del Portal)
  const rx = client.createReceiver(path, { receiveMode: "peekLock" });
  try {
    for (let i = 0; i < 10; i++) {
      const batch = await rx.receiveMessages(15, { maxWaitTimeInMs: 4000 });
      if (!batch.length) break;
      let found = null;
      for (const msg of batch) {
        if (!found && matchesOrder(msg, orderId)) {
          found = {
            orderId: getBody(msg).order_id || orderId,
            deliveryCount: msg.deliveryCount,
            enqueued: msg.enqueuedTimeUtc?.toISOString?.() || null,
          };
        }
        try {
          await rx.abandonMessage(msg);
        } catch {
          /* ignore */
        }
      }
      if (found) return { deadLetterCount: -1, deadLetterPreview: found };
    }
  } finally {
    await rx.close();
  }

  return { deadLetterCount: 0, deadLetterPreview: null };
}

/**
 * E5: publica en q-inventory, agota maxDeliveryCount con abandon → $deadletterqueue.
 * maxDeliveryCount de la cola MVP = 10.
 */
async function runDlqDemo(connectionString, queueName, orderId, options = {}) {
  const steps = [];
  const client = new ServiceBusClient(connectionString);
  const maxDeliveryCount = Number(options.maxDeliveryCount) || 10;
  const dlqPath = deadLetterPath(queueName);

  try {
    // 1) Limpiar cola activa
    const drainActive = client.createReceiver(queueName, { receiveMode: "receiveAndDelete" });
    const drainedActive = await drainQueue(drainActive);
    await drainActive.close();
    if (drainedActive > 0) {
      steps.push({
        label: `Cola activa limpia — ${drainedActive} mensaje(s) anterior(es)`,
        ok: true,
      });
    }

    // 2) Limpiar DLQ histórica (ruta explícita)
    const drainDlq = client.createReceiver(dlqPath, { receiveMode: "receiveAndDelete" });
    const drainedDlq = await drainQueue(drainDlq);
    await drainDlq.close();
    if (drainedDlq > 0) {
      steps.push({
        label: `DLQ preparada — ${drainedDlq} mensaje(s) histórico(s) retirado(s)`,
        ok: true,
      });
    }

    // 3) Publicar
    const sender = client.createSender(queueName);
    await sender.sendMessages({
      body: {
        event_type: "OrderCreated",
        order_id: orderId,
        scenario: "E5",
        at: new Date().toISOString(),
      },
      contentType: "application/json",
      messageId: orderId,
      correlationId: orderId,
      subject: "E5-DLQ-DEMO",
    });
    await sender.close();
    steps.push({ label: "Evento publicado en cola q-inventory", ok: true });

    // 4) Abandon hasta agotar reintentos
    const receiver = client.createReceiver(queueName, { receiveMode: "peekLock" });
    let ourAbandons = 0;
    let pickAttempts = 0;
    const maxPicks = maxDeliveryCount + 8;

    while (ourAbandons < maxDeliveryCount && pickAttempts < maxPicks) {
      pickAttempts++;
      const messages = await receiver.receiveMessages(1, { maxWaitTimeInMs: 20000 });
      if (!messages.length) {
        if (ourAbandons > 0) break;
        steps.push({ label: "Cola vacía tras publicar — no se pudo continuar", ok: false });
        break;
      }

      const msg = messages[0];
      if (!matchesOrder(msg, orderId)) {
        await receiver.completeMessage(msg);
        continue;
      }

      ourAbandons++;
      const deliveryNo = (msg.deliveryCount ?? 0) + 1;
      steps.push({
        label: `Consumidor falla — reintento ${ourAbandons}/${maxDeliveryCount} (entrega nº ${deliveryNo})`,
        ok: true,
      });
      await receiver.abandonMessage(msg);
      await sleep(120);
    }
    await receiver.close();

    // 5) Confirmar en DLQ
    let deadLetterPreview = null;
    let deadLetterCount = 0;
    for (let poll = 0; poll < 8; poll++) {
      const found = await findInDeadLetter(client, queueName, orderId);
      deadLetterCount = found.deadLetterCount;
      deadLetterPreview = found.deadLetterPreview;
      if (deadLetterPreview) break;
      await sleep(1200);
    }

    const success = Boolean(deadLetterPreview);
    if (success) {
      steps.push({
        label: "Mensaje en dead-letter — listo para revisar y reprocesar (Portal → Resubmit)",
        ok: true,
      });
    } else {
      steps.push({
        label:
          "No se confirmó en DLQ en esta ejecución. Revisa Azure Portal: q-inventory → $deadletterqueue.",
        ok: false,
      });
    }

    return {
      success,
      orderId,
      steps,
      deadLetterCount,
      deadLetterPreview,
      portalHint: "Azure Portal → q-inventory → $deadletterqueue → Peek → Resubmit",
    };
  } finally {
    await client.close();
  }
}

module.exports = { runDlqDemo };
