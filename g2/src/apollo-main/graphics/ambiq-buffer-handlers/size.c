/* Apollo S200 buffer byte rounding at 0x53cfe4 and 0x53cff0. */
#include <stdint.h>

extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);

uint32_t audio_uart_ambiq_buffer_round_bytes_53cfe4(uint32_t bytes) {
    return bytes == 0u ? 0u : ((bytes + 7u) >> 3) << 3;
}

uint32_t audio_uart_ambiq_buffer_format_bytes_53cff0(uint32_t pixels,
                                                        uint32_t format) {
    const uint32_t bits = audio_uart_lv_color_bpp_440f44(format & 0xffu);
    return (pixels * bits + 7u) >> 3;
}
