/* Apollo Main Conversate close timer label, native 0x5b68d6..0x5b6941. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_state_20071368;
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *);
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(uint32_t, uint32_t);
extern void audio_lv_label_set_text_fmt_49954c(uint32_t, uint32_t, uint32_t);

static const char close_in_seconds[] = "ID_CONVERSATE_CLOSE_IN_X_SEC";

uint32_t audio_conversate_ui_route_5b68d6(uint32_t ignored, uint32_t seconds) {
    (void)ignored;
    const volatile uint8_t *const state = &audio_conversate_ui_state_20071368;
    const uint32_t root = *(const volatile uint32_t *)(const void *)(state + 0x1cu);
    if (root == 0u || state[0x96u] != 0u)
        return UINT32_MAX;
    const uint32_t first = audio_lv_child_44dce2(root, 0u);
    if (audio_terminal_ui_object_valid_43e2ea((void *)(uintptr_t)first) == 0u)
        return UINT32_MAX;
    const uint32_t label = audio_lv_child_44dce2(first, 2u);
    if (audio_terminal_ui_object_valid_43e2ea((void *)(uintptr_t)label) == 0u)
        return UINT32_MAX;
    const uint32_t index = audio_uart_page_460084(close_in_seconds);
    const uint32_t format = audio_uart_page_45fffe(
        (uint32_t)(uintptr_t)close_in_seconds, index);
    audio_lv_label_set_text_fmt_49954c(label, format, seconds);
    return 0u;
}
