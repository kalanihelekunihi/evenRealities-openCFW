/* Stock Terminal event view refresh at 0x5ea992. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_resource_597324(void);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_terminal_view_position_5ea926(uint32_t);

void audio_terminal_event_refresh_view_5ea992(void) {
    uint8_t *state = audio_terminal_ui_state_base;
    uint32_t root = *(const uint32_t *)(const void *)(state + 4u);
    if (root == 0u)
        return;
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    if (count == 0u) {
        audio_terminal_display_status_44ea04(root, 0u, 0u);
        state[0x28cu] = 1u;
        return;
    }
    if (state[0x28cu] == 0u)
        return;
    uint32_t current = (uint32_t)audio_uart_lv_obj_height_43fdda((void *)(uintptr_t)root);
    int32_t delta = (int32_t)(*(const uint32_t *)(const void *)(state + 0x1c8u) - current);
    if (delta < 0)
        delta = 0;
    audio_terminal_display_status_44ea04(root, (uint32_t)delta, 0u);
    audio_terminal_view_position_5ea926((uint32_t)delta);
}
