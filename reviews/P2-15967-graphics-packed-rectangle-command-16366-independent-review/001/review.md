# Independent review 15967

Partial, accepted:false. Fresh replay passed for 80 bytes at 0x522ae0..0x522b30. Preserves parameters in R4-R7, signed-compares width/height against 1 with the IT-GE second compare, returns unchanged on invalid dimensions or null allocation. On success PKHBT packs x/y and wrapped x+width/y+height, writes fields in order, then fresh-loads global object field and ORs bit 1. Stack frame is 24 bytes; pop restores entry context.

Allocator/external-child behavior remains unresolved; no admission or gate change.
