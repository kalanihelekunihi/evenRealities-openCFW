/* SPDX-License-Identifier: MIT
 * UART boot stage-1 XIP transfer bodies 0x100018c0 and 0x10001940.
 * Register ordering follows the native instruction stream; lengths count
 * bytes, including the stock write path's byte load despite decompiler type.
 */
#include <stdint.h>

static volatile uint32_t *const xip =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
static volatile uint32_t *const xip_aux =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa20000f4);

void gx8002_uart_stage1_xip_read(uint32_t address, uint8_t *destination,
                                  uint32_t length)
{
    while ((xip[0x28 / 4] & 1u) != 0) { }
    xip[0x08 / 4] = 0;
    xip[0x4c / 4] = 0;
    xip[0x00 / 4] = UINT32_C(0xc07);
    xip[0x04 / 4] = length - 1u;
    xip[0x10 / 4] = 1;
    xip[0x18 / 4] = 0;
    *xip_aux = 0;
    xip[0x08 / 4] = 1;
    xip[0x60 / 4] = address;
    for (uint32_t i = 0; i < length; ++i) {
        while ((xip[0x28 / 4] & 8u) == 0) { }
        destination[i] = (uint8_t)xip[0x60 / 4];
    }
    while (xip[0x24 / 4] != 0) { }
    while ((xip[0x28 / 4] & 1u) != 0) { }
}

void gx8002_uart_stage1_xip_write(uint32_t address, const uint8_t *source,
                                   uint32_t length)
{
    while ((xip[0x28 / 4] & 1u) != 0) { }
    xip[0x08 / 4] = 0;
    xip[0x4c / 4] = 0;
    xip[0x00 / 4] = UINT32_C(0x407);
    xip[0x04 / 4] = length;
    xip[0x10 / 4] = 1;
    xip[0x18 / 4] = length << 16;
    *xip_aux = 0;
    xip[0x08 / 4] = 1;
    xip[0x60 / 4] = address;
    for (uint32_t i = 0; i < length; ++i) {
        while ((xip[0x28 / 4] & 2u) == 0) { }
        xip[0x60 / 4] = source[i];
    }
    while (xip[0x20 / 4] != 0) { }
    while ((xip[0x28 / 4] & 1u) != 0) { }
}
