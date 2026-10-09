# Authentic inline emission and rejected divider attribution

Address-taking in three typed data pointers emits the authentic public
always-inline bodies; no implementation wrappers or forced stubs were added.
Keep-static alone emitted none of these bodies. The producing translation unit
and options remain unknown; this is an explicit comparison emission contract.

`Cy_SCB_SetRxFifoLevel` at `[0x9316,0x9342)` matches all44stock bytes, without
relocations. It validates the FIFO level then updates the RX FIFO trigger field,
preserving other bits. This is one new selected candidate awaiting independent
review. The authentic source lives in `cy_scb_common.h`; `results.json` records
header/object hashes and comparison bytes.

The two historical HF divider attributions fail: public getter emits16bytes
with a right-shift by2, whereas stock `0x9F34` extracts bits0–1. Public setter
emits28bytes, accepts divider0–3 and writes bits2–3; stock `0x9F44` accepts
source0–1, validates readiness and writes bits0–1. Mismatch positions are
retained in `results.json`; no source/device definitions were fitted to them.
The adjacent `touch-clkhf14-attribution-2026-10-09` successor tests actual
unchanged source-selection functions against those stock extents.

The presence of a callable emitted inline does not establish original TU/flags,
physical FIFO behavior, interrupts, unique producer or source completeness.
