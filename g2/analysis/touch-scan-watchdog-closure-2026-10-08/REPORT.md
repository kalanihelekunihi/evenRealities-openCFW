# Scan watchdog arithmetic and completion polling

New independent source ../../components/touch/scan_watchdog_offline/watchdog.c closes7288 (GetScanWatchdogTime) and6980 (WaitEndOfCpuScan). Original instructions and locked provenance are recorded beside this report. Selected source executes software division via ARM libgcc; original division helpera6c0 executes unmodified.

## Watchdog configuration

7288 ignores slot argument in this selected build. Widgetcontextu16+14 is the sense divider; byte+33 low2 selects clock source. Internalcontext+48/+50 are coarse-init terms; byte+83 adds offset; +62/+66 are PRS pro/epilogue delay terms, otherwise+64/+68. Add `(divider>>2)*(pro+epi)`; add `divider*(internalbyte77+widgetu16+44)`. Double total for source2, multiply widgetbyte132 chopcycles, divide46, then multiply5. All intermediates retain unsigned32 wrap. This explains a computed software watchdog budget, not an observed acquisition duration.

6980 computes `iterations=(watchdog*(cpuClkHz/1000000))/5` with unsigned32 product, then polls HW.INTR atHW+0x100 bit0x100. It reads before testing budgetzero; while incomplete and budgetpositive it decrements. It returns remainingbudget, NOT a boolean status. Atzero budget a simultaneous completion still returnszero, so caller7bc0 treats that outcome as timeout. It always writes0xc1011111 to INTR and reads back, acknowledging ALL pending interrupt classes selected by the mask, not just scanbit. Native source uses volatile MMIO.

Validation:144 complete original/native watchdog comparisons covering divider0..65535, everyclocklow2 value, chop0/1/255 and normal/extreme configuration terms;100 complete original/native wait comparisons covering initialcompletion, delayedcompletion, budget exhaustion, zero/sub-MHz/integer-MHz configuredCPUclock and zero/nonzero watchdog. Read counts, maskwrites and returnbudget match. No function-return stubs. MMIO completion and write-to-clear behavior are synthetic fixtures; no physical clock, IRQ concurrency, analog acquisition or full peripheral model is verified.

## Dependency boundary

These two CPU helpers narrow the saturated-scan7bc0 boundary. Hardware mode switch6ac0, frame loading6928→PDL9178 and inline saturation-frame construction in7bc0 remain actionable static work. This batch does not mark those as exhausted or claim full ADC/scanner closure. No production firmware, index, commit, shared campaign or device writes.
