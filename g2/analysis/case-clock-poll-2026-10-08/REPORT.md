# Case voltage scaling and regulator-ready polling

Function0x08005048..0x08005086 (62 bytes), historically `case_configure_mode_wait`, is behaviorally consistent with public `HAL_PWREx_ControlVoltageScaling`, not clock-ready polling. Independent `voltage_scaling.c/.h` preserves its raw ABI. Standalone ELF SHA `6175c369d733696ade21cd0f8b74caa54a12f9875c403fbb01f0d9dd99ec5e4f`; no accepted checkpoint or firmware was changed.

Pseudocode: PWR CR1=(oldCR1 & ~0x600)|rawScale. Only scale exactly0x200 computes budget=((SystemCoreClock*6) modulo2^32)/1000000+1 and polls PWR SR2 bit0x400. While busy, return3 if budget already zero, otherwise decrement and repeat. Return0 when ready, or immediately for other scale arguments. PWR base40007000, SR2+14hex, clock global20000124. Actual stock44-byte divide helper0x08000160 executes; native C supplies an independent iterative divide implementation with no helper stub.

A busy status can be observed budget+1 times before timeout; clearing on the next poll after budget decrements to zero still returns success. Raw overflow multiplication is preserved. Malformed scale values and implausible clock values are callee tests, not valid application recommendations. Flags unrelated to VOSF and CR1 fields outside0x600 are preserved subject to the raw scale OR.

Pinned STM32G0 HAL candidate `a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9` power-extension source, source hash and BSD license are included. It uses the same voltage scaling mask, scale1 condition and budget formula; exact producing version/compiled attribution is unproven. The public source describes six microseconds as intent. **No physical delay duration is verified**: tests inject VOSF changes by read count.

Fresh validation: **840** actual stock/source comparisons across scale values, initialCR1, clock values, PRIMASK0/1 and never-ready/immediate/last-retry/one-too-late transitions. Ordered CR1 writes, busy-read values, return, SP and PRIMASK compare. Two semantic mutants (omit+1, wrongbusybit) are rejected. No clock oscillator, voltage transition, interrupt or physical wake was simulated as real hardware.

Application0x0800b600 invokes this with0x200 before system-clock and clock-path configuration, and is called after STOP returns. This supports a static voltage-before-clock restore dependency. Whole wake/clock correctness needs actual provider bodies/state and peripheral trace; this isolated helper does not establish it. Continued case-clock configuration analysis remains actionable; this is not source-by-source global exhaustion.
