# R1 ADT history sample and timeout in C

`native_wear_adt_data.c` supplies sample `0x3ce1c` and timeout `0x4c6cc` as ordinary
C. The [review receipt](adt-data-c-review.json) binds REA stock bytes, production
hashes, differential checks, initialization, qualification and the locked hybrid.

The sample callback ignores context and length. A nonzero previous count causes
the word at history + previous*4 - 4 to be saved in the existing count word before
the new payload count is read. The new count byte is stored to the existing active
field. A nonzero count copies count*4 bytes from payload+4 using the canonical C
native-memory-move wrapper and unchanged upstream memmove/memcpy. Neither old nor
new count is capped. Copies can cross the nominal history prefix and overwrite
adjacent control fields, including active and count. Input aliases and overlap
remain observable in the same order. Null input faults after the previous-history
update. Timeout forwards directly to the existing C ADT teardown.

Only the 20-byte history prefix at `0x2001e454` is newly owned. Native RW/ZI
handlers execute on poison with guards and an independent RW decoder agrees it
starts at zero. Active and count retain their existing definitions. ADT registration
now declares the established three-word sample arguments; its object is unchanged.
Final source-only placement remains unproven.

The fixture passes 1,356 paired stock/C cases executing the actual memory-move
wrapper, upstream memmove/memcpy and ADT teardown. Cases cover previous and incoming
counts 0/1/5/6/7/255, unaligned/overlapping payloads and aliases into control fields,
ignored length extremes, null input, timeout handle boundaries, provider mutations
and interrupt masks. It compares public memory, control write widths before copying,
move/provider arguments and logical faults, and checks preserved registers/SP on
normal returns plus masks and FPSCR. Internal memcpy access patterns are excluded.
Six compiled defects are rejected: count capping, wrong copy size, wrong previous
word, wrong source offset, null guard and lost timeout. Unregister/release remain
modeled. Void R0, fault PC, caller-clobbered registers, APSR and private stack
residue are excluded. Physical/concurrent behavior remains unverified.

All 644 units compile and both relocatable compositions pass without duplicate
strong symbols. All 643 earlier objects remain unchanged. Both ADT callback imports
are resolved without new imports, leaving application/bootloader imports at 172/34.
Manifest validation passes. Sample has a 36-byte executable span and remains a
behavior candidate. Timeout qualifies as an exact four-byte branch to the stock
teardown address. A fresh hybrid matches the locked application before canonical
promotion of those four bytes. The plan now contains 4,345 source-built bytes,
641,815 executable pull-through and 248 resource bytes. Complete source-only linking
and firmware hardware validation remain unfinished.
