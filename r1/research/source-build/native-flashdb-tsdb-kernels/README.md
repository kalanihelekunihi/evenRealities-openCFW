# Pinned FlashDB TSDB helper reuse

Five C bodies are extracted from FlashDB 2.0.0 commit
`4e5677408256f82d47cd56a6b04605dcee35ed9a` under Apache-2.0.
`upstream-slices.json` binds original function slices before visibility/name
adaptation. Source struct layout assertions bind the accessed native fields,
80-byte sector header and 32-byte log index to the recovered configuration.

Reproduce with `python3 r1/tools/build_native_flashdb_tsdb_kernels.py`, then
`/tmp/r1-source-venv/bin/python r1/tools/verify_native_flashdb_tsdb_kernels.py`.
The verifier executes authenticated native code and compiled source in Unicorn.
50,000 boundary/random comparisons pass for R0, callee-saved registers, restored
SP and the 512-byte input/output region. Native/source private stack history,
flags and unused scratch state are not included in that typed contract.

Raw R0-R3 differences remain in forward-sector and both log-index helpers.
Reverse-sector and count-callback R0-R3 agree in the tested cases. These results
do not close the raw ABI gate or promote any body into the main provider graph.
The count callback's compiled 18-byte body is not byte-identical: its increment
uses a different encoding. REA's Ghidra read at 0x87428 independently binds the
native bytes; Ghidra-MCP currently reports no running GUI instance.

The helper source avoids the upstream logging macros. Full control, count and
time-iterator APIs still require native logging, assertion, callback and frame
contracts. The existing no-op FDB_PRINT configuration is not evidence that
those native paths can be omitted. Source attribution enables deliberate
upstream updates, but later releases require contract replay rather than
unverified replacement. Whole-image byte equality and hardware proof remain
open.
