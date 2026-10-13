# UART power/configuration offline comparison source

Selected unchanged pinned Apollo510 SDK bodies with retained BSD3 notice; stock284Bhandle/16Bconfig and register adapters. [Evidence and limitations](../../../analysis/audio-uart-power-config-2026-10-09/REPORT.md), [pseudocode](../../../analysis/audio-uart-power-config-2026-10-09/pseudocode.md).

This is an offline knowledge/comparison artifact, not a production driver. interrupt-clear differs in an extra MIS read and NULL prevalidation access. The original quotient-only division limitation is superseded by the round259 source revision below. External power/clock calls are explicit aliases supplied synthetic returns in tests. UART driver zero-divisor/overflow paths and physical device behavior remain unvalidated.

## Main unsigned division ABI revision (round259)

`division_support.c` now supplies R1:R0 quotient and R3:R2 remainder, preserving callee-saved registers and SP. Its C restoring arithmetic and named ARM AAPCS wrapper matched native Main 0x47cc60..0x47ce90 across 1,569 bounded cases, including wide divisors and native zero behavior (unchanged numerator, zero remainder registers). This supersedes the original quotient-only shim; it does not qualify UART hardware, exact helper bytes/timing/stack scratch, or whole firmware. [Native comparison receipt](../../../analysis/c-source-completion-20261011/peripherals/root-main-udivmod-abi-round259/receipt.json).
