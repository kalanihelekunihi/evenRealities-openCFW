/* Native recursive LV object layout refresh at 0x440d70. */
#include <stdint.h>

extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern uint32_t audio_uart_lv_basic_invalidate_43f1a4(void *);
extern void audio_uart_lv_obj_refr_pos_43ffd0(void *);
extern void audio_uart_lv_obj_layout_apply_4546f4(void *);
extern void audio_uart_lv_obj_scroll_reconcile_44f316(void *, uint32_t);

void audio_uart_lv_obj_update_layout_440d70(void *object) {
    uint8_t *root = (uint8_t *)object;
    uint32_t children = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t i = 0; i < children; ++i) {
        uint8_t *spec = *(uint8_t **)(void *)(root + 8u);
        void **entries = *(void ***)(void *)spec;
        audio_uart_lv_obj_update_layout_440d70(entries[i]);
    }
    volatile uint16_t *flags = (volatile uint16_t *)(void *)(root + 0x2au);
    if ((*flags & 1u) != 0u) {
        *flags = (uint16_t)(*flags & (uint16_t)~1u);
        (void)audio_uart_lv_basic_invalidate_43f1a4(object);
        audio_uart_lv_obj_refr_pos_43ffd0(object);
        if (children != 0u) audio_uart_lv_obj_layout_apply_4546f4(object);
    }
    if ((*flags & 2u) != 0u) {
        *flags = (uint16_t)(*flags & (uint16_t)~2u);
        audio_uart_lv_obj_scroll_reconcile_44f316(object, 0u);
    }
}
