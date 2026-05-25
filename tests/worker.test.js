const test = require('node:test');
const assert = require('node:assert/strict');
const worker = require('../worker');

test('POST /workflows/queue returns 202 and queue receipt', async () => {
  const request = new Request('http://local/workflows/queue', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ workflowType: 'sync', metadata: { source: 'worker-test' } }),
  });

  const response = await worker.fetch(request);
  const body = await response.json();

  assert.equal(response.status, 202);
  assert.equal(body.status, 'queued');
  assert.equal(body.workflowType, 'sync');
  assert.deepEqual(body.metadata, { source: 'worker-test' });
  assert.match(body.workflowId, /^[0-9a-f-]{36}$/i);
});
