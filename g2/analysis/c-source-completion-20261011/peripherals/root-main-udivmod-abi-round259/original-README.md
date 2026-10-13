# UART power/configuration offline comparison source

Selected unchanged pinned Apollo510 SDK bodies with retained BSD3 notice; stock284Bhandle/16Bconfig and register adapters. [Evidence and limitations](../../../analysis/audio-uart-power-config-2026-10-09/REPORT.md), [pseudocode](../../../analysis/audio-uart-power-config-2026-10-09/pseudocode.md).

This is an offline knowledge/comparison artifact, not a production driver. interrupt-clear differs in an extra MIS read and NULL prevalidation access. Quotient-only division helper is not a full runtime ABI. External power/clock calls are explicit aliases supplied synthetic returns in tests. Zero divisor/overflow and physical device behavior unvalidated.
