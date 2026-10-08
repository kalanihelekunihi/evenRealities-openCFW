# Native HAL delay operand calculation

`g2/components/bootloader/platform_startup/delay_math.S` reconstructs locked `41d1c0..41d210` (80 instruction bytes). Original/source differential PASS: **780 cases**, including peripheral mode bits[4:3], large unsigned inputs, saturation/precision boundaries and four FPSCR rounding modes. The resident ROM entry at Thumb `0x41` is a recorded callback, not reconstructed code.

The wrapper converts the unsigned input to float32 and converts it back with five fractional bits (scaled by32). Peripheral register `40021000` bits[4:3] select the calculation: value2 re-converts to float32, multiplies by250.0 and divides by96.0, truncates to unsigned, and subtracts24 if larger; other values subtract15 if larger. At or below the threshold it does not call ROM. For input1, controlled default-rounding tests observe ROM arguments59 in mode2 and17 otherwise. Large conversions can saturate; this differs from the unsigned multiply-by1000 in the outer wrapper41f9d8.

Tests compare S0/S1, FPSCR, return/saved registers, stack and exact ROM arguments. They establish instruction-level operand behavior on the compatible Unicorn core; no ROM internals, elapsed time, silicon clock frequency or physical timing claim. The shared source-image profile now executes this local function and treats only the resident-ROM call as an external boundary.
