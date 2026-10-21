/* Stock Terminal interrupt-confirm-show FSM action at 0x5e6b18. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_interrupt_confirm_prepare_5ec446(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_action_interrupt_confirm_show";
static const char message[] = "interrupt confirm shown: from_state=%d";
static const char short_message[] =
    "[terminal.ui]interrupt confirm shown: from_state=%d";

int32_t audio_terminal_ui_action_5e6b18(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_ui_state_base[0x278u] = 0u;
    audio_terminal_ui_state_base[0x280u] = 0u;
    *(uint32_t *)(void *)(audio_terminal_ui_state_base + 0x284u) = 0u;
    audio_terminal_interrupt_confirm_prepare_5ec446();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x684u,
                           message, (uint8_t)old_state);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c400000u, short_message,
                                    short_message, (uint8_t)old_state);
    return 0;
}
