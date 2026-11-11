# Battery configuration saved-word frame repair

The three battery-configuration getters in `native_battery_configuration.c`
now use explicit saved-R3 frame bridges and C extraction helpers. The previous
compiled getters passed a buffer at entry SP-12; stock passes its saved-R3
word at SP-8. Before/after execution confirms this mismatch for all three
entries. The new bridges retain SP-8 and restore the complete modified word
to R3. No zero initialization or default record replaces the incoming seed.

REA analysis confirms the stock extraction widths and addresses:
`r1_batcfg_byte0_get` at `0x7bb44` reads a byte at offset 0;
`r1_batcfg_flag1_get` at `0x7bb5c` reads an unsigned halfword at offset 2
and returns whether it is nonzero; `r1_batcfg_word1_signed_get` at `0x7bb7c`
reads a signed halfword at offset 2. All call the cached-class reader for
four bytes and ignore its status. The C helpers preserve those access widths
and the signed result. Each bridge is 10 bytes; the current C bodies are
28, 34 and 30 bytes, respectively. Stock bodies are 20, 26 and 20 bytes.

The ignored `build/goal-r1-batcfg-frame/verify.py` probe passes 6,624
stock-versus-C cases. Coverage includes every seed-byte value at each word
position, all partial-fill masks, non-writing reads, full-width read statuses,
signed boundaries and live handle-cell changes. Checks include native buffer
address, handle reads, exact extraction width/order, R0/R3, callee-saved
registers, SP, interrupt masks and callback alignment. Its before-image probe
records all three SP-12 mismatches independently of the repaired code.

An additional 315 comparisons in `class_mismatch.py` execute the actual native
and C cached-class readers with payload sizes other than four. They verify
that rejection reads only the size field, reaches neither port callbacks nor
memory-copy providers, and leaves the getter to extract its incoming seed.
The combined total is 6,939 passing cases. Cached-class successful reads and
flash behavior are outside this integration check.

All 562 R1 units compile without failures or duplicate strong symbols; the
other 561 source units and the manifest are unchanged. Imports remain 227
application and 34 bootloader. Exact source, manifest, native spans, REA,
before-image and probe bindings are in
[the machine-readable review](batcfg-c-frame-review.json).

The C helpers add callback stack depth below the preserved word. Physical
battery behavior, complete flag/fault equivalence, final linking, provider
qualification and byte identity remain unproven. The handle cell at
`0x20007df8` remains an unresolved dependency; this change invents no cold
value. No G2 workflow gates or source-plan selections change.
