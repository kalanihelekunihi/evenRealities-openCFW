/* Stock Terminal notification text/scroll refresh at 0x5ebfae. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern const char *audio_uart_page_49942e(uint8_t *, const char *);
extern void audio_terminal_ui_scroll_to_view_44ea2e(void *, uint32_t);

static uint32_t load32(uint32_t offset) {
    return *(uint32_t *)(void *)(audio_terminal_ui_state_base + offset);
}

void audio_terminal_ui_notification_restore_5ebfae(uint32_t record) {
    uint32_t label = load32(0x1fcu);
    if (label == 0u)
        return;
    (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,
                                  (const char *)(uintptr_t)record);
    if (load32(0x1f4u) != 0u) {
        uint32_t scroll = load32(0x200u);
        if (scroll != 0u)
            audio_terminal_ui_scroll_to_view_44ea2e(
                (void *)(uintptr_t)scroll, 0u);
    }
}
