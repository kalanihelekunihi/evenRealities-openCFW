import crypto from "node:crypto";
import fs from "node:fs";

function fail(message) {
  process.stderr.write(`runtime TLSF wasm proof failed: ${message}\n`);
  process.exit(1);
}

if (process.argv.length !== 3) {
  fail("usage: node runtime_tlsf_wasm_runner.js MODULE.wasm");
}

const modulePath = process.argv[2];
let bytes;
try {
  bytes = fs.readFileSync(modulePath);
} catch (error) {
  fail(`cannot read ${modulePath}: ${error.message}`);
}

let module;
try {
  module = new WebAssembly.Module(bytes);
} catch (error) {
  fail(`invalid WebAssembly module: ${error.message}`);
}

const imports = WebAssembly.Module.imports(module);
if (imports.length !== 0) {
  fail(`module has ${imports.length} unexpected import(s)`);
}

let instance;
try {
  instance = new WebAssembly.Instance(module, {});
} catch (error) {
  fail(`cannot instantiate module: ${error.message}`);
}

const memory = instance.exports.memory;
if (!(memory instanceof WebAssembly.Memory)) {
  fail("module does not export WebAssembly memory");
}

const run = instance.exports.open_cfw_tlsf_wasm_run;
if (typeof run !== "function") {
  fail("module does not export open_cfw_tlsf_wasm_run");
}

const result = run();
if (result !== 0) {
  fail(`allocator oracle returned ${result}`);
}

const proof = {
  abi: "wasm32-ilp32",
  imports: imports.length,
  memory_bytes: memory.buffer.byteLength,
  module_bytes: bytes.length,
  result,
  sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
};
process.stdout.write(`${JSON.stringify(proof)}\n`);
