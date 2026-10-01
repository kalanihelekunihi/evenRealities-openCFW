# Independent review 1927 — touch row overlay boundary 1927

**Result: PASS_SCOPED.** Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-row-overlay-8680-boundary-traces-1918/001`; receipt SHA-256 `efd227f63318f2f093dd3f767cc7f363310c6cad2d428e79d596b4a4afc7d3ff`.

Receipt file hashes and source pin match. Isolated replay regenerates all 16 trace records byte-for-byte. Every fixture executes original 8680 instructions with no helper interception; the synthetic scratch interval is [0,4), current row is at the base, width 128, copy count 1 and mirror is disabled.

The observed boundaries agree with the branch model: count zero returns the literal error; a positive count with sequence zero performs no overlay iterations; one iteration copies ABCD from scratch+16 to scratch+64; and two or more iterations retain an earlier blank-row checksum error and skip the final copy. Whole-buffer output, result and SP are checked.

This is a trace-only boundary slice with fixed geometry and synthetic blank rows. It does not establish full routine pseudocode, mirror/general interval behavior, provider paths, physical storage, or canonical admission.
