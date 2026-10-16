/* Stock terminal result-area cleanup 0x5ec9c0. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_uart_page_delete_event_filter_44d7b8(void *);

void audio_terminal_ui_stop_service_e_5ec9c0(void) {
    uint32_t *const result =
        (uint32_t *)(void *)(audio_terminal_ui_state_base + 0x224u);
    if (result[0] != 0u) {
        audio_uart_page_delete_event_filter_44d7b8(
            (void *)(uintptr_t)result[0]);
        result[0] = 0u;
        result[1] = 0u;
        result[2] = 0u;
    }
}
