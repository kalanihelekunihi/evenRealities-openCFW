/* Apollo LV image-header request wrapper, native 0x488f6a..0x488f9b. */
#include <stdint.h>

extern void audio_uart_lv_image_memzero_488f40(void *state, uint32_t bytes);
extern uint32_t audio_uart_lv_image_source_type_488cb8(const void *source);
extern uint32_t audio_uart_lv_decoder_find_48925a(void *state, void *header);

uint32_t audio_uart_lv_image_header_488f6a(const void *source, void *header) {
    uint8_t state[0x4cu];
    audio_uart_lv_image_memzero_488f40(state, sizeof(state));
    *(uint32_t *)(void *)(state + 0x0cu) = (uint32_t)(uintptr_t)source;
    state[0x10u] = (uint8_t)audio_uart_lv_image_source_type_488cb8(source);
    return audio_uart_lv_decoder_find_48925a(state, header) != 0u;
}
