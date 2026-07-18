const { ServiceBusClient } = require("@azure/service-bus");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function drainActiveQueue(receiver, steps, maxMessages = 30) {
  let drained = 0;
  for (let i = 0; i < maxMessages; i++) {
    const batch = await receiver.receiveMessages(5, { maxWaitTimeInMs: 1500 });
    if (!batch.length) break;
    drained += batch.length;
  }
  if (drained > 0) {
    steps.push({
      label: `Cola preparada — ${drained} mensaje(s) anterior(es) retirado(s) para la demo`,
      ok: true,
    });
  }
}

async function peekOurDeadLetter(dlqReceiver, orderId) {
  const peeked = await dlqReceiver.peekMessages(20, { maxWaitTimeInMs: 8000 });
  const ours = peeked.find((m) => {
    const b = typeof m.body === "object" ? m.body : {};
    return b.order_id === orderId;
  });
  if (!ours) return { deadLetterCount: peeked.length, deadLetterPreview: null };
  return {
    deadLetterCount: peeked.length,
    deadLetterPreview: {
      orderId: ours.body?.order_id || orderId,
      deliveryCount: ours.deliveryCount,
      enqueued: ours.enqueuedTimeUtc?.toISOString?.() || null,
    },
  };
}

async function runDlqDemo(connectionString, queueName, orderId) {
  const steps = [];
  const client = new ServiceBusClient(connectionString);
  const maxDeliveryAttempts = 12;

  try {
    const drainRx = client.createReceiver(queueName, { receiveMode: "receiveAndDelete" });
    await drainActiveQueue(drainRx, steps);
    await drainRx.close();

    const sender = client.createSender(queueName);
    await sender.sendMessages({
      body: {
        event_type: "OrderCreated",
        order_id: orderId,
        scenario: "E5",
      },
      contentType: "application/json",
    });
    await sender.close();
    steps.push({ label: "Evento publicado en cola q-inventory", ok: true });

    const receiver = client.createReceiver(queueName, { receiveMode: "peekLock" });
    let ourAbandons = 0;
    let pickAttempts = 0;

    while (ourAbandons < maxDeliveryAttempts && pickAttempts < 50) {
      pickAttempts++;
      const messages = await receiver.receiveMessages(1, { maxWaitTimeInMs: 15000 });
      if (!messages.length) {
        if (ourAbandons > 0) break;
        steps.push({ label: "Cola vacía tras publicar — no se pudo continuar", ok: false });
        break;
      }

      const msg = messages[0];
      const body = typeof msg.body === "object" ? msg.body : {};
      if (body.order_id !== orderId) {
        await receiver.abandonMessage(msg);
        continue;
      }

      ourAbandons++;
      steps.push({
        label: `Consumidor falla — reintento ${ourAbandons} (entrega nº ${msg.deliveryCount + 1})`,
        ok: true,
      });
      await receiver.abandonMessage(msg);
    }
    await receiver.close();

    const dlqReceiver = client.createReceiver(queueName, { subQueue: "deadLetter" });
    let deadLetterCount = 0;
    let deadLetterPreview = null;

    for (let poll = 0; poll < 6; poll++) {
      const peek = await peekOurDeadLetter(dlqReceiver, orderId);
      deadLetterCount = peek.deadLetterCount;
      deadLetterPreview = peek.deadLetterPreview;
      if (deadLetterPreview) break;
      if (poll < 5) await sleep(2000);
    }
    await dlqReceiver.close();

    const success = Boolean(deadLetterPreview);
    if (success) {
      steps.push({
        label: "Mensaje en dead-letter queue — listo para revisión y reproceso operativo",
        ok: true,
      });
    } else {
      steps.push({
        label:
          "No se confirmó en DLQ en esta ejecución. Revisa en Azure Portal: q-inventory → $deadletterqueue.",
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
