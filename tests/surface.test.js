import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const html=fs.readFileSync("index.html","utf8");
const manifest=JSON.parse(fs.readFileSync("ogx-systems.manifest.json","utf8"));
const pages=fs.readFileSync(".github/workflows/pages-activation.yml","utf8");

test("surface identifies OGX Systems without claiming live deployment",()=>{
  assert.match(html,/OGX SYSTEMS/);
  assert.match(html,/NOT YET VERIFIED/);
  assert.equal(manifest.domain_ref,"OGX_SYSTEMS");
  assert.equal(manifest.deployment_state,"NOT_VERIFIED");
  assert.equal(manifest.dns_state,"NOT_VERIFIED");
  assert.equal(manifest.qualification_state,"NOT_QUALIFIED");
});

test("activation workflow is explicit manual dispatch",()=>{
  assert.match(pages,/workflow_dispatch/);
  assert.match(pages,/actions\/deploy-pages@v4/);
});

test("surface avoids false global health claims",()=>{
  assert.doesNotMatch(html,/100%\s+OPERATIONAL/i);
  assert.doesNotMatch(html,/ALL SYSTEMS OPERATIONAL/i);
});
