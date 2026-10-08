# P2-20807 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed; image SHA-256 and source/fresh receipt hashes verified.

188B replay passed. Ten signed-count iterations with stride200; each tests fresh byte47 then byte48, increments global counter only after both nonzero, stores then independently reloads it. Logger path captures word196/full index; mask path independently reloads word196 into SP0, overwriting saved R0 even if logger skipped. Epilogue returns last SP0 writer; saved slots R1/R2/R3 may also be overwritten by logger.

No stable-global assumption or whole-firmware coverage is inferred. No source or gate files changed.
