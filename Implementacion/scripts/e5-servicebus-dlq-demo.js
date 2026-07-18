const { ServiceBusClient } = require("@azure/service-bus");

const connectionString = process.env.SB_CONN || process.argv[2];
const queueName = process.env.SB_QUEUE || "q-inventory";
const orderId = process.env.ORDER_ID || "ORD-E5-PS";
const abandonCount = Number(process.env.ABANDON_COUNT || 10);

if (!connectionString) {
  console.error("Falta connection string (SB_CONN o argumento).");
  process.exit(1);
}

async function main() {
  const client = new ServiceBusClient(connectionString);
  const sender = client.createSender(queueName);

  const payload = {
    event_type: "OrderCreated",
    order_id: orderId,
    scenario: "E5",
  };

  await sender.sendMessages({ body: payload, contentType: "application/json" });
  console.log("[OK] Mensaje encolado en", queueName);
  await sender.close();

  const receiver = client.createReceiver(queueName, { receiveMode: "peekLock" });
  for (let i = 1; i <= abandonCount; i++) {
    const messages = await receiver.receiveMessages(1, { maxWaitTimeInMs: 15000 });
    if (!messages.length) {
      console.warn("Cola vacia en iteracion", i);
      break;
    }
    const msg = messages[0];
    console.log(`  Abandon ${i}/${abandonCount} deliveryCount=${msg.deliveryCount}`);
    await receiver.abandonMessage(msg);
  }

  await receiver.close();
  await client.close();
  console.log("");
  console.log("Listo. Portal: q-inventory -> $deadletterqueue -> Peek");
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
