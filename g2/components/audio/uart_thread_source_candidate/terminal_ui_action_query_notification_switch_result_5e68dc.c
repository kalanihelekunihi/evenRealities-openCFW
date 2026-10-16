/* Stock Terminal query-notification switch-result FSM action at 0x5e68dc. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern int32_t audio_terminal_ui_restore_query_5e6620(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] =
    "terminal_ui_action_query_notification_switch_result";
static const char success[] =
    "query notification switch success, waiting session id changed";
static const char success_short[] =
    "[terminal.ui]query notification switch success, waiting session id changed";
static const char failure[] =
    "query notification switch failed, restore previous state";
static const char failure_short[] =
    "[terminal.ui]query notification switch failed, restore previous state";

int32_t audio_terminal_ui_action_5e68dc(uint32_t old_state,
                                         uint32_t event_result) {
    if (audio_terminal_ui_state_base[0x27fu] == 0u)
        return 0;
    if ((uint8_t)event_result == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x644u, success);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c000000u, success_short,
                                        success_short);
        return 0;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, function, 0x648u, failure);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x08000000u, failure_short,
                                    failure_short);
    return audio_terminal_ui_restore_query_5e6620((uint8_t)old_state);
}
