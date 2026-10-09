# One-byte deadline0x58FAD2

```c
start=(uint64_t)(uint32_t)kernel_ticks();
deadline=start+(uint64_t)(int64_t)(int32_t)timeout;
now=start;
for (;;) {
    if(deadline<=now)return 0xffffffff;
    if(codec_uart_read(dst,1)==1)return 1;
    osDelay(1); // synthetic tick/arrival boundary in tests
    now=(uint64_t)(uint32_t)kernel_ticks();
}
```

Getter0x58FAC8 calls4490CC then MOVS R1,#0. ASRS R7,R6,#31 at58FAF2 establishes timeout sign extension; ADDS/ADCS form64-bit deadline; unsigned high/low compare58FAFA..58FB02 occurs before drain58FB08. No wrap-normalization is inserted into reconstruction.

Near-wrap startFFFFFFFE timeout5 forms100000003, not3. Zero-extended current32-bit tick cannot equal/exceed this after wrapping, under the modeled tick source. Eight-delay cut is bounded evidence, not a measured hardware hang. Existing response parser57C1FC subtracts ticks and requires separate validation.
