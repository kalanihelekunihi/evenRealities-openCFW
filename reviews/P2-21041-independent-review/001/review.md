# P2-21041 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F204..0x47F294 (144-byte prefix); instruction/reference outputs match candidate. Reads of record bytes 0, 1, and 3 are repeated independently. The two masks R6 and SP4 are accumulated from separate byte observations, preserving possible changes between reads. A later fresh byte-3==3 guard plus fresh word mask comparison conditionally performs a separate word read-modify-write setting bit 0. The prefix ends at F294 with the 40-byte frame active; no return behavior is claimed.
