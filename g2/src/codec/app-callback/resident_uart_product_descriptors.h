/* SPDX-License-Identifier: MIT
 * Native image-A UART channel records at source 0x10026a94,
 * runtime alias 0x20026a94. Final scatter placement remains external.
 */
#ifndef GX8002_RESIDENT_UART_PRODUCT_DESCRIPTORS_H
#define GX8002_RESIDENT_UART_PRODUCT_DESCRIPTORS_H

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

extern struct gx8002_uart_channel_descriptor gx8002_uart_channels_26a94[2];

#endif
