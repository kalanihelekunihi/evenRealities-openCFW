# Goodix initialization probe reconstructed in C

REA confirms stock `0x509e0` clears the active mask and forty bytes beginning
at `0x2001e51c` before powering the device. The shared C counter allocation is
therefore expanded from eight to ten words. Earlier release/acquire evidence
covered accessed indices through seven; it did not establish the initialization
extent. The full span ends immediately before the separate FAL cache at
`0x2001e544`; no ownership of that cache is added.

`r1_goodix_initialize_probe` now clears those forty bytes through the existing
AEABI memory-clear provider, raises reset, prepares transport, opens the bus,
busy-delays ten milliseconds and calls the Goodix initializer. Its full int
return is saved. A zero result means success; any nonzero word means failure.
Cleanup occurs in both cases: bus close, transport release, IRQ close and reset
low. The policy callback word is preserved.

The routine preserves live logging queries and short-circuit behavior. It asks
for mode bit one, conditionally asks again for bit four, and independently asks
again for bit two. Structured logging uses marker `0x0c400000`, identical
descriptor/format pointers to `[RING]%s ppg init\r\n` and the saved result's
success/failed string. Nordic logging uses stock header `0x001c0003` and
`%s ppg init\r\n`. Logging return values do not replace the saved result.

The probe passes 4,096 paired stock/C cases (8,192 executions): four initializer
result words, all triples of low-three-bit logging mode values, and two nonzero
counter seeds. It compares call order/arguments and diagnostic strings, live
query count, exact forty-byte clear and adjacent canary, preserved callback,
result words and preserved registers/stack/masks. The harness places source
counter storage separately so its post-span canary cannot alias another source
global; this is a test layout, not final firmware placement.

All 2,080 acquire, 2,080 release and 192 profile regressions pass against the
current object. Negative controls for a thirty-two-byte clear and a single
cached log-mode query both fail the oracle. The actual memory-clear, hardware,
SDK and logging providers are controlled probe boundaries.

The normal report `build/sources-goal-r1-goodix-initialize/report.json` compiles
569 R1 units without failures or duplicate strong symbols. Imports remain
197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-c-initialize-review.json) binds REA, owned source,
execution probes, negative controls and normal build by hash.

The C body is 164 bytes versus 140 native instruction bytes and is not
byte-qualified. The canonical source plan and G2 gates are unchanged. Initial
startup contents/final addresses, private frames/caller-clobbered registers and
flags, actual diagnostic output, concurrency, physical reset/bus/timing and
complete source-only byte identity remain unverified.
