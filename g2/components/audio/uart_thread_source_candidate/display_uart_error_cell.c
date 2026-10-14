/* Shared mutable error word at native Main 0x20074f14. The locale range
 * writer and float math error path address the same four bytes under
 * different source names. Absolute SRAM placement remains open. */
#include <stdint.h>

volatile uint32_t audio_uart_float_math_error_cell_20074f14;
extern volatile uint32_t audio_uart_ring_errno_20074f14
    __attribute__((alias("audio_uart_float_math_error_cell_20074f14")));
