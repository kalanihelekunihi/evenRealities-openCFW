/* Stock Terminal query-notification return at 0x5e6620. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_terminal_reset_ancillary_5e65f8(void);
extern int32_t audio_terminal_ui_action_5e5442(uint32_t old_state, uint32_t payload);
extern int32_t audio_terminal_ui_action_5e57c6(uint32_t old_state, uint32_t payload);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_restore_notification_return_state";
static const char message[] = "query notification dismissed: restore_state=%d";
static const char compact[] = "[terminal.ui]query notification dismissed: restore_state=%d";

int32_t audio_terminal_ui_restore_query_5e6620(uint32_t old_state) {
    uint8_t saved = audio_terminal_ui_state_base[0x277u];
    audio_terminal_ui_stop_service_e_5ec9c0();
    audio_terminal_reset_ancillary_5e65f8();
    if (saved == 0u) {
        (void)audio_terminal_ui_action_5e5442((uint8_t)old_state, 0u);
    } else if (saved != 2u && saved != 7u && saved != 11u && saved != 12u) {
        (void)audio_terminal_ui_action_5e57c6((uint8_t)old_state, 0u);
        saved = 2u;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x5ffu, message, saved);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c400000u, compact, compact, saved);
    return (int32_t)((uint32_t)saved + 1u);
}
