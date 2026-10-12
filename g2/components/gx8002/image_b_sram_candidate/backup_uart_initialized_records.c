/* SPDX-License-Identifier: MIT
 * Native initialized UART records, stage-2 IRAM 0x10016b84..0x10016c84,
 * runtime DRAM aliases 0x20016b84..0x20016c84. The selected UART code
 * addresses port * 0x80 and reads these exact fields before reconfiguration.
 * Zeros in the unused slots are authenticated stock initialized values.
 */
#include <stdint.h>

struct gx8002_image_b_uart_initial_record {
    uint32_t port;
    uint32_t registers;
    uint32_t clock_hz;
    uint32_t reserved_clock;
    uint32_t baud;
    uint32_t divisor;
    uint32_t fractional_divisor;
    uint32_t data_bits;
    uint32_t stop_bits;
    uint32_t reserved_format[6];
    uint32_t irq_line;
    uint32_t live_runtime[16];
};

_Static_assert(sizeof(struct gx8002_image_b_uart_initial_record) == 128u,
               "native UART port record stride");

__attribute__((section(".data.image_b.uart0_record"), aligned(4)))
struct gx8002_image_b_uart_initial_record gx8002_image_b_uart0_initial = {
    .port = 0u, .registers = UINT32_C(0xa0100000), .baud = 115200u,
    .data_bits = 8u, .stop_bits = 1u, .irq_line = 6u,
};

__attribute__((section(".data.image_b.uart1_record"), aligned(4)))
struct gx8002_image_b_uart_initial_record gx8002_image_b_uart1_initial = {
    .port = 1u, .registers = UINT32_C(0xa0200000), .baud = 115200u,
    .data_bits = 8u, .stop_bits = 1u, .irq_line = 7u,
};
