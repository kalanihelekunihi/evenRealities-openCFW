/* Stock Terminal query count 0x5eb30c and item styles 0x5eb3c6. */
#include <stdint.h>

extern uint8_t *audio_td_session_struct_ptr(void);
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern uint32_t audio_lv_color_44104c(uint32_t);
extern void audio_lv_style_color_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_query_indicator_5eb322(uint32_t);

__attribute__((noinline)) uint32_t audio_terminal_query_count_5eb30c(void) {
    const uint8_t *const session = audio_td_session_struct_ptr();
    if (session == 0)
        return 0u;
    return *(const uint16_t *)(const void *)(session + 0x406u) & 0xffu;
}

void audio_terminal_query_items_style_5eb3c6(uint32_t state_address) {
    if (state_address == 0u)
        return;
    const uint8_t *const state = (const uint8_t *)(uintptr_t)state_address;
    const uint32_t list = *(const uint32_t *)(const void *)(state + 0x21cu);
    if (list == 0u)
        return;
    const uint32_t count = audio_terminal_query_count_5eb30c();
    for (uint32_t index = 0; index < count; ++index) {
        const uint32_t child = audio_lv_child_44dce2(list, index);
        if (child == 0u)
            continue;
        uint32_t rgb = 0x00333333u;
        if (state[0x27cu] == 0u && index == state[0x279u])
            rgb = 0x00ffffffu;
        audio_lv_style_color_44140e(child, audio_lv_color_44104c(rgb), 0u);
    }
    audio_terminal_query_indicator_5eb322(state_address);
}
