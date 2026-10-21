/* Apollo LV base-class event, native 0x43e7d2..0x43ebeb.
 * Lower services retain their native address labels until separately owned. */
#include <stdint.h>

extern uint32_t audio_uart_page_event_code_450286(const void *event);
extern void audio_uart_lv_obj_flag_set_43e046(void *object, uint32_t flags);
extern void audio_uart_lv_obj_flag_clear_43e086(void *object, uint32_t flags);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *object, uint32_t flags);
extern uint32_t audio_uart_lv_obj_state_43e156(void *object);
extern void *audio_uart_lv_obj_group_43e1be(void *object);
extern void audio_uart_lv_obj_event_state_43e442(void *event);
extern void audio_uart_lv_mark_layout_43f648(void *object);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *object);
extern int32_t audio_uart_lv_obj_height_43fdda(void *object);
extern void audio_uart_lv_invalidate_area_4405d4(void *object, const void *area);
extern uint32_t audio_uart_lv_obj_is_scrolling_44d19a(void *object);
extern uint32_t audio_uart_page_get_editing_44d5a4(const void *group);
extern uint32_t audio_uart_lv_child_count_44ddea(void *object);
extern uint32_t audio_uart_lv_get_scrollbar_mode_44e42c(void *object);
extern uint32_t audio_uart_lv_get_scroll_dir_44e442(void *object);
extern int32_t audio_uart_lv_obj_x_44e486(void *object);
extern int32_t audio_uart_lv_obj_y_44e498(void *object);
extern int32_t audio_uart_lv_scroll_left_44e586(void *object);
extern int32_t audio_uart_lv_scroll_right_44e67a(void *object);
extern void audio_uart_lv_scroll_to_x_44e9da(void *object, int32_t x, uint32_t animation);
extern void audio_uart_lv_scroll_to_y_44ea04(void *object, int32_t y, uint32_t animation);
extern void audio_uart_lv_scroll_to_view_44ea56(void *object, uint32_t animation);
extern void audio_uart_lv_get_scrollbar_areas_44eb28(void *object, void *first, void *second);
extern uint32_t audio_uart_lv_metric_43dd52(void *object, uint32_t selector);
extern uint32_t audio_uart_lv_metric_43dd5c(void *object, uint32_t selector);
extern uint32_t audio_uart_lv_metric_43dd66(void *object, uint32_t selector);
extern uint32_t audio_uart_lv_metric_43de76(void *object, uint32_t selector);
extern uint32_t audio_uart_lv_obj_event_451670(void *object, uint32_t code, void *param);
extern void *audio_uart_lv_input_reset_4518d8(void *event);
extern uint32_t audio_uart_lv_event_param_4519a0(void *event);
extern void audio_uart_page_event_extent_4519fa(void *event, int32_t value);
extern uint32_t audio_uart_lv_compass_452c66(void *object, uint32_t selector);
extern void *audio_uart_lv_active_input_452ef8(void);
extern uint32_t audio_uart_lv_input_type_452f00(const void *input);
extern uint32_t audio_uart_lv_input_scroll_object_452fae(const void *input);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static uint16_t get16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}

static void put16(uint8_t *p, uint16_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
}

static void mark_children(void *object) {
    uint8_t *p = (uint8_t *)object;
    uint32_t count = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t i = 0; i < count; ++i) {
        uint32_t spec = get32(p + 8u);
        uint32_t rows = get32((const uint8_t *)(uintptr_t)spec);
        uint32_t child = get32((const uint8_t *)(uintptr_t)(rows + i * 4u));
        audio_uart_lv_mark_layout_43f648((void *)(uintptr_t)child);
    }
}

void audio_uart_lv_base_event_43e7d2(void *unused, void *event) {
    (void)unused;
    uint8_t *e = (uint8_t *)event;
    uint32_t code = audio_uart_page_event_code_450286(event);
    void *object = (void *)(uintptr_t)get32(e);
    uint8_t *p = (uint8_t *)object;

    if (code == 1u) {
        audio_uart_lv_obj_flag_set_43e046(object, 0x20u);
    } else if (code == 0xbu) {
        audio_uart_lv_obj_flag_clear_43e086(object, 0x20u);
        if (audio_uart_lv_input_scroll_object_452fae(
                (void *)(uintptr_t)get32(e + 0x10u)) == 0u &&
            audio_uart_lv_obj_has_flag_43e0e0(object, 8u) != 0u) {
            if ((audio_uart_lv_obj_state_43e156(object) & 1u) != 0u)
                audio_uart_lv_obj_flag_clear_43e086(object, 1u);
            else
                audio_uart_lv_obj_flag_set_43e046(object, 1u);
            (void)audio_uart_lv_obj_event_451670(object, 0x23u, 0);
        }
    } else if (code == 3u) {
        audio_uart_lv_obj_flag_clear_43e086(object, 0x20u);
    } else if (code == 0x32u) {
        mark_children(object);
    } else if (code == 0x11u) {
        if (audio_uart_lv_obj_has_flag_43e0e0(object, 8u) == 0u) {
            if (audio_uart_lv_obj_has_flag_43e0e0(object, 0x810u) != 0u &&
                audio_uart_lv_obj_is_scrolling_44d19a(object) == 0u) {
                int32_t left = audio_uart_lv_scroll_left_44e586(object);
                int32_t right = audio_uart_lv_scroll_right_44e67a(object);
                uint32_t direction = audio_uart_lv_event_param_4519a0(event);
                if (direction == 0x12u || direction == 0x11u) {
                    int32_t y = audio_uart_lv_obj_y_44e498(object);
                    int32_t height = audio_uart_lv_obj_height_43fdda(object);
                    int32_t target = direction == 0x12u ? y + height / 4 : y - height / 4;
                    audio_uart_lv_scroll_to_y_44ea04(object, target, 0u);
                } else if (direction == 0x13u || direction == 0x14u) {
                    uint32_t scroll_dir = audio_uart_lv_get_scroll_dir_44e442(object);
                    if ((scroll_dir & 3u) == 0u || (left < 1 && right < 1)) {
                        int32_t y = audio_uart_lv_obj_y_44e498(object);
                        int32_t height = audio_uart_lv_obj_height_43fdda(object);
                        int32_t target = direction == 0x13u ? y + height / 4 : y - height / 4;
                        audio_uart_lv_scroll_to_y_44ea04(object, target, 0u);
                    } else {
                        int32_t x = audio_uart_lv_obj_x_44e486(object);
                        int32_t width = audio_uart_lv_obj_width_43fd9e(object);
                        int32_t target = direction == 0x13u ? x + width / 4 : x - width / 4;
                        audio_uart_lv_scroll_to_x_44e9da(object, target, 0u);
                    }
                }
            }
        } else {
            uint32_t direction = audio_uart_lv_event_param_4519a0(event);
            if (direction == 0x13u || direction == 0x11u)
                audio_uart_lv_obj_flag_set_43e046(object, 1u);
            else if (direction == 0x14u || direction == 0x12u)
                audio_uart_lv_obj_flag_clear_43e086(object, 1u);
            if (direction != 10u)
                (void)audio_uart_lv_obj_event_451670(object, 0x23u, 0);
        }
    } else if (code == 0x13u) {
        if (audio_uart_lv_obj_has_flag_43e0e0(object, 0x400u) != 0u)
            audio_uart_lv_scroll_to_view_44ea56(object, 1u);
        void *group = audio_uart_lv_obj_group_43e1be(object);
        uint32_t editing = audio_uart_page_get_editing_44d5a4(group);
        uint32_t flags = 2u;
        void *input = audio_uart_lv_active_input_452ef8();
        if (input == 0) input = audio_uart_lv_input_reset_4518d8(event);
        uint32_t kind = (uint8_t)audio_uart_lv_input_type_452f00(input);
        if (kind == 2u || kind == 4u) flags |= 4u;
        if ((uint8_t)editing != 0u)
            audio_uart_lv_obj_flag_set_43e046(object, flags | 8u);
        else {
            audio_uart_lv_obj_flag_set_43e046(object, flags);
            audio_uart_lv_obj_flag_clear_43e086(object, 8u);
        }
    } else if (code == 0xcu) {
        audio_uart_lv_obj_flag_set_43e046(object, 0x40u);
    } else if (code == 0xeu) {
        audio_uart_lv_obj_flag_clear_43e086(object, 0x40u);
        if (audio_uart_lv_get_scrollbar_mode_44e42c(object) == 2u) {
            uint8_t first[16], second[16];
            audio_uart_lv_get_scrollbar_areas_44eb28(object, first, second);
            audio_uart_lv_invalidate_area_4405d4(object, first);
            audio_uart_lv_invalidate_area_4405d4(object, second);
        }
    } else if (code == 0x14u) {
        audio_uart_lv_obj_flag_clear_43e086(object, 0xeu);
    } else if (code == 0x31u) {
        uint32_t glyph = audio_uart_lv_metric_43dd66(object, 0u);
        uint32_t decoration = audio_uart_lv_metric_43de76(object, 0u);
        if (glyph != 0u || (uint16_t)decoration != 0u)
            audio_uart_lv_mark_layout_43f648(object);
        mark_children(object);
    } else if (code == 0x2au) {
        uint32_t first = audio_uart_lv_metric_43dd52(object, 0u);
        uint32_t second = audio_uart_lv_metric_43dd5c(object, 0u);
        uint32_t third = audio_uart_lv_metric_43dd66(object, 0u);
        uint32_t fourth = audio_uart_lv_metric_43de76(object, 0u);
        if ((uint16_t)fourth != 0u || third != 0u ||
            first == 0x3fffffffu || second == 0x3fffffffu)
            audio_uart_lv_mark_layout_43f648(object);
    } else if (code == 0x2cu) {
        put16(p + 0x2au, (uint16_t)(get16(p + 0x2au) | 2u));
        audio_uart_lv_mark_layout_43f648(object);
    } else if (code == 0x1bu) {
        uint32_t value = audio_uart_lv_compass_452c66(object, 0u);
        audio_uart_page_event_extent_4519fa(event, (int32_t)value);
    } else if (code == 0x1du || code == 0x20u || code == 0x1au) {
        audio_uart_lv_obj_event_state_43e442(event);
    } else if (code == 0x17u) {
        audio_uart_lv_obj_flag_clear_43e086(object, 0x20u);
        audio_uart_lv_obj_flag_clear_43e086(object, 0x40u);
    } else if (code == 0x18u) {
        audio_uart_lv_obj_flag_set_43e046(object, 0x10u);
    } else if (code == 0x19u) {
        audio_uart_lv_obj_flag_clear_43e086(object, 0x10u);
    }
}
