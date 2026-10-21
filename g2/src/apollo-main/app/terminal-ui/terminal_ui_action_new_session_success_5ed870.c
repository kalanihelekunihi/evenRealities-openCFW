/* Stock Terminal new-session-result success FSM action at 0x5ed870. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_ui_event_5e5484(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_reset_mode_5eae2c(uint32_t);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern int32_t audio_terminal_ui_action_5e57c6(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_session_list_ui.c";
static const char function[] = "terminal_ui_action_new_session_result_success";
static const char message[] = "new session allowed, waiting first prompt";
static const char short_message[] =
    "[terminal.ui]new session allowed, waiting first prompt";

int32_t audio_terminal_ui_action_5ed870(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_ui_event_5e5484(3u, 0u, 0u);
    audio_terminal_reset_mode_5eae2c(4u);
    audio_terminal_ui_state_base[0x27eu] = 0u;
    audio_terminal_ui_stop_service_a_5eceb2();
    (void)audio_terminal_ui_action_5e57c6((uint8_t)old_state, 0u);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x262u, message);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c000000u, short_message,
                                    short_message);
    return 0;
}
