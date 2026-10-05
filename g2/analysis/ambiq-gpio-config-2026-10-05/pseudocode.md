# Recovered GPIO configuration behavior

Reconstruction for explanation; the compiled implementation retains the pinned upstream bodies. Locked Apollo payload base0x438000; addresses below are runtime addresses.

```c
// 0x480eee,30 bytes
uint32_t gpio_config_get(uint32_t pin, uint32_t *out) {
    if (pin >= 224) return 5;
    if (out == NULL) return 6;
    *out = MMIO32(0x40010000 + 4*pin);
    return 0;
}

// 0x480f0c,126 bytes; lookup tables 0x768ba8 / 0x768bc4
uint32_t gpio_config_set(uint32_t pin, uint32_t cfg) {
    if (pin >= 224) return 5;
    unsigned bank = pin / 32, bit = pin % 32;
    if (extended_drive_bitmap[bank] & (1u << bit)) {
        unsigned pull = (cfg >> 13) & 7;
        if (pull != 0 && pull != 1 && pull != 6) return 7;
    } else {
        unsigned drive_low2 = (cfg >> 10) & 3;
        if (drive_low2 >= 2 &&
            !(additional_drive_bitmap[bank] & (1u << bit))) return 7;
    }
    unsigned prior = read_primask_then_cpsid_i(); // 0x473940
    MMIO32(0x40010400) = 0x73;
    MMIO32(0x40010000 + 4*pin) = cfg;
    MMIO32(0x40010400) = 0;
    restore_primask(prior);
    return 0;
}
```

No internal unknown branch remains within these two bodies. The exact physical interpretation of every raw bit/function selection and logical index is outside this bounded contract. A full pad function-selection lookup, alternate GPIO state writes, clock enable and board reset/power timing are not provided.

Consumers and data provenance:

- Radio shutdown0x4b49ce calls0x52dd7c; that helper first calls state-write for pin93, then configures pin138 at0x52dd8e with raw0x3 from0x78ee48. The earlier state-write is not implemented here, so no complete radio shutdown claim.
- Display helper0x592c78 (existing inferred `jbd4010_configure_gpio_pins`) obtains revision state through0x50938e, configures pin143 for revision<3, pin128 for revision<4, and pin142 unconditionally. All use raw0x183 from0x78ee40. Full power consumers0x593200/0x59328c and electrical effects are not executed here.
- Flash-associated function0x46fb0c calls getter at0x46fd10 with pin103 and a local output pointer. This demonstrates actual snapshot use before subsequent MSPI work; restoration/lifetime for that saved configuration remains next-stage work.

All caller/body/literal hashes and direct call sites are retained in `original/evidence.json`; stock consumer labels retain their existing confidence level. Static callers do not add executed-source coverage.
