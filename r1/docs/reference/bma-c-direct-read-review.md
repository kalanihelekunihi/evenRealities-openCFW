# Bosch direct register read policy in C

The direct-read routine at stock `0x87bbc` now uses a C body in
`r1/src/application/runtime/native_bma_reads.c`. REA/Ghidra confirms validation
order, full-word register/result handling, the 128-byte callback buffer,
low-byte status store, and live dummy-byte reads during copying.

The C body validates the device before testing the output pointer, applies the
SPI read bit when interface is zero, loads dummy count/callback/handle in stock
order, and invokes the callback with the full register and wrapped 32-bit
length-plus-dummy count. It stores the low result byte but tests the complete
result word: raw `0x100` is failure even though the stored byte becomes zero.
On success the existing C copy helper reloads the dummy byte on every iteration.
The native callback slot is loaded as one volatile alias-permitted word and
interpreted using the product adapter's full-word ABI, separately from the
pinned Bosch byte-register/byte-result declaration.

A 24-byte assembly bridge retains the native 152-byte frame: 128 uninitialized
buffer bytes followed by six saved registers. An extra eight-byte outgoing
argument area passes the buffer to C. The buffer remains at entry SP minus 152;
callback stack depth changes from -152 to -192, or -160 to -200 when the actual
product adapter executes. No zero initialization or transfer-length guard is
introduced. This is a behavior candidate, without byte qualification.

Verification:

- 6,332 paired direct native/C cases execute the actual null checker and copy
  helper, with the transport callback modeled. They cover all byte register
  values, full-word registers/results, interface modes, callback buffer writes
  or no writes, zero/bounded lengths, null/invalid contexts, dummy/handle/callback
  mutations and output aliasing the context's dummy byte. Context access traces,
  callback arguments, buffer/output/context bytes, status, preserved registers,
  entry SP and interrupt masks agree. Wrapped full-word transfer length is
  checked on a callback-error path.
- Another 6,332 paired cases execute the actual native/C product read adapters,
  with only the motion-bus request boundary modeled. This verifies its address
  byte load, 16-bit request-length truncation and success/error normalization.
- All 1,791 read-control regression cases pass.
- Negative controls reject byte-truncated status, byte-truncated register and a
  zero-filled callback buffer.
- All 573 R1 units compile and compose without failures or duplicate strong
  symbols, with imports unchanged at 197 application / 34 bootloader.
  `make sources-check` passes.
- The unchanged canonical plan builds a stock-identical hybrid application,
  SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
  It retains 3,827 source-built bytes and 642,333 unclassified binary-pull-through
  bytes; source completeness remains false.

Successful-copy comparisons stay within the native buffer; excessive successful
lengths, 16-bit copy-index wrap, corrupted saved-frame faults, arbitrary callback
inspection of private stack frames, caller-clobbered registers/flags and physical
sensor/bus behavior remain unverified. No G2 workflow gate advances. Source,
REA, test and build hashes are recorded in `bma-c-direct-read-review.json`.
