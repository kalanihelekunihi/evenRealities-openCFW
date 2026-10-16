/* Stock audio rate/format indices at 0x590d3c/0x590d74 and zero wrapper 0x4d4ccc. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

int32_t audio_app_rate_index_590d3c(int32_t rate, uint32_t format) {
    if (rate == 2500)
        return 0;
    if (rate == 5000)
        return 1;
    if (format == 0u && rate == 7500)
        return 2;
    if (rate == 10000)
        return 3;
    return 4;
}

uint32_t audio_app_format_index_590d74(int32_t rate, uint32_t format) {
    if (format != 0u) {
        if (rate == 48000)
            return 5u;
        if (rate == 96000)
            return 6u;
        return 7u;
    }
    switch (rate) {
    case 8000: return 0u;
    case 16000: return 1u;
    case 24000: return 2u;
    case 32000: return 3u;
    case 48000: return 4u;
    default: return 7u;
    }
}

void audio_app_zero_tail_4d4ccc(void *destination, uint32_t length) {
    audio_uart_buffer_zero(destination, length, 0u);
}
