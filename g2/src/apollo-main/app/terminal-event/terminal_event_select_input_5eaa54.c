/* Stock Terminal event input selector at 0x5eaa54. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern int32_t audio_uart_lv_obj_y_44e498(void *object);

void audio_terminal_event_select_input_5eaa54(const uint8_t *input,
                                              uint32_t *position,
                                              uint8_t *flag) {
    if (position == 0 || flag == 0)
        return;
    if (input != 0 && input[0] != 0u) {
        *position = *(const uint32_t *)(const void *)(input + 4u);
        *flag = input[1];
        return;
    }
    uint32_t root = *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + 4u);
    *position = root != 0u ? (uint32_t)audio_uart_lv_obj_y_44e498((void *)(uintptr_t)root) : 0u;
    *flag = audio_terminal_ui_state_base[0x28cu];
}
