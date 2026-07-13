const express = require("express");
const sql = require("mssql");

const PORT = process.env.PORT || 8081;

const sqlConfig = {
  server: process.env.SQL_SERVER,
  database: process.env.SQL_DATABASE || "db-inventory",
  user: process.env.SQL_USER,
  password: process.env.SQL_PASSWORD,
  options: { encrypt: true, trustServerCertificate: false },
};

let pool;
const app = express();
app.use(express.json());

async function initDb() {
  pool = await sql.connect(sqlConfig);
  await pool.request().query(`
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'stock')
    CREATE TABLE stock (sku NVARCHAR(50) PRIMARY KEY, quantity INT NOT NULL);
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'reservations')
    CREATE TABLE reservations (
      order_id UNIQUEIDENTIFIER PRIMARY KEY,
      sku NVARCHAR(50) NOT NULL,
      quantity INT NOT NULL,
      status NVARCHAR(20) NOT NULL
    );
    MERGE stock AS t
    USING (SELECT 'SKU-001' AS sku, 100 AS quantity) AS s
    ON t.sku = s.sku
    WHEN NOT MATCHED THEN INSERT (sku, quantity) VALUES (s.sku, s.quantity);
  `);
}

app.get("/health", (_req, res) => res.json({ status: "ok", app: "MS-INI01-02" }));

app.post("/v1/reservations", async (req, res) => {
  const { orderId, items } = req.body || {};
  const item = (items && items[0]) || { sku: "SKU-001", quantity: 1 };
  const tx = new sql.Transaction(pool);
  await tx.begin();
  try {
    const stock = await new sql.Request(tx)
      .input("sku", sql.NVarChar, item.sku)
      .query("SELECT quantity FROM stock WITH (UPDLOCK) WHERE sku = @sku");
    if (!stock.recordset.length || stock.recordset[0].quantity < item.quantity) {
      await tx.rollback();
      return res.status(409).json({ error: "Stock insuficiente (E3)" });
    }
    await new sql.Request(tx)
      .input("sku", sql.NVarChar, item.sku)
      .input("qty", sql.Int, item.quantity)
      .query("UPDATE stock SET quantity = quantity - @qty WHERE sku = @sku");
    await new sql.Request(tx)
      .input("orderId", sql.UniqueIdentifier, orderId)
      .input("sku", sql.NVarChar, item.sku)
      .input("qty", sql.Int, item.quantity)
      .query(
        "INSERT INTO reservations (order_id, sku, quantity, status) VALUES (@orderId, @sku, @qty, 'RESERVED')"
      );
    await tx.commit();
    return res.status(201).json({ orderId, status: "RESERVED" });
  } catch (e) {
    await tx.rollback();
    throw e;
  }
});

app.delete("/v1/reservations/:orderId", async (req, res) => {
  const orderId = req.params.orderId;
  const row = await pool
    .request()
    .input("orderId", sql.UniqueIdentifier, orderId)
    .query("SELECT sku, quantity FROM reservations WHERE order_id = @orderId");
  if (!row.recordset.length) return res.status(404).json({ error: "No encontrada" });
  const { sku, quantity } = row.recordset[0];
  await pool
    .request()
    .input("sku", sql.NVarChar, sku)
    .input("qty", sql.Int, quantity)
    .query("UPDATE stock SET quantity = quantity + @qty WHERE sku = @sku");
  await pool
    .request()
    .input("orderId", sql.UniqueIdentifier, orderId)
    .query("DELETE FROM reservations WHERE order_id = @orderId");
  return res.json({ orderId, status: "RELEASED" });
});

initDb()
  .then(() => app.listen(PORT, () => console.log(`inventory-service on ${PORT}`)))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });
