/* Apollo Main 0x5b22fa..0x5b23ad: display elapsed time in 12/24-hour mode. */
#include <stdint.h>

extern void audio_time_epoch_to_calendar_44a100(uint32_t, void *);
extern uint32_t audio_time_format_mode_46650c(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern int32_t audio_ble_format_to_buffer(char *, const char *, ...);
extern void audio_uart_page_49942e(uint32_t, const char *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

__attribute__((used, section(".bss.g2_conversate_clock_label_20073cac")))
char audio_conversate_clock_label_buffer_20073cac[20];

static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c";
static const char function[] = "conversate_ui_update_real_time_label";
static const char message[] = "update real time label: %s";
static const char short_message[] =
    "[conversate.ui]update real time label: %s";

void audio_conversate_route_scroll_5b22fa(uint32_t label, uint32_t seconds)
{
    uint32_t record[10];
    audio_time_epoch_to_calendar_44a100(seconds, record);
    char *const buffer = audio_conversate_clock_label_buffer_20073cac;
    audio_uart_buffer_zero(buffer, 20u, 0u);
    uint32_t hour = record[6];
    const uint32_t minute = record[7];
    if (audio_time_format_mode_46650c() == 1u) {
        const char *const meridiem = hour < 12u ? "AM" : "PM";
        hour %= 12u;
        if (hour == 0u) hour = 12u;
        (void)audio_ble_format_to_buffer(buffer, "%02d:%02d %s", hour,
                                         minute, meridiem);
    } else {
        (void)audio_ble_format_to_buffer(buffer, "%02d:%02d", hour, minute);
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, source, function, 0x2cu, message, buffer);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c400000u, short_message,
                                    short_message, buffer);
    audio_uart_page_49942e(label, buffer);
}
