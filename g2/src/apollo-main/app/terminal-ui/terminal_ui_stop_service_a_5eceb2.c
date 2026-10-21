/* Stock terminal timer/object cleanup 0x5eceb2. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *);
extern void audio_uart_page_delete_event_filter_44d7b8(void *);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

void audio_terminal_ui_stop_service_a_5eceb2(void) {
    uint8_t *const state = audio_terminal_ui_state_base;
    uint32_t *const slot = (uint32_t *)(void *)(state + 0x240u);
    if (slot[0] != 0u &&
        audio_terminal_ui_object_valid_43e2ea((void *)(uintptr_t)slot[0]) != 0u)
        audio_uart_page_delete_event_filter_44d7b8((void *)(uintptr_t)slot[0]);
    slot[0] = 0u;
    slot[1] = 0u;
    audio_uart_buffer_zero(state + 0x248u, 0x2cu, 0u);
    state[0x27du] = 0u;
}
