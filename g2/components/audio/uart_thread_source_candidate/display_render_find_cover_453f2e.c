/* Apollo Main LVGL recursive cover finder, stock 0x453f2e..0x453fce. */
#include <stdint.h>

extern uint32_t audio_uart_lv_area_contains_450f28(const void *,
                                                    const void *, uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_mode_452dd8(void *);
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t,
                                                     uint32_t);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);

typedef struct {
    uint8_t result;
    uint8_t padding[3];
    const void *area;
} cover_event_t;

void *audio_uart_lv_render_find_cover_453f2e(const void *area, void *object)
{
    const uint8_t *const bytes = (const uint8_t *)object;
    if (audio_uart_lv_area_contains_450f28(area, bytes + 0x14u, 0u) == 0u)
        return 0;
    if (audio_uart_lv_obj_has_flag_43e0e0(object, 1u) != 0u)
        return 0;
    if (audio_uart_lv_scrollbar_mode_452dd8(object) != 0u)
        return 0;
    if ((int32_t)(uint8_t)audio_uart_lv_style_property_44bdea(
            object, 0u, 0x62u) < 0xfd)
        return 0;
    cover_event_t event = {0u, {0u, 0u, 0u}, area};
    (void)audio_uart_lv_obj_event_451670(object, 0x1au, &event);
    if (event.result == 2u) return 0;
    const uint32_t count = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t index = count; index != 0u; --index) {
        const uint32_t vector = *(const uint32_t *)(const void *)(bytes + 8u);
        const uint32_t table = *(const uint32_t *)(uintptr_t)vector;
        void *const child = (void *)(uintptr_t)
            *(const uint32_t *)(uintptr_t)(table + (index - 1u) * 4u);
        void *const found = audio_uart_lv_render_find_cover_453f2e(area, child);
        if (found != 0) return found;
    }
    return event.result == 0u ? object : 0;
}
