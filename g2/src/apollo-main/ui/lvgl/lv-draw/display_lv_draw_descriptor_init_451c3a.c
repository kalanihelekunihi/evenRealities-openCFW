/* Apollo LV draw descriptor defaults, native 0x451c3a..0x451c6d. */
#include <stdint.h>

void audio_uart_lv_draw_descriptor_init_451c3a(void *descriptor) {
    uint8_t *p = (uint8_t *)descriptor;
    for (unsigned i = 0; i < 0x30u; ++i) p[i] = 0u;
    p[0x14] = 0x30u;
    p[0x20] = 0xffu;
}
