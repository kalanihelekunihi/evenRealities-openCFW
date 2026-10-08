# ADC profile save/restore and apply

Locked bootloader SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5. Reconstructed `g2/components/bootloader/initializer_callbacks/adc_profile.c/h`: transfer42f020..42f14e302 bytes and apply42ea68..42eaf6142 bytes. [650 comparisons](../adc-profile-ff5313.json) PASS/all444 bytes visited; [ownership](../adc-profile-source-ownership-ff5313.json), [disassembly](original-disassembly.txt). Tested image ff53136b29001e2a88deeb93b968bb69fcfe56bcaea576cdf57bc201fbed7911. Full startup/reboot status is separately recorded in the current exact-image report; leaf PASS alone is not seven-case PASS.

## Transfer semantics

Operation and save_restore arguments truncate to8 bits. Invalid context returns2; its module word is read before null/magic guard. Unsupported operation returns6. Context+0xc is a saved-validbyte; config shadow+0x10, eight slot words+0x14..0x30, timer+0x34, window upper/lower+0x38/+0x3c, interrupt enable+0x40. The72-byte context fits these words and prior initialization metadata. Reusable layouts remain faithful to this private binary ABI, not unmodified SDK enum-size assumptions.

```c
if (operation == 0) {
    if (restore && !saved_valid) return 7;
    power_enter(15);                  // status ignored
    if (!restore) return 0;
    status = clock_request(4,15);
    if (status) return status;        // no implicit rollback
    restore(slot[0..7], timer, window_upper, window_lower);
    interrupt_enable = 0;
    adc_config = saved_config & ~1;
    adc_config = (reload(adc_config) & ~1) | (reload_saved_byte & 1);
    interrupt_enable = saved_interrupt_enable;
    saved_valid = 0;
    return 0;
}
if (operation == 1 || operation == 2) {
    if (save) {
        snapshot(slot[0..7], timer, window_upper, window_lower, interrupt_enable);
        saved_config = adc_config;
        saved_valid = 1;
    }
    clock_release(4,15);               // status ignored
    power_leave(15);                  // status ignored
    return 0;
}
```

Snapshot does not itself stop a timer, acknowledge IRQs or drain FIFO/callbacks. Operation1/2 are identical here; no extra behavior is inferred from their names. Restore programs ADC-enablebit0 last with two config writes, then interrupt enable; this ordering is preserved. With restore requested and clock request rejected, saved_valid remains set, no ADC registers restored, and a prior power-control request can remain set. Tests confirm these effects and save→restore register round trips. Stock startup invokes operation0,arg0 before setup and operation2,arg0 after deactivation; it does not exercise restoring a saved profile.

## Apply semantics

First profile byte must be clock selector2; other values return6 before clock request. No argument-null guard is added. Native clock_request(4,15) status is propagated; nonzero leaves ADC CFG unchanged. Success rereads seven bytes and packs CFG fields: clock bits24..26, repeat trigger20, polarity19, trigger16..18, forced bit12, clock mode4, power mode3, repeat2. Bit0 is cleared, leaving activation as a separate entry. Each byte is masked to its field width. Stock profile bytes02010007010001 produce02171014 when accepted; physical frequency/timing is not inferred.

## Required native power/clock children

41bf84 power enter and41c17a leave were already reconstructed in `platform_control/power_domains.c`; they are reused natively, with descriptor-copy41b8f8, release-needed41c0be, callback/hook dispatch41cd1a/41cd34/41cd4a, critical-save41b8ec, native status-poll41d246/delay41d1c0 and clock request/release/class4 children.

Selector15 uses control40021004 bit2000 and status40021008 bit2000. Enter returns immediately if control alreadyset; otherwise hook begin and callback3 precede an atomic control OR; hook end precedes status poll. Native polling counts five delay(1) calls on persistent mismatch and returns4; even poll success is followed by a status-bit check. Leave clears control bit under critical protection, polls for status mismatch(off), and conditionally invokes callback3; hook end still runs on timeout. These actual user15 paths execute in650 tests. Optional external callback/hook targets return synthetic7; absent resident ROM40 cyclewait is explicitly modeled. Fixed status values exercise success/timeout and are not actual acknowledgements or elapsed-time measurements.

Class4 clock allow0 produces error1; allow1/user state exercises native HFADJ enable/bitmap behavior. Existing clock private callback pointer can contain a stack-local address; comparisons normalize it only after a mapped-stack bounds check. No lifetime, scheduler or hardware safety is implied. Special power selectors20/23/28/29 and nonnull async HFADJ configuration are not credited by this user15 profile.

## Scope and next edge

[Contiguous ADC region map](../adc-region-map-ff5313.json) accounts14 source-mapped functions/2148 instruction-body bytes,24 float literal bytes and2 alignment bytes in42e8d0..42f14e. It does not certify code elsewhere, full bootloader, standalone hardware execution or byte equality. All preceding ADC calibration/zero-count/temperature-bypass regressions run against the same candidate; residentROM/factory, physical FIFO, IRQ/task/callback quiescence boundaries persist.

Next actual startup edge: post-context constructor422ad4 publishes real handles into rows currently supplied by a return stub. Its private4×0x11c-byte pool begins20024400 and new magic01ea9e06 differs from ADC/IOM magic. Closing it must propagate real handles into downstream postconfigure/validate/activate wrappers and explicitly account required children; do not equate that constructor with a working bus or scheduler. See the next-provider note.
