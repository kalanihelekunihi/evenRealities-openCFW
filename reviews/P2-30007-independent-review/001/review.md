# Independent review 30007

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-object-input-eight-literals-30406-map/001`. Inventory and report hashes match its receipt; the locked image hash agrees. The exact `[0x4EB31C,0x4EB33C)` span contains eight consecutive words (32 bytes). Each listed byte sequence and little-endian value matches the locked image. All three contributor map hashes are valid; four maps were included in the scan. Independently matching the consumer records to decoded PC-relative LDR operands confirms all 11 word-to-load references, including the shared consumers at `0x4EB324`, `0x4EB328`, and `0x4EB32C`.

The inventory is bounded to these words and the listed consumer maps. Literal values are not treated as pointee contents; this does not establish global consumer or data completeness, source completeness, freeze, or byte equality. The following entry at `0x4EB33C` is outside the inventory.
