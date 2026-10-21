/* Apollo LV draw task defaults, native 0x451b9c..0x451c39. */
#include <stdint.h>

extern const unsigned char audio_uart_display_page_style[];

uint32_t audio_uart_lv_draw_task_init_451b9c(void *task) {
    uint8_t *p = (uint8_t *)task;
    for (unsigned i = 0; i < 0x70u; ++i) p[i] = 0u;

    p[0x21] = p[0x22] = p[0x23] = 0xffu;
    p[0x24] = p[0x25] = p[0x26] = 0xffu;
    p[0x2d] = 0xffu;
    p[0x2e] = 2u;

    uintptr_t style = (uintptr_t)audio_uart_display_page_style;
    for (unsigned i = 0; i < 4u; ++i) p[0x34u + i] = (uint8_t)(style >> (i * 8u));
    p[0x20] = p[0x3b] = p[0x58] = p[0x48] = p[0x6c] = 0xffu;
    p[0x49] = (uint8_t)((p[0x49] & 0xe0u) | 0x0fu);
    return 0u;
}
