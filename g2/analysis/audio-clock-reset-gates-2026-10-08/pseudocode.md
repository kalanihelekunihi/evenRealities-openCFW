# Clock-mux reset: recovered gates and source-guided active path

Actual function0x44B158..0x44B4F2. Gate/bitmap/epilogue are instruction-tested; active-stage labels below are pinned-source interpretations pending full per-call/register matching and instruction tests.

```c
// Exact instruction-backed outer behavior:
if (!(W(0x4000885C) & 2) && (W(0x40008858) >> 16) == 0x5AF0) {
    if (W(0x40008858) & 0x3F) {
        // Original active recovery starts0x44B1D0; not yet native/tested.
        recover_clock_muxes_source_guided();
    }
}
W(0x40008858) = 0;
W(0x40008858) = (W(0x40008858) & 0xFFFF) | 0x5AF00000;
```

Source-guided stage outline: enable required HFRC_DED/HFRC2/XTAL/external/PLL sources; optionally save GPIO15 and request SIP clock; power PDM0/I2S0/I2S1/AUDADC/USB/USBPHY; flush writes and pulse ADC clock selection; restore mux selection; disable temporary peripherals; revert PLL/GPIO/external/HFRC settings; always clear requests and reinstall signature. Source can guide analysis, but must not substitute for matching stock instructions. Delay/wait readiness, callback return handling and exact peripheral side effects remain open.

Both original stock gate and the bitmap test are recovered directly. Low-six bits are clock-request conditions; source names them AUDADC_CLKGEN_OFF, HFRC_DED, HFRC2, XTAL, EXTCLK, PLL. No frequency/rate units follow from the bitmap itself.
