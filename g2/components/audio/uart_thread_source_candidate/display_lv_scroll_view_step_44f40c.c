/* Apollo Main LVGL scroll-to-view step, native 0x44f40c..0x44f703. */
#include <stdint.h>

extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern uint32_t audio_uart_lv_get_scroll_dir_44e442(void *);
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_top_44e230(void *, uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_bottom_44e23a(void *, uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_left_44e244(void *, uint32_t);
extern int32_t audio_uart_lv_style_raw_pad_right_44e24e(void *, uint32_t);
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *);
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *);
extern int32_t audio_uart_lv_scroll_left_44e586(void *);
extern int32_t audio_uart_lv_scroll_right_44e67a(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_area_height_4515a4(const int32_t *);
extern int32_t audio_uart_lv_area_width_451598(const int32_t *);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern void audio_uart_lv_scroll_anim_x_44f3b8(void *, int32_t);
extern void audio_uart_lv_scroll_anim_y_44f3d4(void *, int32_t);
extern void audio_uart_lv_scroll_dispatch_44e884(void *, int32_t, int32_t, uint32_t);

static int32_t add32(int32_t a, int32_t b) {
    return (int32_t)((uint32_t)a + (uint32_t)b);
}
static int32_t sub32(int32_t a, int32_t b) {
    return (int32_t)((uint32_t)a - (uint32_t)b);
}
static int32_t neg32(int32_t a) {
    return (int32_t)(0u - (uint32_t)a);
}
static uint32_t rd32(const uint8_t *p) {
    uint32_t value;
    __builtin_memcpy(&value, p, 4u);
    return value;
}
static uint16_t rd16(const uint8_t *p) {
    uint16_t value;
    __builtin_memcpy(&value, p, 2u);
    return value;
}
static uint8_t scroll_alignment(void *object, uint32_t horizontal) {
    const uint8_t *const spec = (const uint8_t *)(uintptr_t)rd32((const uint8_t *)object + 8u);
    if (spec == 0) return 0u;
    const uint16_t flags = rd16(spec + 0x32u);
    return horizontal ? (uint8_t)((flags & 0x000fu) >> 2u)
                      : (uint8_t)((flags & 0x003fu) >> 4u);
}
static int32_t space(void *object, uint32_t property, uint32_t side,
                     int32_t (*raw)(void *, uint32_t)) {
    const int32_t padding = raw(object, 0u);
    const int32_t border = (int32_t)audio_uart_lv_style_property_44bdea(object, 0u, 0x30u);
    const uint8_t sides = (uint8_t)audio_uart_lv_style_property_44bdea(object, 0u, 0x34u);
    (void)property;
    return (sides & side) != 0u ? add32(padding, border) : padding;
}

void audio_uart_lv_scroll_view_step_44f40c(const int32_t *area, void *object,
                                            int32_t offset[2], uint32_t animated) {
    uint8_t *const parent = (uint8_t *)audio_uart_lv_obj_parent_44dca2(object);
    if (audio_uart_lv_obj_has_flag_43e0e0(parent, 0x10u) == 0u) return;
    const uint32_t directions = audio_uart_lv_get_scroll_dir_44e442(parent);

    const int32_t *vertical_area = area;
    const uint8_t vertical_mode = scroll_alignment(parent, 0u);
    if (vertical_mode != 0u) vertical_area = (const int32_t *)((const uint8_t *)object + 0x14u);
    const int32_t top = space(parent, 0x10u, 2u, audio_uart_lv_style_raw_pad_top_44e230);
    const int32_t bottom = space(parent, 0x11u, 1u, audio_uart_lv_style_raw_pad_bottom_44e23a);
    const int32_t below = sub32(sub32(add32(top, (int32_t)rd32(parent + 0x18u)),
                                      vertical_area[1]), offset[1]);
    const int32_t above = add32(add32(vertical_area[3], bottom),
                                sub32(offset[1], (int32_t)rd32(parent + 0x20u)));
    int32_t dy = 0;
    const int32_t parent_height = audio_uart_lv_obj_height_43fdda(parent);
    if (below < 0 || above < 0) {
        if (below < 1) {
            if (above > 0) {
                dy = neg32(above);
                if (add32(dy, audio_uart_lv_scroll_bottom_44e4bc(parent)) < 0) dy = 0;
            }
        } else {
            dy = below;
            if (sub32(audio_uart_lv_scroll_top_44e4aa(parent), below) < 0) dy = 0;
        }
    }
    if (vertical_mode == 2u) {
        dy = sub32(sub32((int32_t)rd32(parent + 0x20u), bottom), vertical_area[3]);
    } else if (vertical_mode == 1u) {
        dy = sub32(add32(top, (int32_t)rd32(parent + 0x18u)), vertical_area[1]);
    } else if (vertical_mode == 3u) {
        const int32_t extent = audio_uart_lv_area_height_4515a4(vertical_area);
        const int32_t half = sub32(sub32(parent_height, top), bottom) / 2;
        dy = sub32(add32(add32(half, top), (int32_t)rd32(parent + 0x18u)),
                   add32(vertical_area[1], extent / 2));
    }

    const uint8_t horizontal_mode = scroll_alignment(parent, 1u);
    const int32_t *horizontal_area = area;
    if (horizontal_mode != 0u) horizontal_area = (const int32_t *)((const uint8_t *)object + 0x14u);
    const int32_t left = space(parent, 0x12u, 4u, audio_uart_lv_style_raw_pad_left_44e244);
    const int32_t right = space(parent, 0x13u, 8u, audio_uart_lv_style_raw_pad_right_44e24e);
    const int32_t before = sub32(sub32(add32(left, (int32_t)rd32(parent + 0x14u)),
                                       horizontal_area[0]), offset[0]);
    const int32_t after = add32(add32(horizontal_area[2], right),
                                sub32(offset[0], (int32_t)rd32(parent + 0x1cu)));
    int32_t dx = 0;
    if (before < 0 || after < 0) {
        if (before < 1) {
            if (after > 0) {
                dx = neg32(after);
                if (add32(dx, audio_uart_lv_scroll_right_44e67a(parent)) < 0) dx = 0;
            }
        } else {
            dx = before;
            if (sub32(audio_uart_lv_scroll_left_44e586(parent), before) < 0) dx = 0;
        }
    }
    const int32_t parent_width = audio_uart_lv_obj_width_43fd9e(parent);
    if (horizontal_mode == 2u) {
        dx = sub32(sub32((int32_t)rd32(parent + 0x1cu), right), horizontal_area[2]);
    } else if (horizontal_mode == 1u) {
        dx = sub32(add32(left, (int32_t)rd32(parent + 0x14u)), horizontal_area[0]);
    } else if (horizontal_mode == 3u) {
        const int32_t extent = audio_uart_lv_area_width_451598(horizontal_area);
        const int32_t half = sub32(sub32(parent_width, left), right) / 2;
        dx = sub32(add32(add32(half, left), (int32_t)rd32(parent + 0x14u)),
                   add32(horizontal_area[0], extent / 2));
    }

    audio_uart_lv_style_unlink_450500(parent, (void *)audio_uart_lv_scroll_anim_y_44f3d4);
    audio_uart_lv_style_unlink_450500(parent, (void *)audio_uart_lv_scroll_anim_x_44f3b8);
    if ((directions & 1u) == 0u && dx < 0) dx = 0;
    if ((directions & 2u) == 0u && dx > 0) dx = 0;
    if ((directions & 4u) == 0u && dy < 0) dy = 0;
    if ((directions & 8u) == 0u && dy > 0) dy = 0;
    if ((uint8_t)animated != 0u) {
        offset[0] = add32(offset[0], dx);
        offset[1] = add32(offset[1], dy);
    }
    audio_uart_lv_scroll_dispatch_44e884(parent, dx, dy, (uint8_t)animated);
}
