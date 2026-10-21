/* Stock Terminal view-position decision at 0x5ea926. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_resource_597324(void);
extern uint32_t audio_terminal_view_index_5ea8ce(uint32_t position);
extern void audio_terminal_view_select_5ea810(uint32_t index);

void audio_terminal_view_position_5ea926(uint32_t position) {
    uint8_t *state = audio_terminal_ui_state_base;
    if (*(const uint32_t *)(const void *)(state + 8u) == 0u)
        return;
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    if (count == 0u)
        return;
    uint16_t index = (uint16_t)audio_terminal_view_index_5ea8ce(position);
    if (state[0x1c2u] != 0u &&
        *(const uint16_t *)(const void *)(state + 0x1c0u) == index)
        return;
    audio_terminal_view_select_5ea810(index);
}
