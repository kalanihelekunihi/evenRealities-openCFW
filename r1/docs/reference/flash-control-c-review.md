# R1 FlashDB control interface in C

`runtime/native_flashdb_control.c` now implements the complete control routine
`r1_health_sync_provider_00063694` in C, replacing its inline assembly dispatch,
field operations, diagnostics and assertion loops. REA/Ghidra confirms the stock
control flow at `0x63694`. The reported body is noncontiguous (242 instruction
bytes across a 254-byte envelope); the 12-byte TBB table is separate data. This
is local evidence, not corpus coverage or byte qualification.

The implementation retains the native routes:

- Selectors 0 and 11 require an initialization byte of zero before writing the
  size word at +12 or a byte at +26. Selector 4 requires exactly byte value one
  before writing byte +92; other nonzero values do not satisfy that test.
- Selectors 1, 5 and 6 read the word/byte at +12, +92 or +80 and copy it to the
  supplied output. Selectors 2 and 3 store the argument pointer at +28 or +32.
- Selector 9 prints the unsupported-file-mode diagnostic and returns the final
  printer result. Selectors 7, 8, 10 and values at least 12 are native no-ops.
- Returning routes preserve their native R0 value, including the database
  pointer on no-op/pointer-store routes and the transferred value on getters
  and value setters. Assertion routes retain their diagnostic sequence and
  nonreturning loop. Null database processing still faults in the path helper
  after the first diagnostic; no new null fallback is introduced.

Packed volatile word accesses retain unaligned and aliased database/argument
behavior. The prefix calls the actual selected C database-path helper and reads
name/mode state at the native points. No new buffer or default state is added.

The normal object passes 2,568 paired stock/C emulator cases. They cover every
selector from 0 through 13 plus `UINT32_MAX`, initialization bytes 0/1/2/0x80,
mode bytes, unaligned views, argument aliases, null arguments/database, native
return values, ordered byte/word reads and writes, diagnostic text, assertion
loops, guards, return SP, saved registers and interrupt masks. Printer callbacks
can clobber caller registers and mutate database name/mode state between logs;
subsequent accesses still agree. Each invocation resets XPSR/IT state. Two
negative controls (accepting any nonzero initialization byte and writing selector
2's pointer to the wrong slot) are rejected. The diagnostic printer is modeled;
physical flash, asynchronous calls and arbitrary corrupted pointers are excluded.
Private stack traffic and caller-clobbered register/flag outcomes are not claimed.

All 573 R1 units compile with no failures or duplicate strong symbols. Imports
remain 176 for the application and 34 for the bootloader. The manifest and all
other object hashes are unchanged. Five official qualification profiles compile,
but no region qualifies. The source plan remains unchanged. A fresh hybrid
application still equals the locked 646,408-byte stock image: 3,881 source-built
bytes, 642,279 binary pull-through bytes and 248 resource bytes. These stored-byte
provenance counts do not prove executable-C coverage or full source completeness.

## Retained sector-reader dependency

The later [sector control extraction](sector-control-c-review.md) addresses the
frame hazard below by protecting the nested view and retaining native provider
call positions. The following records the earlier, unretained whole-kernel
attempt; the new extraction remains partial.

A sector-reader C candidate was investigated and not retained. The existing
sector reader reserves its 104-byte scratch span at caller SP-128. When it calls
the log reader at that stack position, the latter reserves a further 48 bytes,
placing its separate 32-byte raw read view at caller SP-176. Partial/non-writing
reads consume existing bytes in both views. An ordinary C kernel inserted between
those calls changes the nested stack address and can overwrite those existing
bytes. Preserving only the sector's outer scratch span therefore does not prove
the stock contract. The next extraction must account for the nested read frame
and intervening call effects, rather than adding an initialized C default buffer.
The sector source was restored byte-for-byte to its pre-investigation state;
its current normal object matches the prior report. The candidate remains only
under ignored `build/goal-r1-flash-sector-c/` and does not enter the source plan.

No G2 implementation or workflow gate changed. Hashes and build paths are in
[flash-control-c-review.json](flash-control-c-review.json).
