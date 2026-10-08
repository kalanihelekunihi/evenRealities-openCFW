# P2-20903 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 46 bytes across three frameless entries at 0x47D8CE..0x47D8FC; pinned image/source hashes and tiling match. The first leaf makes one fresh flag-byte read, ANDs with 12 and returns exactly 1 only when both bits2/3 are set, otherwise 0. The next two independent entries each reread the flag byte and return bit4 or bit5 as zero-extended 0/1. No leaf modifies R1-R3 or allocates a frame. The runtime flag pointer comes from the mapped flash literal, but its external RAM contents are not established by the flash artifact.
