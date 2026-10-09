# UART11..14 enclosing pseudocode and ownership

```c
on(domain) {
    descriptor = lookup((uint8_t)domain);
    if (read(enable_reg) & per_device_bit) return 0;
    pre(); group_control(3,1,&shared_mask); // returns ignored
    old = save_irq(); enable_reg |= per_device_bit; restore_irq(old);
    post(); // return ignored
    error = wait(5,status_reg,shared_mask,shared_mask,EQUAL);
    if (error) return error; // command remains set
    return (read(status_reg) & shared_mask) ? 0 : 1;
}
off(domain) {
    descriptor = lookup((uint8_t)domain);
    if (!(read(enable_reg) & per_device_bit)) return 0;
    pre(); old = save_irq(); enable_reg &= ~per_device_bit; restore_irq(old);
    error=0;
    if (can_poll_group(domain)) { // selected bit now clear
        error=wait(5,status_reg,shared_mask,shared_mask,NOT_EQUAL);
        if (!error) group_control(3,0,&shared_mask);
    }
    post(); return error; // no rollback on timeout
}
```

per-device bits200/400/800/1000; enable40021004; status40021008/sharedmask1E00. Device command clear with sibling command set skips group wait. Last-device wait exits on any partial group status; not exclusively zero. No physical acknowledgement contract is invented.

Registrar selection uses cached trim-version fetched from INFO1 by47EF38. StartupFFFFFFFF is a sentinel, not the installed family. PCM2.0 pre/post own postponed/pending flags as described in REPORT. Group action3 is a no-op in PCM2.0, but materially changes request state in newer families, so callback variants cannot be silently swapped.

Interrupt-clear accessesIEC44 thenMIS40 in both stock/source. NULL unmapped access precedes validation in both. Authoritative additive correction is in INDEX.md.
