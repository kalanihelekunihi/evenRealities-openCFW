# Main unsigned division support

The UART power/configuration comparison copies that used to live here were retired: `am_hal_uart_power_control`/`am_hal_uart_configure`/`am_hal_uart_interrupt_clear` now compile from AmbiqSuite 5.1.0 `hal/mcu/am_hal_uart.c` (generated stock-variant copy, see the U6 manifest notes). Only `division_support.c` remains.

## Main unsigned division ABI revision (round259)

`division_support.c` now supplies R1:R0 quotient and R3:R2 remainder, preserving callee-saved registers and SP. Its C restoring arithmetic and named ARM AAPCS wrapper matched native Main 0x47cc60..0x47ce90 across 1,569 bounded cases, including wide divisors and native zero behavior (unchanged numerator, zero remainder registers). This supersedes the original quotient-only shim; it does not qualify UART hardware, exact helper bytes/timing/stack scratch, or whole firmware. Native comparison receipt (`pre-consolidation:g2/analysis/c-source-completion-20261011/peripherals/root-main-udivmod-abi-round259/receipt.json`).
