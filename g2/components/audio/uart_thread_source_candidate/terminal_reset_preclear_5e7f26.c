/* Stock Terminal voice-timeout stop at 0x5e7f26. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_timer_state_20073c38[0x18]; /* stock RAM */
extern uint32_t audio_log_flags(void); /* stock 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* stock 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.timer";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_timer.c";
static const char function[] = "terminal_timer_voice_timeout_stop";
static const char message[] = "voice timeout stop";
static const char compact[] = "[terminal.timer]voice timeout stop";

void audio_terminal_reset_preclear_5e7f26(void) {
    uint8_t *timer = audio_terminal_ui_timer_state_20073c38;
    if (timer[0] == 0u)
        return;
    timer[0] = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x39u, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10000000u, compact, compact);
}
