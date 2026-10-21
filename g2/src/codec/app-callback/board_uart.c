/* Experimental C reduction of retained image_a_xip pseudocode. Function
 * envelopes: 0x10203004, 0x1020300c, 0x10203050, 0x1020324c, 0x10203260.
 * No stock/source execution or producing ABI qualification is claimed here.
 * Independent native listings establish signed gain bytes and both burst loads.
 * Product constants are semantic data; their final placement remains open.
 */
#include <stddef.h>
#include <stdint.h>
#include "resident_board_product_state.h"

/* Stock literal at 0x10203008 and nine signed dB gains at 0x1020a8aa. */
const uint32_t g2_codec_board_constant =
    (uint32_t)(uintptr_t)&gx8002_board_state_269a4;
const int8_t g2_codec_gain_table[9] = {6, 12, 18, 24, 30, 36, 42, 48, 54};

uint32_t g2_codec_audio_board_get(void)
{
    return g2_codec_board_constant;
}

int32_t g2_codec_audio_board_gain(int32_t gain)
{
    const uint32_t index = (uint32_t)gain - UINT32_C(1);
    return index < 9 ? (int32_t)g2_codec_gain_table[index] : 0;
}

struct g2_codec_uart_prefix {
    uint32_t reserved_00;
    volatile uint32_t *registers;
    uint8_t reserved_08_33[44];
    int32_t burst_nonzero_direction;
    int32_t burst_zero_direction;
};
_Static_assert(offsetof(struct g2_codec_uart_prefix, registers) == 4,
               "32-bit UART register pointer offset");
_Static_assert(offsetof(struct g2_codec_uart_prefix, burst_nonzero_direction) == 0x34,
               "UART burst offset");
_Static_assert(offsetof(struct g2_codec_uart_prefix, burst_zero_direction) == 0x38,
               "UART alternate burst offset");

uint32_t g2_codec_dw_uart_dma_burst(const struct g2_codec_uart_prefix *uart,
                                 int32_t direction)
{
    /* Native 0x10203052/54 load both fields before conditional selection. */
    const int32_t first = ((const volatile struct g2_codec_uart_prefix *)uart)->burst_nonzero_direction;
    const int32_t second = ((const volatile struct g2_codec_uart_prefix *)uart)->burst_zero_direction;
    const int32_t size = direction == 0 ? second : first;
    switch (size) {
    case 4: return 1;
    case 8: return 2;
    case 16: return 3;
    case 32: return 4;
    case 64: return 5;
    case 128: return 6;
    case 256: return 7;
    case 512: return 8;
    case 1024: return 9;
    default: return 0;
    }
}

void g2_codec_dw_uart_putc(const struct g2_codec_uart_prefix *uart, uint32_t value)
{
    volatile uint32_t *const registers = uart->registers;
    while ((registers[5] & UINT32_C(0x20)) == 0) {
    }
    registers[0] = value;
}

uint32_t g2_codec_dw_uart_getc(const struct g2_codec_uart_prefix *uart)
{
    volatile uint32_t *const registers = uart->registers;
    while ((registers[5] & UINT32_C(1)) == 0) {
    }
    return registers[0] & UINT32_C(0xff);
}
