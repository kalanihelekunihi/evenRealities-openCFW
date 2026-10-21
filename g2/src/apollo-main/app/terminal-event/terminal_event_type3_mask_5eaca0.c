/* Stock Terminal type-three indexed update at 0x5eaca0. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_resource_597324(void);
extern uint32_t audio_terminal_item_59737c(uint32_t index);
extern uint32_t audio_terminal_item_height_5ea67a(uint32_t item);
extern void audio_terminal_event_default_5eaad4(const uint8_t *input);
extern void audio_terminal_view_row_5ea768(uint32_t row, uint32_t index);
extern void audio_terminal_event_apply_input_5eaa96(const uint8_t *input);
extern void audio_terminal_recompute_offsets_5ea6da(uint32_t first);
extern void audio_terminal_event_refresh_view_5ea992(void);
extern int32_t audio_uart_lv_obj_y_44e498(void *object);
extern void audio_terminal_view_position_5ea926(uint32_t position);

void audio_terminal_event_type3_mask_5eaca0(uint32_t raw_index,
                                             const uint8_t *input) {
    uint8_t *state = audio_terminal_ui_state_base;
    uint32_t root = *(uint32_t *)(void *)(state + 4u);
    if (root == 0u)
        return;
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    uint16_t index = (uint16_t)raw_index;
    if (count == 0u || index >= count || count !=
        *(uint16_t *)(void *)(state + 0x1c4u)) {
        audio_terminal_event_default_5eaad4(input);
        return;
    }
    uint32_t item = audio_terminal_item_59737c(index);
    if (item == 0u) {
        audio_terminal_event_default_5eaad4(input);
        return;
    }
    uint16_t height = (uint16_t)audio_terminal_item_height_5ea67a(item);
    uint16_t prior = *(uint16_t *)(void *)(state + 0x3cu + (uint32_t)index * 2u);
    if (height == prior) {
        uint16_t first = *(uint16_t *)(void *)(state + 0x1c0u);
        if (state[0x1c2u] != 0u && index >= first &&
            index < (uint16_t)(first + 12u))
            audio_terminal_view_row_5ea768((uint16_t)(index - first), index);
        if (input != 0 && input[0] != 0u)
            audio_terminal_event_apply_input_5eaa96(input);
        return;
    }
    *(uint16_t *)(void *)(state + 0x3cu + (uint32_t)index * 2u) = height;
    audio_terminal_recompute_offsets_5ea6da(index);
    state[0x1c2u] = 0u;
    if (input != 0 && input[0] != 0u) {
        audio_terminal_event_apply_input_5eaa96(input);
    } else if (state[0x28cu] != 0u && index == (uint16_t)(count - 1u)) {
        audio_terminal_event_refresh_view_5ea992();
    } else {
        audio_terminal_view_position_5ea926(
            (uint32_t)audio_uart_lv_obj_y_44e498((void *)(uintptr_t)root));
    }
}
