# LIS2DW12 tap policy in C

The stock disable routine at `0x751b8` and enable routine at `0x75290` now
express their sensor settings and logging decisions in C in
`r1/src/application/runtime/native_lis_aux.c`. REA/Ghidra independently
recovered both native instruction sequences from a symbol-annotated ELF
containing the unchanged locked application bytes. The source route getter
retains its call boundary with `noinline`.

Disable reads the INT1 route, clears bit 3, writes it, disables Z/Y/X tap
detection and double-tap mode, then sets full scale to 2 and data rate to 3.
Enable sets Z/Y/X detection, X/Y/Z thresholds to 3, duration/quiet/shock to 0,
and mode to 1 before reading, setting bit 3 and writing the INT1 route.
Both routines ignore sensor helper errors and return 1. Ring and SDK logging
gates read live mode separately, including the short-circuited second ring
read, and retain the native messages and IDs.

Each routine keeps a 10-byte assembly bridge to capture the incoming R3 word,
supply its low byte as the route scratch, and restore the modified word to R3.
Replacing it with a zeroed or indeterminate C local would change native behavior
when the route getter leaves the byte untouched. The route setter's existing
frame bridge also remains. C bodies change private call-stack depth; these
routines are behavior candidates, without instruction-byte qualification.

Verification:

- 49,152 paired native/C policy cases (98,304 executions), covering both
  routines, four incoming scratch words, absent/byte/word getter writes,
  four raw helper status words and all 512 three-read logging-mode sequences.
  Helper order, arguments, logging strings, scratch state, restored R3,
  callee-saved registers and interrupt masks agree.
- 2,096 route-get cases and 1,728 route-set cases pass with actual C/native
  register wrappers and modeled bus callbacks. The setter C body and bridge
  remain byte-unchanged from the preceding normal build.
- Negative controls reject cached mode reads, zeroed scratch and early return
  after a route-get error.
- All 573 R1 units compile and compose without failures or duplicate strong
  symbols. Imports remain 197 application / 34 bootloader. `make sources-check`
  passes.
- The unchanged canonical plan still produces a stock-identical hybrid
  application, SHA-256
  `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
  It contains 3,827 source-built bytes and 642,333 unclassified binary
  pull-through bytes. Source completeness remains false.

Sensor-setting and logging calls are modeled in the policy comparison. The
separate route tests execute their native/C wrappers, with bus callbacks modeled.
Caller-clobbered registers other than restored R3, APSR flags, arbitrary callback
access to private stack frames, physical sensor operation and IRQ/timing behavior
are outside these receipts. No G2 workflow gate advances. Exact source, REA,
probe and build hashes are recorded in `lis-c-tap-policy-review.json`.
