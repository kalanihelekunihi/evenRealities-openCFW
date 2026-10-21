/* Stock Terminal default event handler at 0x5eaad4. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_event_select_input_5eaa54(const uint8_t *, uint32_t *, uint8_t *);
extern void audio_terminal_event_type4_5ea9f6(void);
extern uint32_t audio_terminal_resource_597324(void);
extern uint32_t audio_terminal_item_59737c(uint32_t);
extern uint32_t audio_terminal_item_height_5ea67a(uint32_t);
extern void audio_terminal_recompute_offsets_5ea6da(uint32_t);
extern void audio_terminal_event_apply_input_5eaa96(const uint8_t *);
extern void audio_terminal_event_refresh_view_5ea992(void);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_view_position_5ea926(uint32_t);

void audio_terminal_event_default_5eaad4(const uint8_t *input) {
    uint8_t *state = audio_terminal_ui_state_base;
    uint32_t root = *(const uint32_t *)(const void *)(state + 4u);
    if (root == 0u)
        return;
    uint32_t position = 0u;
    uint8_t flag = 0u;
    audio_terminal_event_select_input_5eaa54(input, &position, &flag);
    audio_terminal_event_type4_5ea9f6();
    state[0x28cu] = flag;
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    if (count == 0u)
        return;
    for (uint32_t index = 0; index < count; ++index) {
        uint32_t item = audio_terminal_item_59737c((uint16_t)index);
        uint16_t height = item != 0u
            ? (uint16_t)audio_terminal_item_height_5ea67a(item) : 0x1cu;
        *(uint16_t *)(void *)(state + 0x3cu + index * 2u) = height;
    }
    audio_terminal_recompute_offsets_5ea6da(0u);
    *(uint16_t *)(void *)(state + 0x1c4u) = count;
    state[0x1c2u] = 0u;
    if (input != 0 && input[0] != 0u) {
        audio_terminal_event_apply_input_5eaa96(input);
    } else if (state[0x28cu] != 0u) {
        audio_terminal_event_refresh_view_5ea992();
    } else {
        audio_terminal_display_status_44ea04(root, position, 0u);
        audio_terminal_view_position_5ea926(position);
    }
}
