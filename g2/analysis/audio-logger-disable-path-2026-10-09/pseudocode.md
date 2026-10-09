# Stock logger disable path (reconstruction, not decompiler export)

```c
// 0x472C7C..0x472C84; literal at 0x47345C.
void logger_set_sink(uint32_t callback) {
    *(volatile uint32_t *)0x200742F0 = callback;
}
// 0x4C2B30..0x4C2B68; no names/units inferred for children.
void conditional_disable(void) {
    if (*(volatile uint8_t *)0x20074F4E != 1) return;
    if (child_539254() != 0) for (;;) {} // loop 0x4C2B44
    if (child_539304() != 0) for (;;) {} // loop 0x4C2B4E
    logger_set_sink(0);
    child_480F0C(0x1C, *(const uint32_t *)0x78EE3C);
    *(volatile uint8_t *)0x20074F4E = 0;
}
// 0x444684; independently recovered corpus evidence, not exercised here.
void alternate_sink_dispatch(uint32_t unused, void *arg) {
    ((void (*)(void *))*(volatile uint32_t *)0x200742F0)(arg);
}
```

Call chain in current Ghidra corpus: 0x5CDD14 -> 0x4C2AE8 -> 0x4C2B30 -> 0x472C7C. Function 0x5CDD14 includes the product/version initialization call and logger usage later. This is an initialization-associated call chain, not evidence that the flag equals1 during any particular live boot.

No null guard appears in the alternate dispatch's corpus output. Reachability, caller ABI and runtime callback binding are unresolved; do not infer a hardware null-call failure from this alone.
