# Reconstructed logger providers

These are readable behavioral reconstructions, not original source or a compiled firmware module.

```c
// 0x539254: ITM control disable. poll/delay/clock providers remain boundaries.
uint32_t trace_disable(void) {
    trace_wait_idle(); // 0x53928C; return ignored by caller
    *(volatile uint32_t *)0xE0000E80 &= ~0x10u; // ITM TCR SWOENA
    *(volatile uint32_t *)0xE0000E80 &= ~1u;    // ITM TCR ITMENA
    uint32_t status = poll(1000, (void *)0xE0000E80, 0, 0);
    if (status == 0) {
        status = shared_clock_release(); // 0x4D3F78
        if (status == 3) status = 0;
    }
    return status;
}
// 0x53928C
uint32_t trace_wait_idle(void) {
    if (!trace_port_ready() || !trace_not_busy()) return 4;
    delay(500); // call 0x4807A0; units not established here
    return 0;
}
// 0x5392F8 ->0x5392D4
bool trace_port_ready(void) { return poll(1000,(void *)0xE0000000,3,1)==0; }
// 0x5392AE
bool trace_not_busy(void) { return poll(1000,(void *)0xE0000E80,0x800000,0)==0; }
// 0x539304
uint32_t trace_ref_release(void) {
    uint32_t saved_primask = read_primask(); // 0x473940
    disable_irq();
    volatile uint8_t *refs = (void *)0x20074F7E;
    if (*refs != 0) --*refs;
    uint32_t status;
    if (*refs != 0) status=3;
    else {
        *(volatile uint8_t *)0x20074F7D=0;
        status=shared_clock_release();
        if (status==3) status=0;
    }
    write_primask(saved_primask); // original MSR, not corpus inferred privilege helper
    return status;
}
```

The enclosing0x4C2B30 treats any nonzero result as fatal, even the retained-reference status3 of trace_ref_release. This result is confined to synthetic counter fixtures; it does not prove a reachable stock failure.

Actual scatter record at0x75D3C8 resolves relative handler to0x5FA01F (Thumb). Fields at0x75D3CC are length0x70AF0 and destination0x20004558. Handler0x5FA01E zeroes this span, then reads the next length. The validation stops at the next record and does not execute the decompressor or complete startup.
