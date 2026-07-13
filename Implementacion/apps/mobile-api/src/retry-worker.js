// Stub MVP — worker de reintentos SQS → EventBridge (extender en fase 2)
const jitter = Number(process.env.JITTER_MS || 500);
console.log(`retry-worker stub (jitter ${jitter}ms)`);
setInterval(() => {}, 60_000);
