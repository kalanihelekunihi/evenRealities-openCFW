/* Native LV object flag mutation 0x43ded4 and 0x43dfa4. */
#include <stdint.h>

extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *, uint32_t);
extern uint32_t audio_uart_lv_layout_positioned_43f612(void *);
extern void audio_uart_page_invalidate_440656(void *);
extern void *audio_uart_lv_obj_group_43e1be(void *);
extern void audio_uart_page_update_unbound_44d45c(void *);
extern void *audio_uart_page_active_object_44d58c(void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern void audio_uart_lv_mark_layout_43f648(void *);
extern void audio_uart_lv_get_scrollbar_areas_44eb28(void *, void *, void *);
extern void audio_uart_lv_invalidate_area_4405d4(void *, const void *);

uint32_t audio_uart_lv_obj_has_state_43e184(void *object, uint32_t mask) {
    if (object == 0) __builtin_trap();
    return ((*(const uint16_t *)((const uint8_t *)object + 0x28u) & mask) != 0u);
}

void audio_uart_page_43ded4(void *object, uint32_t flags) {
    if (object == 0) __builtin_trap();
    if (audio_uart_lv_obj_has_flag_43e0e0(object, flags) != 0u) return;
    const uint8_t old_layout = (uint8_t)audio_uart_lv_layout_positioned_43f612(object);
    if ((flags & 1u) != 0u) audio_uart_page_invalidate_440656(object);
    uint8_t *const bytes = (uint8_t *)object;
    *(uint32_t *)(void *)(bytes + 0x24u) |= flags;
    if ((flags & 1u) != 0u && audio_uart_lv_obj_has_state_43e184(object, 2u) != 0u) {
        void *group = audio_uart_lv_obj_group_43e1be(object);
        if (group != 0) {
            audio_uart_page_update_unbound_44d45c(group);
            void *active = audio_uart_page_active_object_44d58c(group);
            if (active != 0) audio_uart_page_invalidate_440656(active);
        }
    }
    const uint8_t new_layout = (uint8_t)audio_uart_lv_layout_positioned_43f612(object);
    if (old_layout != new_layout || (flags & 0x01800000u) != 0u) {
        audio_uart_lv_mark_layout_43f648(audio_uart_lv_obj_parent_44dca2(object));
        audio_uart_lv_mark_layout_43f648(object);
    }
    if ((flags & 0x10u) != 0u) {
        uint32_t first[4], second[4];
        audio_uart_lv_get_scrollbar_areas_44eb28(object, first, second);
        audio_uart_lv_invalidate_area_4405d4(object, first);
        audio_uart_lv_invalidate_area_4405d4(object, second);
    }
}

void audio_uart_page_43dfa4(void *object, uint32_t flags) {
    if (object == 0) __builtin_trap();
    if (audio_uart_lv_obj_has_flag_any_43e11c(object, flags) == 0u) return;
    const uint8_t old_layout = (uint8_t)audio_uart_lv_layout_positioned_43f612(object);
    if ((flags & 0x10u) != 0u) {
        uint32_t first[4], second[4];
        audio_uart_lv_get_scrollbar_areas_44eb28(object, first, second);
        audio_uart_lv_invalidate_area_4405d4(object, first);
        audio_uart_lv_invalidate_area_4405d4(object, second);
    }
    uint8_t *const bytes = (uint8_t *)object;
    *(uint32_t *)(void *)(bytes + 0x24u) &= ~flags;
    if ((flags & 1u) != 0u) {
        audio_uart_page_invalidate_440656(object);
        audio_uart_lv_mark_layout_43f648(audio_uart_lv_obj_parent_44dca2(object));
        audio_uart_lv_mark_layout_43f648(object);
    }
    const uint8_t new_layout = (uint8_t)audio_uart_lv_layout_positioned_43f612(object);
    if (old_layout != new_layout || (flags & 0x01800000u) != 0u)
        audio_uart_lv_mark_layout_43f648(audio_uart_lv_obj_parent_44dca2(object));
}
