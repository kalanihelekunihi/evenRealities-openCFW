/* Native lv_obj_update_layout outer dirty-screen loop at 0x43f66c. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[]; /* native RAM 0x2006f548 */
extern void *audio_uart_lv_object_screen(void *);
extern void audio_uart_lv_obj_update_layout_440d70(void *);

void audio_uart_page_43f66c(void *object) {
    if (audio_uart_display_lv_root[0x60u] != 0u) return;
    audio_uart_display_lv_root[0x60u] = 1u;
    uint8_t *screen = (uint8_t *)audio_uart_lv_object_screen(object);
    for (;;) {
        volatile uint16_t *flags = (volatile uint16_t *)(void *)(screen + 0x2au);
        if ((*flags & 4u) == 0u) break;
        *flags = (uint16_t)(*flags & (uint16_t)~4u);
        audio_uart_lv_obj_update_layout_440d70(screen);
    }
    audio_uart_display_lv_root[0x60u] = 0u;
}
