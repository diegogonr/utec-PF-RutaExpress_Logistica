const sql = require("mssql");
const { EventHubProducerClient } = require("@azure/event-hubs");

const POLL_MS = Number(process.env.POLL_MS || 5000);

const sqlConfig = {
  server: process.env.SQL_SERVER,
  database: process.env.SQL_DATABASE || "db-orders",
  user: process.env.SQL_USER,
  password: process.env.SQL_PASSWORD,
  options: { encrypt: true, trustServerCertificate: false },
};

async function runOutboxPublisher() {
  const pool = await sql.connect(sqlConfig);
  const producer = new EventHubProducerClient(
    process.env.EVENTHUB_CONNECTION_STRING,
    process.env.EVENTHUB_NAME || "eh-canonical"
  );

  console.log("outbox-publisher started");
  setInterval(async () => {
    const rows = await pool.request().query(`
      SELECT TOP 10 id, payload FROM outbox WHERE status = 'PENDING' ORDER BY created_at
    `);
    for (const row of rows.recordset) {
      try {
        const batch = await producer.createBatch();
        batch.tryAdd({ body: row.payload });
        await producer.sendBatch(batch);
        await pool
          .request()
          .input("id", sql.UniqueIdentifier, row.id)
          .query("UPDATE outbox SET status = 'PUBLISHED' WHERE id = @id");
        console.log("published outbox", row.id);
      } catch (e) {
        console.error("publish error", e.message);
      }
    }
  }, POLL_MS);
}

runOutboxPublisher().catch((e) => {
  console.error(e);
  process.exit(1);
});
