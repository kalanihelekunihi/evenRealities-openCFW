/* Stock Terminal type-two incremental event at 0x5eabde. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_resource_597324(void);
extern uint32_t audio_terminal_last_record_597350(void);
extern uint32_t audio_terminal_item_height_5ea67a(uint32_t item);
extern void audio_terminal_recompute_offsets_5ea6da(uint32_t first);
extern void audio_terminal_event_apply_input_5eaa96(const uint8_t *input);
extern void audio_terminal_event_default_5eaad4(const uint8_t *input);
extern void audio_terminal_list_rollover_5eab8e(void);
extern void audio_terminal_event_refresh_view_5ea992(void);
extern int32_t audio_uart_lv_obj_y_44e498(void *object);
extern void audio_terminal_view_position_5ea926(uint32_t position);

void audio_terminal_event_type2_5eabde(const uint8_t *input) {
    uint8_t *state = audio_terminal_ui_state_base;
    uint32_t root = *(const uint32_t *)(const void *)(state + 4u);
    if (root == 0u)
        return;
    uint32_t resource = audio_terminal_resource_597324();
    uint32_t last = audio_terminal_last_record_597350();
    if (resource == 0u || last == 0u)
        return;
    uint16_t count = *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u);
    if (count == 0u)
        return;
    uint16_t prior_count = *(const uint16_t *)(const void *)(state + 0x1c4u);
    uint8_t rolled = 0u;
    if (count == (uint16_t)(prior_count + 1u)) {
        uint16_t index = (uint16_t)(count - 1u);
        *(uint16_t *)(void *)(state + 0x3cu + (uint32_t)index * 2u) =
            (uint16_t)audio_terminal_item_height_5ea67a(last);
        audio_terminal_recompute_offsets_5ea6da(index);
    } else if (count == 0x40u && prior_count == 0x40u) {
        audio_terminal_list_rollover_5eab8e();
        rolled = 1u;
    } else {
        audio_terminal_event_default_5eaad4(input);
        return;
    }
    *(uint16_t *)(void *)(state + 0x1c4u) = count;
    state[0x1c2u] = 0u;
    if (input != 0 && input[0] != 0u) {
        audio_terminal_event_apply_input_5eaa96(input);
        if (rolled != 0u)
            audio_terminal_view_position_5ea926(
                (uint32_t)audio_uart_lv_obj_y_44e498((void *)(uintptr_t)root));
    } else if (state[0x28cu] != 0u) {
        audio_terminal_event_refresh_view_5ea992();
    } else {
        audio_terminal_view_position_5ea926(
            (uint32_t)audio_uart_lv_obj_y_44e498((void *)(uintptr_t)root));
    }
}
