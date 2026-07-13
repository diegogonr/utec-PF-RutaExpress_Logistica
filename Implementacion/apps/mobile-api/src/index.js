const express = require("express");
const app = express();
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok", app: "APP-15" }));

app.post("/deliveries/:id/complete", (req, res) => {
  res.json({
    deliveryId: req.params.id,
    ack: true,
    scenario: "E6",
  });
});

app.post("/deliveries/:id/evidence", (req, res) => {
  const { sha256 } = req.body || {};
  if (!sha256 || sha256 === "invalid") {
    return res.status(400).json({
      deliveryId: req.params.id,
      scenario: "E7",
      error: "Hash invalido",
    });
  }
  res.json({
    deliveryId: req.params.id,
    stored: true,
    scenario: "E7",
  });
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`mobile-api on ${port}`));
