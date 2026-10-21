/* Stock Terminal 12-row view selection at 0x5ea810. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_resource_597324(void);
extern void audio_lv_object_flag_43ded4(uint32_t object, uint32_t flag);
extern void audio_terminal_view_row_5ea768(uint32_t slot, uint32_t item_index);

void audio_terminal_view_select_5ea810(uint32_t first) {
    uint8_t *state = audio_terminal_ui_state_base;
    uint32_t resource = audio_terminal_resource_597324();
    uint16_t count = resource != 0u
        ? *(const uint16_t *)(const void *)(uintptr_t)(resource + 0x8500u) : 0u;
    for (uint32_t slot = 0; slot < 12u; ++slot) {
        uint32_t object = *(const uint32_t *)(const void *)(state + 0xcu + slot * 4u);
        if (object == 0u)
            continue;
        uint32_t item_index = (uint16_t)first + slot;
        if (item_index >= count)
            audio_lv_object_flag_43ded4(object, 1u);
        else
            audio_terminal_view_row_5ea768(slot, (uint16_t)item_index);
    }
    *(uint16_t *)(void *)(state + 0x1c0u) = (uint16_t)first;
    state[0x1c2u] = 1u;
}
