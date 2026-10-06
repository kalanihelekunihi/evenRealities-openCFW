# P2-15873 independent review

Before replay, the captured 4,908 instruction-file paths and all 33 image pins matched current inputs. Fresh replay exactly reproduces the saved summary, index, exclusions, and image-pin records: 4,842 files have whole-file candidate matches; one file has two candidate images; 66 files are excluded. Candidate counts are 3,033 Apollo main flash, 1,797 bootloader flash, one each for the decoded Apollo-main and bootloader ITCM, five BLE record-3, and six case flash. The ambiguous file is a 24-byte ITCM range that matches both Apollo images, so per-image counts overlap. Exclusions are 39 no candidate match, 13 missing `bytes`, 7 `bytes` represented as a list, 4 JSON parse errors, 2 unsupported top-level objects, and 1 unsupported block shape.

These are candidate byte matches, not ownership. The ambiguous ITCM remains unresolved, and counts cannot be summed into coverage or used as canonical admission. Status remains partial and unaccepted.
