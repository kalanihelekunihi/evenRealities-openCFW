# Independent review 3005

**Result:** PASS_SCOPED; `accepted: false`.

Candidate `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-queue-adapters-map-3004/002` pins the original flash image and the three exact body ranges. Receipt hashes for instructions, replay, and pseudocode match. I reran the static verifier into `/tmp/review-3004-isolated`; all 45 original Thumb instructions were decoded across the three contiguous spans. The sole PC-relative literal resolves to `0x40050000`.

The initialization adapter's stack descriptor agrees with the push and stores: its first two words are incoming R1 shifted right one and incoming R2; the third word's low byte is set to one while upper bytes remain from the saved R2 word; the fourth word remains incoming R3. The status-zero path writes `0x100` at record+0x20. The enable adapter guards record+0x24, uses fresh index reads around node lookup/publication, and calls `0x427878`; the disable adapter calls `0x4278C8`. Both child return values remain in R0 while the pop restores incoming R7 into R1.

This is a static contract with child contracts unresolved; it does not establish node validity, side effects, aliasing, physical MMIO behavior, or caller/global ownership.
