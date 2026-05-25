const fs = require('node:fs');
const path = require('node:path');

const filePath = path.resolve(__dirname, '..', 'data', 'system_registry.json');

try {
  const raw = fs.readFileSync(filePath, 'utf8');
  JSON.parse(raw);
  console.log('JSON validation passed:', filePath);
} catch (error) {
  console.error('JSON validation failed:', error.message);
  process.exitCode = 1;
}
