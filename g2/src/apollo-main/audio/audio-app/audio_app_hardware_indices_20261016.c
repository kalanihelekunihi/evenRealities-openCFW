/* Stock zero wrapper 0x4d4ccc (movs r2,#0; b.w 0x43c0ec).
 *
 * The rate/format index helpers that used to live here (0x590d3c, 0x590d74)
 * are liblc3 v1.1.3 lc3.c resolve_dt / resolve_srate, kept out of line by
 * IAR; they now come from the upstream unit third-party/upstream/liblc3/src/lc3.c. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

void audio_app_zero_tail_4d4ccc(void *destination, uint32_t length) {
    audio_uart_buffer_zero(destination, length, 0u);
}
