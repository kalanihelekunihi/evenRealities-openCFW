# OpenCFW change scan — 2026-10-07 20:28 UTC

Compared with the saved 19:41 UTC scan. This scan only reads evidence and writes this report/snapshot; no tests, generators, firmware changes, staging or campaign changes.

Component C/header/assembly inventory increased from 391 to 404: 315 bootloader, 89 foundation. 13 new files, no modified baseline files and no removals. Exact paths/hashes are in snapshot.json. Git check-ignore found no ignore rule for the changed source files. Build outputs remain separate from the visible source inventory.

The separately owned 215-object candidate aac9ab01… has an independently verified ELF SHA-256 matching its recorded identity. Its three integration receipts now report all seven cases PASS: normal/update 2, malformed-input 3, interrupted-update 2. The 214-object predecessor is preserved. Shared offline ELF hash is unchanged at 129a6b2f38f145f33e791874f52d722fb1715d5fff5c957a285644312f34a6f9.

New evidence reports 16 installed-updater fixtures, 151 callback-cut updater fixtures, 128 wrapper fixtures and 152 classifier bucket comparisons. The negative-zero classifier difference was corrected in the owned successor. The updater binding already existed in its predecessor; it should not be counted as a newly reconstructed function. Three signaling-NaN inputs still differ in cumulative FPSCR exception flags: bucket agreement is not full helper equivalence.

Additional standalone reconstruction receipts report PCM2.1 boost service (stock 0x42ae9c, 80 bytes) PASS across 128 cases and PCM2.2 selector 6 (stock 0x428840, 222 bytes) PASS across 192 cases. These addons are not installed into the 215-object candidate. Its actual HP-to-LP call path still reaches the unsupported selector-6 binding; the standalone test does not close that integrated path.

All results are existing bounded original-instruction comparisons inspected, not rerun here. Synthetic MMIO, unavailable resident-ROM delay stubs and unverified scheduling/peripheral behavior remain limits. None establishes a deployable image, whole-source completeness, byte-identical bundle completion or hardware correctness. Historical failure diagnostics are preserved alongside later PASS receipts; they must not be silently counted as successful tests.

The work is producing real C/header sources, not only scripts and state documents. The immediate remaining boundaries are installation/integration of the independently tested addons and the classifier floating-point flags, followed by remaining transition functions. No active campaign plan or gate was changed by this scan.
