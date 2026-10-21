/* Native Conversate UI scroll routes 0x5b5ed2 and 0x5b5ef6. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_lv_child_44dce2(uint32_t parent, uint32_t index);
extern void audio_terminal_display_status_44ea04(uint32_t object,
                                                  uint32_t target,
                                                  uint32_t animated);

static uint32_t scroll_selected_child(uint32_t value) {
    const uint32_t parent = *(const uint32_t *)(const void *)(
        audio_conversate_ui_settings_extension_20071369 + 0x1bu);
    const uint32_t child = audio_lv_child_44dce2(parent, 1u);
    if (child != 0u)
        audio_terminal_display_status_44ea04(child, value, 1u);
    return 0u;
}

uint32_t audio_conversate_ui_route_5b5ed2(uint32_t state, uint32_t value) {
    (void)state;
    return scroll_selected_child(value);
}

uint32_t audio_conversate_ui_route_5b5ef6(uint32_t state, uint32_t value) {
    (void)state;
    return scroll_selected_child(value);
}
