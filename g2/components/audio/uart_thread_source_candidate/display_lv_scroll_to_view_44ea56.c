/* Apollo LV scroll-to-view ancestor walk, native 0x44ea56..0x44ea97. */
#include <stdint.h>

extern void audio_uart_page_43f66c(void *object);
extern void *audio_uart_lv_obj_parent_44dca2(void *object);
extern void audio_uart_lv_scroll_view_step_44f40c(void *coordinates, void *child,
                                                   void *area, uint32_t animation);

void audio_uart_lv_scroll_to_view_44ea56(void *object, uint32_t animation) {
    audio_uart_page_43f66c(object);
    uint32_t area[2] = {0u, 0u};
    void *child = object;
    void *parent = audio_uart_lv_obj_parent_44dca2(child);
    while (parent != 0) {
        audio_uart_lv_scroll_view_step_44f40c((uint8_t *)object + 0x14u,
                                               child, area, (uint8_t)animation);
        child = parent;
        parent = audio_uart_lv_obj_parent_44dca2(child);
    }
}
