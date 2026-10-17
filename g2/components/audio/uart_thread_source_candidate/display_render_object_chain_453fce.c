/* Apollo Main LVGL selected-object render and ancestor sibling walk,
 * stock 0x453fce..0x454074. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_display_active_screen_get(void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_draw_color_chain_44c582(void *, uint32_t);
extern void audio_uart_lv_draw_object_4541b6(void *, void *);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);

static uint32_t read32(const uint8_t *bytes, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void write32(uint8_t *bytes, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_render_object_chain_453fce(void *layer, void *object)
{
    if (object == 0) {
        void *const display = (void *)(uintptr_t)read32(
            audio_uart_display_lv_root, 0x10u);
        object = audio_uart_display_active_screen_get(display);
    }
    if (object == 0) return;

    void *current = object;
    void *parent = audio_uart_lv_obj_parent_44dca2(object);
    if (parent != 0) {
        const uint32_t color = audio_uart_lv_draw_color_chain_44c582(parent, 0u);
        write32((uint8_t *)layer, 0x39u, color);
    }
    audio_uart_lv_draw_object_4541b6(layer, object);

    while (parent != 0) {
        uint8_t seen = 0u;
        const uint32_t count = audio_uart_lv_child_count_44ddea(parent);
        const uint8_t *const bytes = (const uint8_t *)parent;
        for (uint32_t index = 0u; index < count; ++index) {
            const uint32_t vector = read32(bytes, 8u);
            const uint32_t table = *(const uint32_t *)(uintptr_t)vector;
            void *const child = (void *)(uintptr_t)
                *(const uint32_t *)(uintptr_t)(table + index * 4u);
            if (seen == 0u) {
                if (child == current) seen = 1u;
            } else {
                audio_uart_lv_draw_object_4541b6(layer, child);
            }
        }
        (void)audio_uart_lv_obj_event_451670(parent, 0x1fu, layer);
        (void)audio_uart_lv_obj_event_451670(parent, 0x20u, layer);
        (void)audio_uart_lv_obj_event_451670(parent, 0x21u, layer);
        current = parent;
        parent = audio_uart_lv_obj_parent_44dca2(parent);
    }
}
