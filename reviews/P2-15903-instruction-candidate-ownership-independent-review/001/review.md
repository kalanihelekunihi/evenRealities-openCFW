# P2-15903 independent review

Fresh replay exactly reproduces the candidate ownership partition: 4,908 indexed candidate files, 3,301 merged intervals, and all 33 image partitions. Owner event counts remain valid across each image, and per-image totals match the saved diagnostic. Main flash has 163,016 bytes with candidate instruction evidence, including 80,008 bytes with multiple candidate owners; boot flash has 123,960 and 96,702 respectively.

These are candidate-evidence counts, not code/data classification or semantic coverage. Overlaps and conditional routes remain unresolved, and no-indexed-evidence spans are not proven opaque. Status remains partial and unaccepted.
