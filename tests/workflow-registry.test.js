const test = require('node:test');
const assert = require('node:assert/strict');
const { queueWorkflow } = require('../services/workflow-registry');

test('queueWorkflow returns queued workflow receipt with payload data', () => {
  const receipt = queueWorkflow({ workflowType: 'deployment', metadata: { source: 'test' } });
  assert.equal(receipt.status, 'queued');
  assert.equal(receipt.workflowType, 'deployment');
  assert.deepEqual(receipt.metadata, { source: 'test' });
  assert.match(receipt.workflowId, /^[0-9a-f-]{36}$/i);
  assert.equal(typeof receipt.acceptedAt, 'string');
});
