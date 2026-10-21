/* Native Conversate selection-timeout callback 0x5b39b4..0x5b3a59. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_state_20071368;
extern uint8_t audio_conversate_ui_deinit_tail_200713fd[];
extern uint8_t audio_conversate_timer_mgr_ram_20073a3c[];
extern uint32_t audio_conversate_timer_expired_5b3628(const uint8_t *, uint32_t);
extern void audio_conversate_timer_2_stop_5b383c(void);
extern void audio_conversate_timer_2_start_5b37d8(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_timer_process_select_timeout";
static const char message[] = "Select timeout, switch to unselect";
static const char short_message[] =
    "[conversate.timer]Select timeout, switch to unselect";

void audio_conversate_ui_cleanup_flush_5b39b4(uint32_t tick) {
    uint8_t *const timer = audio_conversate_timer_mgr_ram_20073a3c + 8u;
    if (audio_conversate_ui_state_20071368 != 2u ||
        audio_conversate_ui_deinit_tail_200713fd[1] != 1u) {
        if (timer[0] != 0u)
            audio_conversate_timer_2_stop_5b383c();
        return;
    }
    if (timer[0] == 0u) {
        audio_conversate_timer_2_start_5b37d8();
        return;
    }
    if (!audio_conversate_timer_expired_5b3628(timer, tick))
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 283u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c000000u, short_message, short_message);
    audio_conversate_timer_2_stop_5b383c();
    (void)audio_conversate_report_5b02e4(13u, 0u);
}
