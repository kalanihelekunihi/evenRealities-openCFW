/* Stock Terminal FSM interrupt-confirm defer-query action at 0x5e6d58. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_action_interrupt_confirm_defer_query";
static const char message[] =
    "defer query while interrupt confirm shown: state=%d refresh=%lu";
static const char short_message[] =
    "[terminal.ui]defer query while interrupt confirm shown: state=%d refresh=%lu";

int32_t audio_terminal_ui_action_5e6d58(uint32_t old_state,
                                         uint32_t event_payload) {
    audio_terminal_ui_state_base[0x280u] = 1u;
    *(uint32_t *)(void *)(audio_terminal_ui_state_base + 0x284u) = event_payload;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x6b7u,
                           message, (uint8_t)old_state, event_payload);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, short_message,
                                    short_message, (uint8_t)old_state,
                                    event_payload);
    return 0;
}
