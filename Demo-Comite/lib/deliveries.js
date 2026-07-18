let sessionRef = null;

function bindDeliveriesSession(session) {
  sessionRef = session;
}

function emptyJourney() {
  return { accepted: false, deliveryCompleted: false, evidenceValid: null };
}

function nextDeliveryId() {
  const nums = sessionRef.deliveries
    .map((d) => Number.parseInt(String(d.id), 10))
    .filter((n) => Number.isFinite(n));
  const max = nums.length ? Math.max(...nums) : 120;
  return String(max + 1);
}

function normalizeDeliveryIds() {
  const used = new Set();
  for (const d of sessionRef.deliveries) {
    let id = String(d.id);
    if (used.has(id)) {
      id = nextDeliveryId();
      while (used.has(id)) {
        id = String(Number.parseInt(id, 10) + 1);
      }
      d.id = id;
    }
    used.add(String(d.id));
  }
}

function initDeliveries() {
  return [
    {
      id: "123",
      orderId: null,
      customer: "Próximo pedido del portal",
      address: "Se asigna al confirmar en Portal B2B",
      journey: emptyJourney(),
    },
  ];
}

function deliveryStatus(d) {
  if (d.journey.deliveryCompleted) return "DELIVERED";
  if (d.journey.evidenceValid === true) return "POD_OK";
  if (d.journey.accepted) return "AT_DESTINATION";
  return "IN_TRANSIT";
}

function formatDelivery(d) {
  return {
    id: d.id,
    orderId: d.orderId,
    customer: d.customer,
    address: d.address,
    status: deliveryStatus(d),
    journey: d.journey,
    canAccept: deliveryStatus(d) === "IN_TRANSIT" && Boolean(d.orderId),
    canTakePhoto: d.journey.accepted && !d.journey.deliveryCompleted,
    canComplete: d.journey.evidenceValid === true && !d.journey.deliveryCompleted,
  };
}

function findDelivery(id, orderId) {
  if (orderId) {
    const byOrder = findDeliveryByOrderId(orderId);
    if (byOrder) return byOrder;
  }
  if (id == null || id === "") return undefined;
  const key = String(id);
  return sessionRef.deliveries.find((d) => String(d.id) === key);
}

function findDeliveryByOrderId(orderId) {
  return sessionRef.deliveries.find((d) => d.orderId === orderId);
}

function getActiveDelivery() {
  return sessionRef.activeDeliveryId ? findDelivery(sessionRef.activeDeliveryId) : null;
}

function assignOrderToRoute(orderId, customerId) {
  normalizeDeliveryIds();
  let slot = sessionRef.deliveries.find((d) => !d.orderId);
  if (!slot) {
    slot = {
      id: nextDeliveryId(),
      orderId: null,
      customer: "Cliente B2B",
      address: "Por asignar",
      journey: emptyJourney(),
    };
    sessionRef.deliveries.push(slot);
  }
  slot.orderId = orderId;
  slot.customer = customerId;
  slot.address = "Av. Javier Prado 4200, San Borja";
  slot.journey = emptyJourney();
  return slot.id;
}

module.exports = {
  bindDeliveriesSession,
  emptyJourney,
  initDeliveries,
  deliveryStatus,
  formatDelivery,
  findDelivery,
  findDeliveryByOrderId,
  getActiveDelivery,
  assignOrderToRoute,
  normalizeDeliveryIds,
  nextDeliveryId,
};
