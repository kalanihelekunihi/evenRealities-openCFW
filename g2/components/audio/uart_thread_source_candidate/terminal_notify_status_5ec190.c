/* Stock Terminal status-change UI child at 0x5ec190. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_status_apply_layout_5ebc9e(uint32_t state,
                                                       uint32_t mode);
extern uint32_t audio_uart_page_44104c(uint32_t rgb);
extern void audio_uart_page_44140e(uint32_t object, uint32_t color,
                                    uint32_t selector);
extern void audio_uart_page_43dfa4(uint32_t object, uint32_t flag);
extern void audio_uart_page_43ded4(uint32_t object, uint32_t value);
extern void audio_terminal_status_publish_5e5498(uint32_t event,
                                                   uint32_t value);

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

void audio_terminal_notify_status_5ec190(void) {
    uint32_t root = word(0x208u);
    uint32_t first = word(0x20cu);
    uint32_t second = word(0x210u);
    if (root == 0u || first == 0u || second == 0u)
        return;
    uint8_t status = audio_terminal_ui_state_base[0x278u];
    if (status == 0u || status == 1u) {
        audio_terminal_status_apply_layout_5ebc9e(
            (uint32_t)(uintptr_t)audio_terminal_ui_state_base, status);
        if (status == 0u) {
            uint32_t color = audio_uart_page_44104c(0x00ffffffu);
            audio_uart_page_44140e(first, color, 0u);
            color = audio_uart_page_44104c(0x00333333u);
            audio_uart_page_44140e(second, color, 0u);
        } else {
            uint32_t color = audio_uart_page_44104c(0x00333333u);
            audio_uart_page_44140e(first, color, 0u);
            color = audio_uart_page_44104c(0x00ffffffu);
            audio_uart_page_44140e(second, color, 0u);
        }
        audio_uart_page_43dfa4(root, 1u);
        audio_terminal_status_publish_5e5498(2u, status == 1u ? 1u : 0u);
    } else {
        audio_uart_page_43ded4(root, 1u);
        uint32_t gray = audio_uart_page_44104c(0x00333333u);
        audio_uart_page_44140e(first, gray, 0u);
        gray = audio_uart_page_44104c(0x00333333u);
        audio_uart_page_44140e(second, gray, 0u);
    }
}
