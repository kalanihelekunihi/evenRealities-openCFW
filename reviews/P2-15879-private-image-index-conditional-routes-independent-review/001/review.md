# P2-15879 independent review

The captured 4,908-file snapshot was replayed from its saved path list and exactly reproduces the saved summary, index, exclusions, image pins, and conditional-route models. It has 4,903 candidate files, one ambiguous file, and five exclusions. Candidate counts include 3,033 Apollo-main flash, 1,797 bootloader flash, one decoded ITCM candidate each for main and bootloader, 22 BLE record-3, 7 case flash, and 22/21 Binh-A stage2 SRAM/XIP candidates.

The current scan has four additions, all `format-repair-16286/instructions.json` files. Its separate replay reports 4,912 files scanned and 4,907 candidates, including 3,037 Apollo-main candidates. The original 16284 snapshot was not overwritten. The conditional models preserve their expected spans, guards, and external references; this index does not claim that any guard was satisfied.

These candidate matches do not establish ownership, ISA validity, semantic correctness, or canonical coverage. Counts overlap across images and revisions. Status remains partial and unaccepted.
