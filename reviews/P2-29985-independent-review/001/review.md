# Independent review 29985

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-dispatch69-event764-negativeone-helper-frame48-middle-30384-map/001`. Its candidate hashes and locked image hash match the receipt. Independent reassembly verifies the exact interval `[0x4EB092,0x4EB0DC)` as 74 contiguous bytes and 25 Thumb instructions.

Separate query calls gate event764 by bit1 and the later call by bit0 or bit2. The event arguments use fresh PC-relative words, including the narrow loads at `0x4EB328` and `0x4EB32C`, and the specified current SP slots. `MOVS.W R0,#0x0C000000` produces N=Z=C=0 and preserves V. The subsequent modified-immediate `MOVS.W R0,#0xFFFFFFFF` uses byte replication, setting N=1 and Z=0 while preserving C and V; its actual result is passed to `4EAD10`. Literal references match the locked image.

This is bounded partial evidence. The call continuation and branch to `0x4EB1AE` are outside the interval; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.
