/* SPDX-License-Identifier: MIT
 * Native XIP 0x102035d8 signed length loop. Its 0x10203260 DesignWare
 * receive provider is already selected in board_uart.c.
 */
#include <stdint.h>

struct g2_codec_uart_prefix;
extern uint32_t g2_codec_dw_uart_getc(
    const struct g2_codec_uart_prefix *uart);

int32_t gx8002_xip_uart_read_102035d8(uint32_t port, uint8_t *destination,
                                       int32_t count)
{
    volatile const uint8_t *const channel =
        (volatile const uint8_t *)(uintptr_t)
            (UINT32_C(0x20026a94) + (port << 7u));
    for (int32_t index = 0; index < count; ++index)
        destination[index] = (uint8_t)g2_codec_dw_uart_getc(
            (const struct g2_codec_uart_prefix *)(const void *)channel);
    return count > 0 ? count : 0;
}
