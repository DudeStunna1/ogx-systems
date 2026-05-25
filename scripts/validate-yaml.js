const fs = require('node:fs');
const path = require('node:path');
const YAML = require('yaml');

const filePath = path.resolve(__dirname, '..', 'config', 'systems.yaml');

try {
  const raw = fs.readFileSync(filePath, 'utf8');
  YAML.parse(raw);
  console.log('YAML validation passed:', filePath);
} catch (error) {
  console.error('YAML validation failed:', error.message);
  process.exitCode = 1;
}
