/* Stock session count, validity, object lookup and selection at
 * 0x5eca48/0x5eca64/0x5ecb52/0x5ecc1a. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint8_t *audio_td_active_session(void);
extern uint32_t audio_terminal_session_animate_5896fc(uint32_t, uint32_t,
                                                       uint32_t);
extern void audio_terminal_session_apply_5ecb88(int32_t);
extern void audio_terminal_session_focus_5ecbea(int32_t);

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

__attribute__((noinline)) uint32_t audio_terminal_session_count_5eca48(void) {
    const uint8_t *const active = audio_td_active_session();
    if (active == 0)
        return 0u;
    const uint32_t count = *(const uint32_t *)(const void *)(active + 8u);
    return count < 11u ? count : 10u;
}

__attribute__((noinline)) uint32_t audio_terminal_session_valid_5eca64(int32_t index) {
    const int32_t selected = (int16_t)index;
    return selected >= 0 && (uint32_t)selected <
        audio_terminal_session_count_5eca48();
}

__attribute__((noinline)) uint32_t audio_terminal_session_object_5ecb52(int32_t index) {
    const int32_t selected = (int16_t)index;
    if (selected == -1)
        return word(0x248u);
    if (audio_terminal_session_valid_5eca64(selected) == 0u)
        return 0u;
    return word(0x24cu + (uint32_t)selected * 4u);
}

void audio_terminal_session_select_5ecc1a(int32_t index) {
    const int16_t selected = (int16_t)index;
    const int16_t prior = *(const int16_t *)(const void *)(
        audio_terminal_ui_state_base + 0x27au);
    if (selected == prior)
        return;
    const uint32_t from = audio_terminal_session_object_5ecb52(prior);
    const uint32_t to = audio_terminal_session_object_5ecb52(selected);
    uint32_t animated = 0u;
    if (from != 0u || to != 0u)
        animated = audio_terminal_session_animate_5896fc(from, to, 200u) & 0xffu;
    if (animated == 0u)
        audio_terminal_session_apply_5ecb88(selected);
    else
        *(int16_t *)(void *)(audio_terminal_ui_state_base + 0x27au) = selected;
    audio_terminal_session_focus_5ecbea(selected);
}
