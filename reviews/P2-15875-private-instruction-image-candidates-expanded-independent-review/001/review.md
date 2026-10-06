# P2-15875 independent review

The captured 4,908 instruction-file paths still match the current scan, and all 33 image pins match. Fresh replay exactly reproduces the saved outputs: 4,860 candidate files, one ambiguous file, and 48 exclusions. Of the candidate matches, 4,844 use `as_recorded` bytes and 17 use the explicitly labeled `each_halfword_byte_swapped` hypothesis. The transformation remains explicit in each record; bytes are not silently normalized.

Per-image candidate counts include 3,033 Apollo main flash, 1,797 bootloader flash, one decoded ITCM candidate for each image, 22 BLE record-3 candidates, and 7 case flash candidates. The 24-byte decoded ITCM map remains ambiguous between Apollo main and bootloader. The 48 exclusions are 43 with no whole-file candidate match, 4 JSON parse errors, and 1 unsupported top-level object.

Candidate counts overlap revisions/images and do not establish ownership, ISA validity, semantic coverage, or canonical admission. Status remains partial and unaccepted.
