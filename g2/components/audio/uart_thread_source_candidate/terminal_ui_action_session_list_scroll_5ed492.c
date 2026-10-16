/* Stock Terminal session-list scroll FSM action at 0x5ed492. */
#include <stdint.h>

extern void audio_terminal_session_select_5ecc1a(int32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_session_list_ui.c";
static const char function[] = "terminal_ui_action_session_list_scroll";
static const char message[] = "session list scroll apply: selected=%d";
static const char short_message[] =
    "[terminal.ui]session list scroll apply: selected=%d";

int32_t audio_terminal_ui_action_5ed492(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    const int32_t selected = (int16_t)(uint16_t)event_payload;
    audio_terminal_session_select_5ecc1a(selected);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x1fdu,
                           message, selected);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c400000u, short_message,
                                    short_message, selected);
    return 0;
}
