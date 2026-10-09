# Authentic SysLib delay linkage

Both unchanged public delay wrappers now match the complete stock extents:
`Cy_SysLib_Delay` `[0xA2F0,0xA324)` 52 bytes and `Cy_SysLib_DelayUs`
`[0xA324,0xA338)` 20 bytes. Three original BL instructions target the
authentic DelayCycles assembly at `0x4480`. Its matching 32-byte object is
reused and not counted again. Two selected candidates/72 new bytes await review.

Actual PC-relative stock references and zero-addend source ABS32 relocations
bind `cy_delay32kMs=0x2000086C`, `cy_delayFreqMhz=0x20000870`, and
`cy_delayFreqKhz=0x20000874`. No initial global values were invented. The
microsecond helper reads the MHz coefficient as a byte; the millisecond
wrapper reads its coefficients as words. Both use low-32-bit multiplication.

```c
void delay_ms(uint32_t ms) {
    while (ms > 32768u) {
        delay_cycles(cy_delay32kMs);
        ms -= 32768u;
    }
    delay_cycles(ms * cy_delayFreqKhz);
}
void delay_us(uint16_t us) {
    delay_cycles((uint32_t)us * cy_delayFreqMhz);
}
```

The `ms == 32768` boundary uses the multiplication path. These names describe
the authentic source contract, not verified elapsed duration: runtime clock
configuration and coefficient values remain unproven here. Source flags and
objects are unchanged; no patched bytes, guessed call targets, firmware/device
change or live-timing claim. `results.json` preserves original references,
relocations and hashes; `link.py` reproduces the comparator.
