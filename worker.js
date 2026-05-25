const { getHealthRuntime } = require('./services/health-runtime');
const { getSystemRegistry } = require('./services/system-registry');
const { queueWorkflow } = require('./services/workflow-registry');

function json(data, init = {}) {
  return new Response(JSON.stringify(data), {
    status: init.status || 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      ...(init.headers || {}),
    },
  });
}

async function handleRequest(request) {
  const url = new URL(request.url);

  if (request.method === 'GET' && url.pathname === '/health') {
    return json(getHealthRuntime());
  }

  if (request.method === 'GET' && url.pathname === '/system/status') {
    const health = getHealthRuntime();
    const registry = await getSystemRegistry();

    return json({
      status: health.status,
      service: health.service,
      uptimeSeconds: health.uptimeSeconds,
      registryCount: registry.systems.length,
      timestamp: health.timestamp,
    });
  }

  if (request.method === 'GET' && url.pathname === '/systems/registry') {
    return json(await getSystemRegistry());
  }

  if (request.method === 'POST' && url.pathname === '/workflows/queue') {
    let payload = {};
    try {
      payload = await request.json();
    } catch {
      payload = {};
    }
    return json(queueWorkflow(payload), { status: 202 });
  }

  return json({ error: 'Not Found', path: url.pathname }, { status: 404 });
}

module.exports = {
  handleRequest,
  fetch: (request) => handleRequest(request),
};
