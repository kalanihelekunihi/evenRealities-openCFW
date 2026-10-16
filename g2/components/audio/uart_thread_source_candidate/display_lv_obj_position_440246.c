#include <stdint.h>

typedef struct { int32_t x1, y1, x2, y2; } lv_area_440246;
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *, uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *, uint32_t);
extern void audio_uart_page_invalidate_440656(void *);
extern void audio_uart_lv_obj_coords_43fc2a(void *, lv_area_440246 *);
extern void audio_uart_lv_obj_content_coords_43feca(void *, lv_area_440246 *);
extern uint32_t audio_uart_lv_area_contains_450f28(const lv_area_440246 *, const lv_area_440246 *, uint32_t);
extern void audio_uart_lv_scrollbar_invalidate_44f2ca(void *);
extern void audio_uart_lv_obj_move_children_44035e(void *, int32_t, int32_t, uint32_t);
extern void audio_uart_lv_obj_event_451670(void *, uint32_t, void *);

static uint32_t get32(const void *p, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)p + offset);
}
static void put32(void *p, uint32_t offset, uint32_t value) {
    *(uint32_t *)((uint8_t *)p + offset) = value;
}

void audio_uart_lv_obj_position_440246(void *object, int32_t x, int32_t y) {
    void *parent = (void *)(uintptr_t)get32(object, 4u);
    uint32_t target_x = (uint32_t)x;
    uint32_t target_y = (uint32_t)y;
    if (parent != 0) {
        if (audio_uart_lv_obj_has_flag_43e0e0(object, 0x40000u) != 0u) {
            target_x += get32(parent, 0x14u);
            target_y += get32(parent, 0x18u);
        } else {
            const int32_t scroll_x = audio_uart_lv_obj_x_44e486(parent);
            target_x += get32(parent, 0x14u) - (uint32_t)scroll_x;
            const int32_t scroll_y = audio_uart_lv_obj_y_44e498(parent);
            target_y += get32(parent, 0x18u) - (uint32_t)scroll_y;
        }
        target_x += (uint32_t)audio_uart_lv_style_pad_left_43efc6(parent, 0u);
        target_y += (uint32_t)audio_uart_lv_style_pad_top_43f022(parent, 0u);
    }
    const int32_t dx = (int32_t)(target_x - get32(object, 0x14u));
    const int32_t dy = (int32_t)(target_y - get32(object, 0x18u));
    if (dx == 0 && dy == 0) return;

    audio_uart_page_invalidate_440656(object);
    lv_area_440246 old_area;
    audio_uart_lv_obj_coords_43fc2a(object, &old_area);
    lv_area_440246 parent_area;
    uint8_t was_contained = 0u;
    if (parent != 0) {
        audio_uart_lv_obj_content_coords_43feca(parent, &parent_area);
        was_contained = (uint8_t)audio_uart_lv_area_contains_450f28(&old_area, &parent_area, 0u);
        if (was_contained == 0u) audio_uart_lv_scrollbar_invalidate_44f2ca(parent);
    }

    put32(object, 0x14u, get32(object, 0x14u) + (uint32_t)dx);
    put32(object, 0x18u, get32(object, 0x18u) + (uint32_t)dy);
    put32(object, 0x1cu, get32(object, 0x1cu) + (uint32_t)dx);
    put32(object, 0x20u, get32(object, 0x20u) + (uint32_t)dy);
    audio_uart_lv_obj_move_children_44035e(object, dx, dy, 0u);
    if (parent != 0) audio_uart_lv_obj_event_451670(parent, 0x2au, object);
    audio_uart_page_invalidate_440656(object);
    if (parent != 0) {
        const uint8_t is_contained = (uint8_t)audio_uart_lv_area_contains_450f28(
            (const lv_area_440246 *)((uint8_t *)object + 0x14u), &parent_area, 0u);
        if (was_contained != 0u || is_contained != 0u)
            audio_uart_lv_scrollbar_invalidate_44f2ca(parent);
    }
}
