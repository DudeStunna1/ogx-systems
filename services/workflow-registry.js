const crypto = require('node:crypto');

function queueWorkflow(payload = {}) {
  const workflowType = payload.workflowType || 'unspecified';

  return {
    workflowId: crypto.randomUUID(),
    workflowType,
    status: 'queued',
    acceptedAt: new Date().toISOString(),
    metadata: payload.metadata || {},
  };
}

module.exports = {
  queueWorkflow,
};
