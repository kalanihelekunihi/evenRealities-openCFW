# Current scan — 2026-10-05T18:04:42.292982+00:00

Compared with the 16:59 UTC scan, foundation C/header inventory grew from 7 to 15 (8 added, 2 changed). All are visible to Git; none is ignored. Touch now includes FIFO trigger behavior and linked RX/TX/trigger validation. Apollo now has four MSPI interrupt operations plus disable/deinitialize. These are callable source modules, not complete firmware providers.

Fresh focused tests: **24 pass, zero failures** (touch 11, MSPI 6, resource preservation 7). Saved original/source comparison evidence covers 234 unique touch instruction bytes, 230 MSPI interrupt bytes, and 174 MSPI lifecycle bytes: 638 cumulative nonoverlapping bytes. Lifecycle queue-disable/termination/delay calls remain explicitly stubbed. Saved comparison/ELF hashes and current build-input checks are recorded in comparison.json; mismatched historical inputs must not be described as fresh execution validation. Original-instruction comparisons were not rerun by this scan.

New CMDQ static evidence identifies the 12-byte disable wrapper and 66-byte CMDQ disable body. It proves a register/enable-bit clear with no wait/free in those bodies. Termination uses a global per-module queue pointer and force=true, unlike disable's caller-local pointer lookup. This remains analysis: no new CMDQ implementation/link-validation exists yet.

Packer, official manifest, workflow state, and official Apollo hashes remain unchanged. The production reference target still repacks official payloads. Zero complete blob-free source payloads and no source-built byte-identical bundle have been demonstrated. Broad campaign coverage was not recomputed; earlier 4.58% reviewed/11.40% exported figures are historical footprints, not source completion.

Build binaries/reports under g2/build are ignored by the existing build/ rule; accepted foundation source is visible. The next concrete implementation gap is replacing the CMDQ-disable stub with its recovered behavior, then bounding termination/index-refresh separately. No firmware edits, commits, staging, device writes, shared-state edits, or broad campaign scans were performed.
