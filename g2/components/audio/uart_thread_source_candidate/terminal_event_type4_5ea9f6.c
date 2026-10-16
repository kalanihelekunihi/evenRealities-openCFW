/* Stock Terminal type-four event reset 0x5ea9f6. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_lv_object_size_call_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_event_reset_list_5ea7dc(void);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);

void audio_terminal_event_type4_5ea9f6(void) {
    uint8_t *state = audio_terminal_ui_state_base;
    audio_uart_buffer_zero(state + 0x3cu, 0x80u, 0u);
    audio_uart_buffer_zero(state + 0xbcu, 0x104u, 0u);
    *(uint32_t *)(void *)(state + 0x1c8u) = 0u;
    *(uint16_t *)(void *)(state + 0x1c4u) = 0u;
    uint32_t child = *(const uint32_t *)(const void *)(state + 8u);
    if (child != 0u)
        audio_lv_object_size_call_43f4c0(child, 0x240u, 0u);
    audio_terminal_event_reset_list_5ea7dc();
    uint32_t root = *(const uint32_t *)(const void *)(state + 4u);
    if (root != 0u)
        audio_terminal_display_status_44ea04(root, 0u, 0u);
    state[0x28cu] = 1u;
}
