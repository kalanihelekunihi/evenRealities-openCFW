/* Native LVGL nested-event scope 0x44ffd0/0x44ffdc.
 * The active event is the live LV root word at +0x6c. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];

void audio_uart_lv_event_scope_begin_44ffd0(void *event) {
    uint32_t *active=(uint32_t *)(void *)(audio_uart_display_lv_root+0x6cu);
    *(uint32_t *)((uint8_t *)event+0x14u)=*active;
    *active=(uint32_t)(uintptr_t)event;
}

void audio_uart_lv_event_scope_end_44ffdc(void *event) {
    uint32_t *active=(uint32_t *)(void *)(audio_uart_display_lv_root+0x6cu);
    *active=*(uint32_t *)((uint8_t *)event+0x14u);
}
