/* Native timer starts 0x5b3766, 0x5b37d8, and 0x5b384c. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_state_20071368;
extern uint8_t audio_conversate_ui_deinit_tail_200713fd[];
extern uint8_t audio_conversate_timer_mgr_ram_20073a3c[];
extern void audio_conversate_timer_start_5b3570(void *, uint32_t, const char *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char loading_function[] = "conversate_timer_loading_timeout_start";
static const char select_function[] = "conversate_timer_select_timeout_start";
static const char extend_function[] = "conversate_timer_auto_extend_start";
static const char loading_skip[] = "Loading timeout start skipped: state not loading";
static const char select_skip[] = "Select timeout start skipped: mode unselected";
static const char extend_skip[] = "Auto extend start skipped: condition not met";
static const char loading_short[] =
    "[conversate.timer]Loading timeout start skipped: state not loading";
static const char select_short[] =
    "[conversate.timer]Select timeout start skipped: mode unselected";
static const char extend_short[] =
    "[conversate.timer]Auto extend start skipped: condition not met";
static const char loading_name[] = "Loading timeout";
static const char select_name[] = "Select timeout";
static const char extend_name[] = "Auto extend";

static void log_skip(const char *function, uint32_t line, const char *message,
                     const char *short_message) {
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, short_message, short_message);
}

void audio_conversate_timer_1_start_5b3766(void) {
    if (audio_conversate_ui_state_20071368 == 1u)
        audio_conversate_timer_start_5b3570(
            audio_conversate_timer_mgr_ram_20073a3c, 2000u, loading_name);
    else
        log_skip(loading_function, 183u, loading_skip, loading_short);
}

void audio_conversate_timer_2_start_5b37d8(void) {
    if (audio_conversate_ui_deinit_tail_200713fd[1] == 1u)
        audio_conversate_timer_start_5b3570(
            audio_conversate_timer_mgr_ram_20073a3c + 8u, 5000u, select_name);
    else
        log_skip(select_function, 201u, select_skip, select_short);
}

void audio_conversate_timer_3_start_5b384c(void) {
    if (audio_conversate_ui_state_20071368 == 4u &&
        audio_conversate_ui_deinit_tail_200713fd[1] == 0u)
        audio_conversate_timer_start_5b3570(
            audio_conversate_timer_mgr_ram_20073a3c + 0x10u, 1000u, extend_name);
    else
        log_skip(extend_function, 213u, extend_skip, extend_short);
}
