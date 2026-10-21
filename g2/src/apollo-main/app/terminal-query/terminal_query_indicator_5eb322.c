/* Stock Terminal query-indicator offset 0x5eb2ee and layout 0x5eb322. */
#include <stdint.h>

extern uint32_t audio_uart_ring_secondary_head_cell; /* stock 0x200746e0 */
extern uint32_t audio_terminal_query_count_5eb30c(void);
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern int32_t audio_uart_lv_obj_x_43fc70(void *);
extern int32_t audio_uart_lv_obj_y_43fce0(void *);
extern void audio_lv_object_flag_43ded4(uint32_t, uint32_t);
extern void audio_lv_object_clear_flag_43dfa4(uint32_t, uint32_t);
extern void audio_lv_object_position_43f09a(uint32_t, uint32_t, uint32_t);

int32_t audio_terminal_query_indicator_offset_5eb2ee(void) {
    const uint8_t *const font =
        (const uint8_t *)(uintptr_t)audio_uart_ring_secondary_head_cell;
    const int32_t height =
        *(const int32_t *)(const void *)(font + 0x0cu);
    return height > 16 ? (height - 16) / 2 : 0;
}

static uint32_t word(const uint8_t *state, uint32_t offset) {
    return *(const uint32_t *)(const void *)(state + offset);
}

void audio_terminal_query_indicator_5eb322(uint32_t state_address) {
    if (state_address == 0u)
        return;
    const uint8_t *const state = (const uint8_t *)(uintptr_t)state_address;
    const uint32_t indicator = word(state, 0x220u);
    const uint32_t list = word(state, 0x21cu);
    if (indicator == 0u || list == 0u)
        return;
    if (state[0x27cu] != 0u ||
        state[0x279u] >= audio_terminal_query_count_5eb30c()) {
        audio_lv_object_flag_43ded4(indicator, 1u);
        return;
    }
    const uint32_t child = audio_lv_child_44dce2(list, state[0x279u]);
    if (child == 0u) {
        audio_lv_object_flag_43ded4(indicator, 1u);
        return;
    }
    const int32_t y = audio_uart_lv_obj_y_43fce0((void *)(uintptr_t)list) +
                      audio_uart_lv_obj_y_43fce0((void *)(uintptr_t)child) +
                      audio_terminal_query_indicator_offset_5eb2ee();
    const int32_t x = audio_uart_lv_obj_x_43fc70((void *)(uintptr_t)list) - 20;
    audio_lv_object_position_43f09a(indicator, (uint32_t)x, (uint32_t)y);
    audio_lv_object_clear_flag_43dfa4(indicator, 1u);
}
