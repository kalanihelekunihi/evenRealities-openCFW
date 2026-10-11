#include <stdint.h>

/* Native 0x58fb38 wraps channel-3 transmission at 0x55e7fa and
 * maps a nonzero status to -1. Selected codec_uart_tx does the same. */
extern int32_t codec_uart_tx(const uint8_t *wire, uint32_t count);

int32_t audio_uart_send_bytes(const void *wire, uint32_t count) {
    return codec_uart_tx(wire, count);
}
