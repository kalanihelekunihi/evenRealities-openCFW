# UART group helper pseudocode

```c
// UART domains11..14 only; stock input narrows to8bits.
can_poll(domain) {
    lookup(&d, (uint8_t)domain);
    if ((read(d.enable_register) & 0x1e00) != 0)
        if ((read(d.enable_register) & d.enable_mask) == 0) return 0;
    return 1;
}
pre()  { if (!slot[3]) return 0; return slot[3](); }
post() { if (!slot[4]) return 0; return slot[4](); }
control(action, enable, metadata) {
    if (!slot[1]) return 0;
    return slot[1]((uint8_t)action, (uint8_t)enable, metadata);
}
wait(budget, register, mask, expected, equal) {
    for (;;) {
        matched = (read(register) & mask) == expected;
        if ((uint8_t)equal ? matched : !matched) return 0;
        if (budget-- == 0) return 4;
        delay(1); // synthetic boundary in current fixtures
    }
}
```

slotbase20073270. Predicate uses **enable** register, not shared status register. Wait uses supplied register, here group status40021008. Enable bits and group status are different state axes. Volatile read duplication preserved intentionally, not folded into one snapshot.

Stock interrupt-clear0x58E7E4 writesIEC+44 then readsMIS+40, exactly matching tested source. NULL prevalidation access faults in both. This corrects prior decompiler-based interpretation. No physical read-side-effect inference.
