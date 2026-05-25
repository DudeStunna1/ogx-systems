const test = require('node:test');
const assert = require('node:assert/strict');
const { getSystemRegistry } = require('../services/system-registry');

test('getSystemRegistry returns systems array from data file', async () => {
  const registry = await getSystemRegistry();
  assert.equal(registry.version, '1.0.0');
  assert.ok(Array.isArray(registry.systems));
  assert.ok(registry.systems.length > 0);
  assert.equal(registry.systems[0].id, 'core-runtime');
});
