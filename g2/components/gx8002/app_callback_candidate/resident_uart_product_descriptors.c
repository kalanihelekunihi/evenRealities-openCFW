/* SPDX-License-Identifier: MIT
 * Image-A source initializer 0x10026a94..0x10026b94. XIP channel users
 * index these two 128-byte records by channel << 7 at runtime alias
 * 0x20026a94. Exact product values are authenticated against stock bytes.
 */
#include "resident_uart_product_descriptors.h"

struct gx8002_uart_channel_descriptor gx8002_uart_channels_26a94[2]
    __attribute__((section(".gx8002.uart_channels.26a94"), used,
                   aligned(4))) = {
    {.channel = 0u, .register_base = UINT32_C(0xa0100000),
     .baud = 115200u, .data_bits = 8u, .initialized = 1u, .irq = 6u},
    {.channel = 1u, .register_base = UINT32_C(0xa0200000),
     .baud = 115200u, .data_bits = 8u, .initialized = 1u, .irq = 7u},
};
