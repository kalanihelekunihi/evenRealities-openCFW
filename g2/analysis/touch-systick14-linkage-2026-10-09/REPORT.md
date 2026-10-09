# SysTick callback and initialization linkage

Three unchanged authentic public-source bodies match the complete stock spans:
ServiceCallbacks `[0xA5F4,0xA620)` 44 bytes; Init `[0xA650,0xA6A8)` 88 bytes;
SetCallback `[0xA6A8,0xA6C0)` 24 bytes. These 156 new bytes await independent
review. The already reviewed 48 enable/clock bytes are reused, not recounted.

Source symbol and original literal references establish a five-pointer callback
array at `0x20000F40` (20 bytes), represented as NOLOAD in the comparator.
The initializer zeros five slots, stores the service handler at RAM vector
offset `0x3C` (SysTick slot 15), selects clock source, writes the low 24 bits of
reload, clears current count, and enables interrupt and counter. Assertions
guard reload < `0x1000000`; no assertion continuation is treated as normal.

Service reads the control register and invokes each non-null callback only
when COUNTFLAG bit16 is set. It reads slots as it progresses, rather than
snapshotting the whole array. SetCallback accepts indexes0–4, replaces the
pointer and returns the old pointer; out-of-range returns null without a write.

```c
handler set_callback(uint32_t index, handler replacement) {
    if (index > 4) return NULL;
    handler previous = callbacks[index];
    callbacks[index] = replacement;
    return previous;
}
void service(void) {
    if (!(CTRL & (1u << 16))) return;
    for (unsigned i = 0; i < 5; ++i)
        if (callbacks[i]) callbacks[i]();
}
```

This is source/byte and interface evidence, not timer execution, thread safety,
callback reentrancy validation, interrupt delivery or initialized-memory proof.
`results.json` records original calls/literals, object relocations and hashes.
No firmware/Git/shared-state/device mutations.
