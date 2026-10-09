# SysTick literal extents and preserved audio rescan

Two preselected authentic PDL/GNU14.2.1 object sections match the stock touch
image over their entire 24-byte extents, with no relocations or source changes.
These are two new review-pending candidates, 48 bytes, within the existing
54-entry census. The reviewed aggregate remains 23 functions/2,320 bytes.
There are 29 other remaining entries plus these two pending candidates.

`Cy_SysTick_Enable` at `[0xA620,0xA638)` comprises 20 instruction bytes and
the four-byte literal `0xE000E010`. It performs two separate volatile
read-modify-writes: set control bit 1 (interrupt enable), then set bit 0
(counter enable). Combining the writes would change the observed sequence.

`Cy_SysTick_SetClockSource` at `[0xA638,0xA650)` comprises 18 instruction
bytes, two alignment bytes `c046`, and the same four-byte control-register
literal. It preserves every other bit and writes bit 2 from argument bit 0.
This establishes register manipulation, not the physical clock frequency or
the units of RTOS delays. Exact original PC-relative references, full-span
hashes, object identity and instructions are in `results.json`; `verify.py`
repeats the comparison using existing source-built objects.

Equivalent readable pseudocode (analysis only):

```c
void enable(void) {
    CTRL = CTRL | 2u;
    CTRL = CTRL | 1u;
}
void set_clock_source(uint32_t source) {
    CTRL = (CTRL & ~4u) | ((source << 2) & 4u);
}
```

The requested audio rescan freshly reproduced all saved results exactly:
704 block-insertion cases, 360 block/wake/resumed-return cases, and 245 codec
lifecycle/HAL cases. Captures are isolated in
`/tmp/opencfw-readonly-rescan-20261009/comparison.json`; original result files
and manifests were not overwritten. Sandbox Unicorn failed even on an ARM
NOP; an approved execution outside the sandbox passed the NOP and all cases.

Codec retention and failed-close findings stand: close/reopen preserves
retained RX bytes; invalid-handle close clears channel-active before failing
but retains codec-open. Peripheral-domain and clock return injections do not
prove physical failure because the recovered HAL ignores those returns.
Notification compositions explicitly order wake or timeout and restore the
saved continuation; no exception delivery or real device schedule is asserted.
The bounded audio/UART/power static ledger remains exhausted at those recorded
boundaries. Whole-firmware source and pseudocode coverage remain incomplete.

A read-only preservation check confirmed 2,884 prior sealed entries, all 110
inputs and all four checkpoints. Observed index SHA-256 remained
`7f02499d1aa1e24c2f27981948dcf777f84e0e7866977c2a4c9c911344aa12fd`.
It differs from the historical scan baseline as previously documented; no
index change occurred during this work. No Git, production, device or shared
campaign-state mutation was performed. Existing system-interface report
totals are stale; use the canonical 54 = 23 reviewed + 31 remaining ledger,
with these two now awaiting independent review rather than counted reviewed.
