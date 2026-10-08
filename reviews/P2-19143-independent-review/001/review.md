# Independent review: P2-19143

Status: partial / unaccepted. No source or gate changes.

Fresh replay of locked bytes and compare exact: instructions and references match; slice 0x469CE4..0x469D24 (64 bytes).

The loop freshly reads the index before the source-byte read and again after the destination store before advancing/storing the index; count is also freshly read and decremented. SDIV/MLS computes the observed wrapped-index remainder. The exit zero-extends the selected low16 length, while preceding error/empty routes retain their stated values into the shared POP. Alias-sensitive order is preserved.
