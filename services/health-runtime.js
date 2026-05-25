const startTime = Date.now();

function getHealthRuntime() {
  return {
    status: 'ok',
    service: 'SYSTEMS.OS',
    uptimeSeconds: Math.floor((Date.now() - startTime) / 1000),
    timestamp: new Date().toISOString(),
  };
}

module.exports = {
  getHealthRuntime,
};
