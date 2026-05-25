const fs = require('node:fs/promises');
const path = require('node:path');

const registryPath = path.resolve(__dirname, '..', 'data', 'system_registry.json');

async function getSystemRegistry() {
  const raw = await fs.readFile(registryPath, 'utf8');
  const parsed = JSON.parse(raw);

  if (!Array.isArray(parsed.systems)) {
    throw new Error('Invalid system registry format: systems must be an array');
  }

  return {
    version: parsed.version || '1.0.0',
    systems: parsed.systems,
    generatedAt: parsed.generatedAt || null,
  };
}

module.exports = {
  getSystemRegistry,
};
