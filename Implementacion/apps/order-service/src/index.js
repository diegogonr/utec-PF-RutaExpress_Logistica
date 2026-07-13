const express = require("express");
const crypto = require("crypto");
const Redis = require("ioredis");
const sql = require("mssql");

const PORT = process.env.PORT || 8080;
const INVENTORY_URL =
  process.env.INVENTORY_SERVICE_URL ||
  "http://inventory-service.rutaexpress.svc.cluster.local:8081";
const MOCK_WMS_URL =
  process.env.MOCK_WMS_URL || "http://127.0.0.1/mock/wms/v1/reservations/confirm";
const APIM_SUBSCRIPTION_KEY = process.env.APIM_SUBSCRIPTION_KEY || "";

const sqlConfig = {
  server: process.env.SQL_SERVER,
  database: process.env.SQL_DATABASE || "db-orders",
  user: process.env.SQL_USER,
  password: process.env.SQL_PASSWORD,
  options: {
    encrypt: true,
    trustServerCertificate: false,
  },
};

let pool;
const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: Number(process.env.REDIS_PORT || 6380),
  password: process.env.REDIS_PASSWORD || undefined,
  tls: process.env.REDIS_TLS === "true" ? {} : undefined,
});

async function initDb() {
  pool = await sql.connect(sqlConfig);
  await pool.request().query(`
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'orders')
    CREATE TABLE orders (
      id UNIQUEIDENTIFIER PRIMARY KEY,
      customer_id NVARCHAR(100) NOT NULL,
      payload_hash NVARCHAR(64) NOT NULL,
      status NVARCHAR(50) NOT NULL,
      created_at DATETIME2 DEFAULT SYSUTCDATETIME()
    );
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'outbox')
    CREATE TABLE outbox (
      id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
      aggregate_id UNIQUEIDENTIFIER NOT NULL,
      event_type NVARCHAR(100) NOT NULL,
      payload NVARCHAR(MAX) NOT NULL,
      status NVARCHAR(20) NOT NULL DEFAULT 'PENDING',
      created_at DATETIME2 DEFAULT SYSUTCDATETIME()
    );
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_orders_payload_hash')
    CREATE INDEX ix_orders_payload_hash ON orders(payload_hash);
  `);
}

function hashPayload(body) {
  return crypto.createHash("sha256").update(JSON.stringify(body)).digest("hex");
}

async function reserveInventory(orderId, items) {
  const res = await fetch(`${INVENTORY_URL}/v1/reservations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ orderId, items }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw Object.assign(new Error(err), { status: res.status });
  }
  return res.json();
}

async function releaseInventory(orderId) {
  await fetch(`${INVENTORY_URL}/v1/reservations/${orderId}`, { method: "DELETE" });
}

async function confirmWms(orderId, wmsMode) {
  const headers = { "Content-Type": "application/json" };
  if (APIM_SUBSCRIPTION_KEY) {
    headers["Ocp-Apim-Subscription-Key"] = APIM_SUBSCRIPTION_KEY;
  }
  if (wmsMode === "503") headers["X-Mock-Wms-Status"] = "503";
  const res = await fetch(MOCK_WMS_URL, {
    method: "POST",
    headers,
    body: JSON.stringify({ orderId }),
  });
  return res.status;
}

function wmsFailed(status) {
  return status < 200 || status >= 300;
}

const app = express();
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok", app: "APP-02" }));

app.post("/v1/orders", async (req, res) => {
  const idempotencyKey = req.headers["idempotency-key"];
  if (!idempotencyKey) {
    return res.status(400).json({ error: "Idempotency-Key requerido (E1)" });
  }

  const cached = await redis.get(`idem:${idempotencyKey}`);
  if (cached) {
    return res.status(200).json(JSON.parse(cached));
  }

  const body = req.body || {};
  const payloadHash = hashPayload(body);
  const dup = await pool
    .request()
    .input("hash", sql.NVarChar, payloadHash)
    .query("SELECT TOP 1 id, status FROM orders WHERE payload_hash = @hash");
  if (dup.recordset.length > 0) {
    return res.status(409).json({
      error: "Orden duplicada (E2)",
      orderId: dup.recordset[0].id,
      status: dup.recordset[0].status,
    });
  }

  const orderId = crypto.randomUUID();
  const wmsMode = req.headers["x-mock-wms-status"] || "200";

  try {
    await reserveInventory(orderId, body.items || []);

    const wmsStatus = await confirmWms(orderId, wmsMode);
    if (wmsFailed(wmsStatus)) {
      await releaseInventory(orderId);
      return res.status(503).json({ error: "WMS no confirmó (E4)", orderId, wmsStatus });
    }

    await pool
      .request()
      .input("id", sql.UniqueIdentifier, orderId)
      .input("customerId", sql.NVarChar, body.customerId || "unknown")
      .input("hash", sql.NVarChar, payloadHash)
      .input("status", sql.NVarChar, "CONFIRMED")
      .query(
        "INSERT INTO orders (id, customer_id, payload_hash, status) VALUES (@id, @customerId, @hash, @status)"
      );

    const eventPayload = JSON.stringify({
      event_type: "OrderCreated",
      order_id: orderId,
      correlation_id: idempotencyKey,
    });
    await pool
      .request()
      .input("agg", sql.UniqueIdentifier, orderId)
      .input("payload", sql.NVarChar, eventPayload)
      .query(
        "INSERT INTO outbox (aggregate_id, event_type, payload, status) VALUES (@agg, 'OrderCreated', @payload, 'PENDING')"
      );

    const response = { orderId, status: "CONFIRMED", scenario: "E1" };
    await redis.set(`idem:${idempotencyKey}`, JSON.stringify(response), "EX", 86400);
    return res.status(201).json(response);
  } catch (err) {
    if (err.status === 409) {
      return res.status(409).json({ error: "Inventario insuficiente (E3)" });
    }
    console.error(err);
    return res.status(500).json({ error: "Error interno", detail: err.message });
  }
});

initDb()
  .then(() => {
    app.listen(PORT, () => console.log(`order-service listening on ${PORT}`));
  })
  .catch((err) => {
    console.error("DB init failed", err);
    process.exit(1);
  });
