# RTC alarm configuration lookup order

`board/native_rtc_device.c` now shares an explicitly ordered name comparison
between calendar write and alarm callback binding. It loads the caller name
before the record name through volatile views, matching stock `0x563f8` and
`0x56444`. Callback publication also uses a volatile record view. These changes
remain ordinary C and introduce no assembly bridge.

All 1,128 stock/C comparisons pass. Cases cover opened values without adding
an opened guard, name match/mismatch, null/nonzero/full-width callback words,
controlled name mutation between lookup reads, and calendar sources from
44 bytes before through 44 bytes after the destination, plus separate storage.
Actual stock memory move and the current C adapter with pinned musl memory
providers execute. No copy stub replaces overlap handling.

Checks compare status, exact ordered lookup reads and strcmp arguments,
complete controlled record/neighbor bytes, source storage, R4-R11, SP, interrupt
masks and strcmp call alignment. Both functions reproduce the old-source
counterexample: stock and corrected C use the original caller name and return
zero; old C observes the changed name and returns 2. This is a controlled
ordering discrepancy, not evidence of production race frequency.

Other preexisting device-function bodies and normalized relocations remain
unchanged. All 562 R1 units compile without failures or duplicate strong
symbols; imports remain 211 application / 34 bootloader, the other 561 units
are unchanged and source checks pass. strcmp is modeled. Memory-copy byte
results do not establish identical access widths or fault behavior. Physical
RTC operation, concurrency, byte qualification and complete source-only firmware
remain unproven. Source-plan selections and G2 gates are unchanged. Exact
bindings are in the [machine-readable review](rtc-c-alarm-order-review.json).
