# Independent review 2893

Status: **PASS_SCOPED** (`accepted: false`).

The source and candidate artifact hashes match. The body `[0x42AD40, 0x42ADB8)` hashes to the receipt value; isolated static replay regenerated 39 instructions with complete byte coverage and the literal values in the listing.

I checked the ordered VFP comparisons and conditional branches. They implement category 0 for `[-273, -20)`, category 1 for `[-20, 0)`, category 2 for `[0, 50)`, category 3 for `[50, 1000)`, and category 4 otherwise. The literal words resolve to `0xC3888000` (-273), `0x42480000` (50), and `0x447A0000` (1000); `-20` is the encoded VFP immediate. The path-dependent S1/S2 use and flags are described without claiming a fixed full-register contract.

This is a static map, not dynamic evidence for boundary values, NaNs, infinities, or exception modes. No equivalence shortcut or canonical admission is claimed.
