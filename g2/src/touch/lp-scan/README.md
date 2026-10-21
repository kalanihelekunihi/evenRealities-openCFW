# Independent offline LP scan launch

scan.c/h reconstructs stock0x6d74..0x702c with existing closed mode/GPIO/MRSS/PDL dependencies. It configures channel-engine baseline/signal processing, copies eleven-word LP frames, checks readiness, programs AOS/result-start fields and starts scanning. Reusing the same range skips frame reload; errors retain documented partial state/busy flags. No hardware model, production firmware patch or complete-image build claim.

Evidence and pseudocode explanation: ../../../analysis/touch-lp-filter-closure-2026-10-08/REPORT.md.1952 bounded instruction/source cases pass; actual initialization/preparation compositions are explicitly sliced and peripherals synthetic. History allocation426-byte gap and partial/full result-window arithmetic are separate facts; no physical overflow claim.
