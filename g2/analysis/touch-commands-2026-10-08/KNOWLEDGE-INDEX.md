# Bounded firmware knowledge index

| Directory | Functions/interface | Validation boundary |
| --- | --- | --- |
| ../dependency-followup-2026-10-08 | Touch FIFO9218..9316; I2Cinit98f4/IRQ9b0c; case wake5094/50a8 | Six FIFO compiled-body matches; I2C synthetic MMIO; earlier real-helper callbacks null |
| ../touch-callback-ownership-2026-10-08 | Callback3700; publish slice3c18..3c36 | Bounded commands0/1/3/9; static-buffer ownership; synthetic descriptor interruption |
| ../case-stop-mode-2026-10-08 | STOP50e8 | Actual register instructions; WFI/WFE controlled wake cuts |
| . | Commands3700..389e; sensor35f4; deferred3a80 | All command branches under bounded sensor counts; reset/EEPROM explicit cuts; actual IRQ composition |
| ../case-clock-poll-2026-10-08 | Voltage scaling5048; divide0160 | Regulator state injected by read count; no physical time |
| ../touch-eeprom-dispatch-2026-10-08 | Write dispatcher8aac; actual simple-mode85d4 direction | Dispatcher provider cuts; stock copy/division with synthetic row callbacks; no physical programming |

Prior directory manifests are preserved. Counts describe individual suites, not additive whole-image coverage or integrated source completeness. These standalone modules are not installed into the accepted 242-object firmware checkpoint.
