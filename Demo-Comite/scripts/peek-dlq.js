const { ServiceBusClient } = require("@azure/service-bus");

async function main() {
  const cs = process.env.SB_CONN;
  if (!cs) throw new Error("SB_CONN missing");
  const client = new ServiceBusClient(cs);

  console.log("=== subQueue deadLetter peekLock ===");
  const r1 = client.createReceiver("q-inventory", {
    subQueue: "deadLetter",
    receiveMode: "peekLock",
  });
  const a = await r1.receiveMessages(5, { maxWaitTimeInMs: 8000 });
  console.log("received", a.length);
  for (const m of a) {
    console.log({
      messageId: m.messageId,
      correlationId: m.correlationId,
      subject: m.subject,
      deliveryCount: m.deliveryCount,
      deadLetterReason: m.deadLetterReason,
      body: m.body,
    });
    await r1.abandonMessage(m);
  }
  await r1.close();

  console.log("=== explicit path ===");
  try {
    const r2 = client.createReceiver("q-inventory/$deadletterqueue", {
      receiveMode: "peekLock",
    });
    const b = await r2.receiveMessages(5, { maxWaitTimeInMs: 8000 });
    console.log("received", b.length);
    for (const m of b) {
      console.log({ messageId: m.messageId, body: m.body, deliveryCount: m.deliveryCount });
      await r2.abandonMessage(m);
    }
    await r2.close();
  } catch (e) {
    console.log("explicit path error:", e.message);
  }

  // Active queue sanity
  const r3 = client.createReceiver("q-inventory", { receiveMode: "peekLock" });
  const peeked = await r3.peekMessages(5);
  console.log("active peek", peeked.length);
  await r3.close();

  await client.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
