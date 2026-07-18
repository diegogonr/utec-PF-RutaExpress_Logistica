/** Inventario visible en la demo (espejo de sesión alineado al seed MS-INI01-02). */

const CATALOG = [
  {
    sku: "SKU-001",
    label: "Caja retail estándar",
    cd: "CD Lima Sur",
    seed: 100,
  },
  {
    sku: "SKU-002",
    label: "Kit promocional temporada",
    cd: "CD Lima Norte",
    seed: 0,
  },
  {
    sku: "SKU-003",
    label: "Insumo farmacia (cadena frío)",
    cd: "CD Callao",
    seed: 0,
  },
  {
    sku: "SKU-004",
    label: "Electro mediano (marketplace)",
    cd: "CD Arequipa",
    seed: 0,
  },
  {
    sku: "SKU-005",
    label: "Bebida pack ×24",
    cd: "CD Lima Sur",
    seed: 0,
  },
];

function createInventoryState() {
  return {
    levels: Object.fromEntries(CATALOG.map((c) => [c.sku, c.seed])),
    reservedOpen: 0,
    movements: [],
  };
}

function snapshot(state) {
  const items = CATALOG.map((c) => {
    const available = state.levels[c.sku] ?? 0;
    return {
      sku: c.sku,
      label: c.label,
      cd: c.cd,
      seed: c.seed,
      available,
      status: available > 0 ? "ok" : "empty",
    };
  });
  return {
    items,
    totals: {
      skus: items.length,
      withStock: items.filter((i) => i.available > 0).length,
      units: items.reduce((sum, i) => sum + i.available, 0),
      reservedOpen: state.reservedOpen,
    },
    movements: state.movements.slice(0, 12),
    source: "MS-INI01-02 · seed Azure SQL (vista de sesión)",
  };
}

function pushMovement(state, entry) {
  state.movements.unshift({
    at: new Date().toISOString(),
    ...entry,
  });
  if (state.movements.length > 40) state.movements.length = 40;
}

/**
 * Aplica el resultado del pedido al espejo de sesión.
 * E1: descuenta stock. E3: rechazo. E4: reserva compensada (sin cambio neto).
 */
function applyOrderResult(state, { scenario, sku, quantity, orderId }) {
  const qty = Number(quantity) || 0;
  const code = sku || "SKU-001";
  if (!(code in state.levels)) state.levels[code] = 0;

  if (scenario === "E1") {
    state.levels[code] = Math.max(0, state.levels[code] - qty);
    state.reservedOpen += qty;
    pushMovement(state, {
      type: "reserve",
      tone: "ok",
      sku: code,
      quantity: qty,
      orderId: orderId || null,
      label: `Reservado ${qty} uds. · ${code}`,
    });
    return;
  }

  if (scenario === "E3") {
    pushMovement(state, {
      type: "reject",
      tone: "warn",
      sku: code,
      quantity: qty,
      orderId: orderId || null,
      label: `Sin stock · ${code} (pedido ${qty} uds.)`,
    });
    return;
  }

  if (scenario === "E4") {
    pushMovement(state, {
      type: "compensate",
      tone: "warn",
      sku: code,
      quantity: qty,
      orderId: orderId || null,
      label: `Saga: reserva liberada · ${code}`,
    });
  }
}

function resetInventory(state) {
  state.levels = Object.fromEntries(CATALOG.map((c) => [c.sku, c.seed]));
  state.reservedOpen = 0;
  state.movements = [];
  pushMovement(state, {
    type: "reset",
    tone: "info",
    sku: null,
    quantity: 0,
    orderId: null,
    label: "Vista de sesión reiniciada al seed MVP",
  });
}

module.exports = {
  CATALOG,
  createInventoryState,
  snapshot,
  applyOrderResult,
  resetInventory,
};
