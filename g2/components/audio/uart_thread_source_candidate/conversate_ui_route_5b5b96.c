/* Native Conversate UI previous-item route at 0x5b5b96. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern void *audio_conversate_reply_list_get_5b43e8(void);
extern uint32_t audio_lv_child_44dce2(uint32_t parent, uint32_t index);
extern uint32_t audio_terminal_session_animate_5896fc(uint32_t old_object,
                                                        uint32_t new_object,
                                                        uint32_t duration);

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_conversate_ui_settings_extension_20071369 + offset);
}

static void set_word(uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(audio_conversate_ui_settings_extension_20071369 + offset) = value;
}

uint32_t audio_conversate_ui_route_5b5b96(uint32_t state, uint32_t value) {
    (void)state;
    (void)value;
    const uint8_t *const replies = audio_conversate_reply_list_get_5b43e8();
    const uint32_t index = word(0x83u);
    if (index == UINT32_MAX || replies == 0 ||
        *(const uint16_t *)(const void *)replies == 0u)
        return 0u;
    const uint32_t next = index == 0u
        ? word(0x7bu)
        : audio_lv_child_44dce2(word(0x63u), index - 1u);
    (void)audio_terminal_session_animate_5896fc(word(0x7fu), next, 200u);
    set_word(0x7fu, next);
    set_word(0x83u, index - 1u);
    return 0u;
}
