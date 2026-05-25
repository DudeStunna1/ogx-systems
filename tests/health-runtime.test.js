const test = require('node:test');
const assert = require('node:assert/strict');
const { getHealthRuntime } = require('../services/health-runtime');

test('getHealthRuntime returns ok status payload', () => {
  const health = getHealthRuntime();
  assert.equal(health.status, 'ok');
  assert.equal(health.service, 'SYSTEMS.OS');
  assert.equal(typeof health.uptimeSeconds, 'number');
  assert.equal(typeof health.timestamp, 'string');
});
