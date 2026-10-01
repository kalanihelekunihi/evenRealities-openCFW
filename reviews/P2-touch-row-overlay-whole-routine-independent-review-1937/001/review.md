# Independent review 1937 — whole row-overlay routine

**Result: REVISE_PROSE.** Candidate `touch-row-overlay-whole-routine-1928/001`; receipt SHA-256 `90d577ec596e00671c0722cc5641543262f98800cf8b19194acb73e50a3b467d`.

Receipt binds to the pinned source. Independent Capstone M-class decode reproduces all 183 instructions across [0x8680,0x8804), exactly matching the 388-byte body and saved disassembly. All five parent trace receipt hashes and each listed file hash match. This packet contains pseudocode/disassembly but no replay harness, so no fixture regeneration was possible for this whole-body candidate.

Most control-flow/dataflow claims agree with the decode: the sequence/count branch chooses a bounded candidate count; the final iteration uses scratch and does not reset the previous checksum status; candidate failures can therefore persist; the provider call result is not subsequently tested.

The left-starting overlap pseudocode is incorrect. At 0x87C6–0x87D4, code compares windowEnd with overlayEnd. If windowEnd is below overlayEnd, it sets copy amount to windowEnd−windowStart; otherwise it retains overlayEnd−windowStart. The decoded amount is therefore min(windowEnd, overlayEnd)−windowStart, not unconditionally overlayEnd−windowStart. This is a right-edge clamp in that branch. The related 1926 trace’s offset=60,length=128 case does not distinguish these models: bytes beyond the logical window are zero in both synthetic source backing and destination, so its whole-buffer equality cannot evidence writes beyond that window.

This is an append-only pseudocode correction request; no candidate files were changed. Other geometry and all external provider/physical storage behavior remain subject to the packet’s stated limits. Parent trace fixtures do not close the full whole-body semantic model. Canonical admission remains false.
