/* SPDX-License-Identifier: MIT
 * Image-A source initializer 0x10026a94..0x10026b94. XIP channel users
 * index these two 128-byte records by channel << 7 at runtime alias
 * 0x20026a94. Exact product values are authenticated against stock bytes.
 */
#include <stdint.h>

struct gx8002_uart_channel_descriptor {
    uint32_t channel;
    uint32_t register_base;
    uint32_t reserved_08[2];
    uint32_t baud;
    uint32_t reserved_14[2];
    uint32_t data_bits;
    uint32_t initialized;
    uint32_t reserved_24[6];
    uint32_t irq;
    uint32_t reserved_40;
    uint32_t callback_enabled;
    uint32_t callback;
    uint32_t callback_arg;
    uint32_t reserved_50[12];
};
_Static_assert(sizeof(struct gx8002_uart_channel_descriptor) == 128,
               "native UART channel extent");

const struct gx8002_uart_channel_descriptor gx8002_uart_channels_26a94[2]
    __attribute__((section(".gx8002.uart_channels.26a94"), used,
                   aligned(4))) = {
    {.channel = 0u, .register_base = UINT32_C(0xa0100000),
     .baud = 115200u, .data_bits = 8u, .initialized = 1u, .irq = 6u},
    {.channel = 1u, .register_base = UINT32_C(0xa0200000),
     .baud = 115200u, .data_bits = 8u, .initialized = 1u, .irq = 7u},
};
