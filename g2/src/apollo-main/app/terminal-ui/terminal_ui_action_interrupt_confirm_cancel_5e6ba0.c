/* Stock Terminal interrupt-confirm-cancel FSM action at 0x5e6ba0. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern void audio_terminal_request_display(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_action_interrupt_confirm_cancel";
static const char cancel_message[] =
    "interrupt confirm cancel: deferred=%d refresh=%lu";
static const char cancel_short[] =
    "[terminal.ui]interrupt confirm cancel: deferred=%d refresh=%lu";
static const char replay_message[] =
    "interrupt confirm cancel -> replay deferred query, refresh=%lu";
static const char replay_short[] =
    "[terminal.ui]interrupt confirm cancel -> replay deferred query, refresh=%lu";
static const char cancelled_message[] =
    "interrupt confirm cancelled, back to processing";
static const char cancelled_short[] =
    "[terminal.ui]interrupt confirm cancelled, back to processing";

int32_t audio_terminal_ui_action_5e6ba0(void) {
    uint8_t deferred = audio_terminal_ui_state_base[0x280u];
    uint32_t refresh = *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + 0x284u);
    audio_terminal_ui_stop_service_d_5ec770();
    audio_terminal_ui_state_base[0x280u] = 0u;
    *(uint32_t *)(void *)(audio_terminal_ui_state_base + 0x284u) = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x693u,
                           cancel_message, deferred, refresh);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, cancel_short,
                                    cancel_short, deferred, refresh);
    if (deferred != 0u) {
        audio_terminal_request_display(0x15u, refresh);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x696u,
                               replay_message, refresh);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c400000u, replay_short,
                                        replay_short, refresh);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x698u,
                               cancelled_message);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c000000u, cancelled_short,
                                        cancelled_short);
    }
    return 0;
}
