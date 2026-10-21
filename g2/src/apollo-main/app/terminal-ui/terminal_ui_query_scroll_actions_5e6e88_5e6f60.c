/* Stock Terminal query-scroll up/down FSM actions at 0x5e6e88/0x5e6f60. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_query_layout_5ebb96(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char up_function[] = "terminal_ui_action_query_scroll_up";
static const char down_function[] = "terminal_ui_action_query_scroll_down";
static const char up_message[] =
    "query scroll up apply: browsing=%d idx=%u target_y=%d apply=%d";
static const char down_message[] =
    "query scroll down apply: browsing=%d idx=%u target_y=%d apply=%d";
static const char up_short[] =
    "[terminal.ui]query scroll up apply: browsing=%d idx=%u target_y=%d apply=%d";
static const char down_short[] =
    "[terminal.ui]query scroll down apply: browsing=%d idx=%u target_y=%d apply=%d";

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

static int32_t scroll_action(uint32_t payload, const char *function,
                             const char *message, const char *short_message,
                             uint32_t line) {
    uint32_t target_y = payload & 0xffffu;
    uint32_t object = word(0x214u);
    if (object == 0u)
        return 0;
    uint32_t apply = (payload >> 31) & 1u;
    uint32_t browsing = (payload >> 30) & 1u;
    uint32_t index = (payload >> 16) & 0xffu;
    if (apply != 0u)
        audio_terminal_display_status_44ea04(object, target_y, 1u);
    audio_terminal_ui_state_base[0x27cu] = (uint8_t)browsing;
    audio_terminal_ui_state_base[0x279u] = (uint8_t)index;
    audio_terminal_query_layout_5ebb96();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, line, message,
                           browsing, index, target_y, apply);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0d000000u, short_message,
                                    short_message, browsing, index, target_y,
                                    apply);
    return 0;
}

int32_t audio_terminal_ui_action_5e6e88(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    return scroll_action(event_payload, up_function, up_message, up_short,
                         0x703u);
}

int32_t audio_terminal_ui_action_5e6f60(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    return scroll_action(event_payload, down_function, down_message,
                         down_short, 0x71eu);
}
