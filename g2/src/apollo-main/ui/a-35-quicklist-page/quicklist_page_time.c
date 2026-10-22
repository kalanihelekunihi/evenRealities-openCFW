/* QuickList page helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c.
 * Native 0x4f5068..0x4f50d5 and 0x4f517c..0x4f5595; literal pool words at
 * 0x4f5c3c..0x4f5c48, 0x4f5e14, 0x4f5e7c..0x4f5e80, 0x4f5fb0..0x4f5fcc, and the
 * function-local "AM"/"PM"/"%s" literals at 0x4f5710, 0x4f5714 and 0x4f5834.
 *
 * 0x4f5068 is this TU's out-of-line copy of the LVGL 9.3 lv_obj_style.h inline
 * lv_obj_set_style_pad_all. 0x4f509a clears the UI list copy and the completed
 * UID cache (dashboard data reset). 0x4f517c..0x4f5366 build the row time label:
 * "Today"/"Tomorrow", a short date within a week, otherwise a full date, plus
 * the time of day in the user's 12/24-hour format. */
#include "ui_quicklist_page_private.h"

/* am_hal_rtc_time_t word layout as filled by service_time. */
typedef struct {
    uint32_t read_error; /* +0 */
    uint32_t weekday;    /* +4 */
    uint32_t century;    /* +8 */
    uint32_t year;       /* +12 years since 2000 */
    uint32_t month;      /* +16 1..12 */
    uint32_t day;        /* +20 1..31 */
    uint32_t hour;       /* +24 */
    uint32_t minute;     /* +28 */
    uint32_t second;     /* +32 */
    uint32_t hundredths; /* +36 */
} g2_calendar_t;
_Static_assert(sizeof(g2_calendar_t) == 40u, "am_hal_rtc_time_t");

/* quicklist_date_relation_4f51aa results. */
enum {
    QL_DATE_TODAY = 0u,
    QL_DATE_TOMORROW = 1u,
    QL_DATE_YESTERDAY = 2u,
    QL_DATE_WITHIN_WEEK_AHEAD = 3u,
    QL_DATE_WITHIN_WEEK_BEHIND = 4u,
    QL_DATE_SAME_YEAR = 5u,
    QL_DATE_OTHER_YEAR = 6u,
};

/* quicklist_format_timestamp_4f5366 modes. */
enum {
    QL_FORMAT_DATE_TIME = 0u,
    QL_FORMAT_DATE = 1u,
    QL_FORMAT_TIME = 2u,
};

extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* style pad_right */
extern uint32_t audio_quicklist_refresh_lock_4ffac8(void);   /* quicklist_lock_storage */
extern void audio_quicklist_refresh_unlock_4ffb26(void);     /* quicklist_unlock_storage */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern void service_time_epoch_to_calendar(uint32_t epoch, g2_calendar_t *out); /* 0x44a100 */
extern void service_time_current_calendar_get(g2_calendar_t *out);              /* 0x44a19a */
extern uint8_t svc_universal_setting_get_date_format_466500(void); /* 0 Y/M/D, 1 M/D/Y, else D/M/Y */
extern uint32_t audio_time_format_mode_46650c(void);               /* 1 = 12-hour clock */
extern uint32_t audio_uart_page_460084(const char *key);           /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern const uint8_t *g2_audio_log_timezone; /* pointer cell RAM 0x200036fc; +8 s8 UTC offset in 15 min */

/* Days per month, one ROM initializer per local array (0x30 bytes each). */
static const int32_t month_days_next[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}; /* ROM 0x73ab74 */
static const int32_t month_days_prev[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}; /* ROM 0x73aba4 */
static const int32_t month_days_span[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}; /* ROM 0x73abd4 */

static const char id_today[] = "ID_GENERAL_TODAY";       /* ROM 0x7849dc */
static const char id_tomorrow[] = "ID_GENERAL_TOMORROW"; /* ROM 0x7849f0 */
static const char fmt_short_date[] = "%02d/%02d";        /* ROM 0x78c8a8 */
static const char fmt_ymd[] = "%04d/%02d/%02d";          /* ROM 0x789e10 */
static const char fmt_mdy_dmy[] = "%02d/%02d/%04d";      /* ROM 0x789e20 */
static const char fmt_time_12h[] = "%02d:%02d %s";       /* ROM 0x789e30 */
static const char fmt_time_24h[] = "%02d:%02d";          /* ROM 0x78c8b4 */
static const char fmt_date_time[] = "%s, %s";            /* ROM 0x78ed94 */
static const char str_am[] = "AM";                       /* ROM 0x4f5710 */
static const char str_pm[] = "PM";                       /* ROM 0x4f5714 */
static const char fmt_one[] = "%s";                      /* ROM 0x4f5834 */

void lv_obj_set_style_pad_all_4f5068(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

void quicklist_page_reset_4f509a(uint8_t full)
{
    (void)audio_quicklist_refresh_lock_4ffac8();
    audio_uart_buffer_zero(&g2_quicklist_ui_data_2012a72c, sizeof g2_quicklist_ui_data_2012a72c, 0u);
    audio_uart_buffer_zero(&g2_quicklist_completed_201303cc, sizeof g2_quicklist_completed_201303cc, 0u);
    if (full != 0u)
        g2_quicklist_page_active_20074e1c = 0;
    audio_quicklist_refresh_unlock_4ffb26();
}

uint8_t quicklist_is_leap_year_4f517c(uint32_t year)
{
    return (uint8_t)((((year & 3u) == 0u) && (year % 100u != 0u)) || (year % 400u == 0u));
}

/* Classifies `when` relative to `now` (both calendar records). */
uint8_t quicklist_date_relation_4f51aa(const void *now_p, const void *when_p)
{
    const g2_calendar_t *now = (const g2_calendar_t *)now_p;
    const g2_calendar_t *when = (const g2_calendar_t *)when_p;
    int32_t days_prev[12];
    int32_t days_next[12];
    int32_t days_span[12];
    uint32_t year = now->year + 2000u;
    int32_t limit;
    int32_t diff;
    uint32_t month;

    if (year != when->year + 2000u) {
        if (when->year + 2000u == year + 1u && now->month == 12u && now->day == 31u &&
            when->month == 1u && when->day == 1u)
            return QL_DATE_TOMORROW;
        return QL_DATE_OTHER_YEAR;
    }
    if (now->month == when->month && now->day == when->day)
        return QL_DATE_TODAY;
    if (now->month == when->month && when->day == now->day + 1u)
        return QL_DATE_TOMORROW;
    if (when->month == now->month + 1u && when->day == 1u) {
        audio_uart_display_area_copy_439c04(days_next, month_days_next, sizeof days_next);
        limit = days_next[now->month - 1u];
        if (now->month == 2u && quicklist_is_leap_year_4f517c(year) != 0u)
            limit = 29;
        if ((int32_t)now->day == limit)
            return QL_DATE_TOMORROW;
    }
    if (now->month == when->month && when->day == now->day - 1u)
        return QL_DATE_YESTERDAY;
    if (when->month == now->month - 1u && now->day == 1u) {
        audio_uart_display_area_copy_439c04(days_prev, month_days_prev, sizeof days_prev);
        limit = days_prev[when->month - 1u];
        if (when->month == 2u && quicklist_is_leap_year_4f517c(year) != 0u)
            limit = 29;
        if ((int32_t)when->day == limit)
            return QL_DATE_YESTERDAY;
    }

    diff = 0;
    if (now->month == when->month) {
        diff = (int32_t)(when->day - now->day);
    } else {
        audio_uart_display_area_copy_439c04(days_span, month_days_span, sizeof days_span);
        if (now->month < when->month) {
            for (month = now->month; month < when->month; ++month) {
                diff += days_span[month - 1u];
                if (month == 2u && quicklist_is_leap_year_4f517c(year) != 0u)
                    ++diff;
            }
            diff = (int32_t)when->day + diff - (int32_t)now->day;
        } else {
            for (month = when->month; month < now->month; ++month) {
                diff += days_span[month - 1u];
                if (month == 2u && quicklist_is_leap_year_4f517c(year) != 0u)
                    ++diff;
            }
            diff = -((int32_t)now->day + diff - (int32_t)when->day);
        }
    }
    if ((uint32_t)(diff - 2) < 6u)
        return QL_DATE_WITHIN_WEEK_AHEAD;
    if ((uint32_t)(diff + 7) < 6u)
        return QL_DATE_WITHIN_WEEK_BEHIND;
    return QL_DATE_SAME_YEAR;
}

/* Formats `seconds` (UTC epoch) as "<date>, <time>", "<date>" or "<time>"
 * into out[out_len]. Returns 1 when written, 0 for bad arguments. */
uint8_t quicklist_format_timestamp_4f5366(int64_t seconds, uint8_t mode, char *out, int32_t out_len)
{
    g2_calendar_t when;
    g2_calendar_t now;
    char date[32];
    char time[32];
    int32_t offset;

    if (seconds < 1 || out == NULL || out_len < 1)
        return 0u;

    offset = (int32_t)(int8_t)g2_audio_log_timezone[8] * 900;
    service_time_current_calendar_get(&now);
    service_time_epoch_to_calendar((uint32_t)(seconds + offset), &when);
    audio_uart_buffer_zero(date, sizeof date, 0u);
    audio_uart_buffer_zero(time, sizeof time, 0u);

    if (mode == QL_FORMAT_DATE_TIME || mode == QL_FORMAT_DATE) {
        switch (quicklist_date_relation_4f51aa(&now, &when)) {
        case QL_DATE_TODAY:
            (void)g2_audio_dump_snprintf(date, sizeof date,
                                         audio_uart_page_45fffe(id_today, audio_uart_page_460084(id_today)));
            break;
        case QL_DATE_TOMORROW:
            (void)g2_audio_dump_snprintf(date, sizeof date,
                                         audio_uart_page_45fffe(id_tomorrow,
                                                                audio_uart_page_460084(id_tomorrow)));
            break;
        case QL_DATE_YESTERDAY:
        case QL_DATE_WITHIN_WEEK_AHEAD:
        case QL_DATE_WITHIN_WEEK_BEHIND:
        case QL_DATE_SAME_YEAR:
            if (svc_universal_setting_get_date_format_466500() == 0u ||
                svc_universal_setting_get_date_format_466500() == 1u)
                (void)g2_audio_dump_snprintf(date, sizeof date, fmt_short_date, when.month, when.day);
            else
                (void)g2_audio_dump_snprintf(date, sizeof date, fmt_short_date, when.day, when.month);
            break;
        default:
            if (svc_universal_setting_get_date_format_466500() == 0u)
                (void)g2_audio_dump_snprintf(date, sizeof date, fmt_ymd, when.year + 2000u, when.month,
                                             when.day);
            else if (svc_universal_setting_get_date_format_466500() == 1u)
                (void)g2_audio_dump_snprintf(date, sizeof date, fmt_mdy_dmy, when.month, when.day,
                                             when.year + 2000u);
            else
                (void)g2_audio_dump_snprintf(date, sizeof date, fmt_mdy_dmy, when.day, when.month,
                                             when.year + 2000u);
            break;
        }
    } else {
        date[0] = '\0';
    }

    if (mode == QL_FORMAT_DATE_TIME || mode == QL_FORMAT_TIME) {
        if (audio_time_format_mode_46650c() == 1u) {
            uint32_t hour12 = when.hour % 12u;
            if (hour12 == 0u)
                hour12 = 12u;
            (void)g2_audio_dump_snprintf(time, sizeof time, fmt_time_12h, hour12, when.minute,
                                         when.hour < 12u ? str_am : str_pm);
        } else {
            (void)g2_audio_dump_snprintf(time, sizeof time, fmt_time_24h, when.hour, when.minute);
        }
    } else {
        time[0] = '\0';
    }

    if (date[0] != '\0' && time[0] != '\0')
        (void)g2_audio_dump_snprintf(out, (uint32_t)out_len, fmt_date_time, date, time);
    else if (date[0] != '\0')
        (void)g2_audio_dump_snprintf(out, (uint32_t)out_len, fmt_one, date);
    else if (time[0] != '\0')
        (void)g2_audio_dump_snprintf(out, (uint32_t)out_len, fmt_one, time);
    else
        out[0] = '\0';
    return 1u;
}
