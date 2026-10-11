/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102035b4..0x102035d2, 0x102037f0..0x102037fe.
 * The output path owns CR-before-LF conversion and the resident UART channel
 * stride. Product SRAM channel descriptors and selected port are typed imports.
 */
#include <stdint.h>

struct g2_codec_uart_prefix;
extern void g2_codec_dw_uart_putc(const struct g2_codec_uart_prefix *uart,
                                   uint32_t value);
extern uint8_t gx8002_xip_uart_channel_storage_20026a94[];
extern uint32_t gx8002_xip_console_port_2002731c;

static struct g2_codec_uart_prefix *gx8002_xip_uart_channel(uint32_t port)
{
    return (struct g2_codec_uart_prefix *)(void *)(
        gx8002_xip_uart_channel_storage_20026a94 + port * 0x80u);
}

void gx8002_xip_uart_putc_102035b4(uint32_t port, uint32_t character)
{
    struct g2_codec_uart_prefix *channel = gx8002_xip_uart_channel(port);
    if (character == 10u) g2_codec_dw_uart_putc(channel, 13u);
    g2_codec_dw_uart_putc(channel, character & 0xffu);
}

void gx8002_xip_console_putc_102037f0(uint32_t character)
{
    gx8002_xip_uart_putc_102035b4(gx8002_xip_console_port_2002731c,
                                    character);
}
