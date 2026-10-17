/* Native Conversate auto-extend tick 0x5b3a88..0x5b3c29. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_state_20071368;
extern uint8_t audio_conversate_ui_deinit_tail_200713fd[];
extern uint8_t audio_conversate_timer_mgr_ram_20073a3c[];
extern uint32_t audio_conversate_timer_expired_5b3628(const uint8_t *, uint32_t);
extern void audio_conversate_timer_3_start_5b384c(void);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_timer_process_auto_extend_tick";
static const char rearm[] = "Auto extend timer not running in tag extend, re-arm";
static const char rearm_short[] =
    "[conversate.timer]Auto extend timer not running in tag extend, re-arm";
static const char reset[] = "Auto extend countdown reset";
static const char reset_short[] = "[conversate.timer]Auto extend countdown reset";
static const char countdown[] = "Auto extend countdown: %d/%d";
static const char countdown_short[] = "[conversate.timer]Auto extend countdown: %d/%d";
static const char finished[] = "Auto extend countdown finished, close extend page";
static const char finished_short[] =
    "[conversate.timer]Auto extend countdown finished, close extend page";

static void log_plain(uint32_t level, uint32_t line, const char *message,
                      uint32_t simple_level, const char *short_message) {
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, path, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(simple_level, short_message, short_message);
}

static uint32_t read_word(const uint8_t *p) {
    return *(const uint32_t *)(const void *)p;
}

static void write_word(uint8_t *p, uint32_t value) {
    *(uint32_t *)(void *)p = value;
}

static uint32_t timer_should_tick(const uint8_t *timer) {
    return timer[0] != 0u && audio_conversate_ui_state_20071368 == 4u &&
           audio_conversate_ui_deinit_tail_200713fd[1] == 0u &&
           audio_conversate_ui_deinit_tail_200713fd[15] == 1u;
}

void audio_conversate_ui_cleanup_commit_5b3a88(uint32_t tick) {
    uint8_t *const timer = audio_conversate_timer_mgr_ram_20073a3c + 0x10u;
    if (!timer[0] && audio_conversate_ui_state_20071368 == 4u &&
        audio_conversate_ui_deinit_tail_200713fd[1] == 0u &&
        audio_conversate_ui_deinit_tail_200713fd[15] == 1u) {
        log_plain(3u, 305u, rearm, 0x0c000000u, rearm_short);
        audio_conversate_timer_3_start_5b384c();
    }
    if (!timer_should_tick(timer) ||
        !audio_conversate_timer_expired_5b3628(timer, tick))
        return;
    uint32_t count = read_word(timer + 8u);
    if (count == UINT32_MAX) {
        log_plain(4u, 318u, reset, 0x10000000u, reset_short);
        count = 0u;
    } else {
        count++;
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 323u, countdown,
                               count, audio_conversate_ui_deinit_tail_200713fd[0]);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x10800000u, countdown_short, countdown_short,
                             count, audio_conversate_ui_deinit_tail_200713fd[0]);
    }
    write_word(timer + 8u, count);
    const uint32_t limit = audio_conversate_ui_deinit_tail_200713fd[0];
    if (count >= limit) {
        log_plain(3u, 327u, finished, 0x0c000000u, finished_short);
        write_word(timer + 8u, 0u);
        timer[0] = 0u;
        (void)audio_conversate_report_5b02e4(10u, 2u);
    } else {
        (void)audio_conversate_report_5b02e4(9u, limit - count);
        write_word(timer + 4u, tick + 1000u);
    }
}
