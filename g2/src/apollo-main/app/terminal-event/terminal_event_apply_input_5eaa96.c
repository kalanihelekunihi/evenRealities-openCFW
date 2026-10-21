/* Stock Terminal event input application at 0x5eaa96. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_event_refresh_view_5ea992(void);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_view_position_5ea926(uint32_t);

void audio_terminal_event_apply_input_5eaa96(const uint8_t *input) {
    if (input == 0 || input[0] == 0u)
        return;
    uint32_t root = *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + 4u);
    if (root == 0u)
        return;
    uint8_t flag = input[1];
    audio_terminal_ui_state_base[0x28cu] = flag;
    if (flag != 0u) {
        audio_terminal_event_refresh_view_5ea992();
        return;
    }
    uint32_t position = *(const uint32_t *)(const void *)(input + 4u);
    audio_terminal_display_status_44ea04(root, position, 0u);
    audio_terminal_view_position_5ea926(position);
}
