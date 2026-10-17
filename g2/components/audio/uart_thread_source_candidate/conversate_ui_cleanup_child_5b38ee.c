/* Native Conversate loading-timeout callback 0x5b38ee..0x5b39b3. */
#include <stdint.h>

extern uint8_t audio_conversate_timer_mgr_ram_20073a3c[];
extern uint8_t audio_conversate_ui_state_20071368;
extern uint8_t audio_conversate_machine_context_200e3aec[];
extern uint32_t audio_conversate_timer_expired_5b3628(const uint8_t *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern uint32_t audio_quicklist_tick_now(void);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern void audio_conversate_enter_loading_5b57ac(void);
extern void audio_conversate_timer_1_start_5b3766(void);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_timer_process_loading_timeout";
static const char entered[] = "Loading timeout, enter main";
static const char entered_short[] = "[conversate.timer]Loading timeout, enter main";
static const char retry[] =
    "loading timeout, app not started yet, resend start request and retry";
static const char retry_short[] =
    "[conversate.timer]loading timeout, app not started yet, resend start request and retry";

static void log_message(uint32_t level, uint32_t line, const char *message,
                        uint32_t simple_level, const char *short_message) {
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, path, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(simple_level, short_message, short_message);
}

void audio_conversate_ui_cleanup_child_5b38ee(uint32_t tick) {
    uint8_t *const timer = audio_conversate_timer_mgr_ram_20073a3c;
    if (!audio_conversate_timer_expired_5b3628(timer, tick))
        return;
    timer[0] = 0u;
    if (audio_conversate_ui_state_20071368 != 1u)
        return;
    if (audio_conversate_machine_context_200e3aec[0] == 1u) {
        log_message(3u, 249u, entered, 0x0c000000u, entered_short);
        (void)audio_conversate_report_5b02e4(4u, audio_quicklist_tick_now());
    } else {
        log_message(2u, 254u, retry, 0x08000000u, retry_short);
        audio_conversate_enter_loading_5b57ac();
        audio_conversate_timer_1_start_5b3766();
    }
}
