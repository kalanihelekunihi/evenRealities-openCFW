/* dashboard_async_update_data, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard.c.
 * Native 0x49ce14..0x49dd46; literal pools 0x49db48..0x49dc0c, 0x49dd48..0x49ddb4,
 * 0x49e114..0x49e144, 0x49e40c..0x49e448 and 0x49e650..0x49e670.
 *
 * Applies one parsed phone package (RAM 0x20366718, produced by
 * dashboard_parse_data_package 0x4fe318) to the UI-side copies under the
 * dashboard mutex, then posts a refresh to the dashboard UI application.
 * Exactly one section flag is honoured, checked in this order:
 *   +0x14b8 news info request   -> 2 (answered by dashboard_respond_NewsInfo_to_app)
 *   +0x14b9 news protocol v2    -> 0
 *   +0x14b6 display settings    (tile order, widget list, time format)
 *   +0x14b0 weather
 *   +0x14b3 legacy news         -> 2 (dropped)
 *   +0x14b4 stock               (one stock per package, accumulated to stock_total)
 *   +0x14b5 schedule            (one event per package, published at the last one)
 * The stock logs pass floats through varargs, so the unit needs double-precision
 * VFP conversions (profile g2-apollo-main-20). */
#include <stdint.h>
#include <stdbool.h>

#define DASHBOARD_APP 1u
#define DASHBOARD_MSG_SETTINGS 1u
#define DASHBOARD_MSG_CALENDAR 2u
#define DASHBOARD_MSG_STOCK 4u
#define STOCK_NUM_LIMIT 9u
#define SCHEDULE_RECORD_SIZE 0x210u
#define WAIT_FOREVER 0xffffffffu

/* Parsed package offsets (RAM 0x20366718). */
#define P_WEATHER 0x24u           /* +0x24..0x9f, mirrored into the settings block */
#define P_STOCK_CODE 0xe30u       /* char[0x40] */
#define P_STOCK_NAME 0xe70u       /* char[0x40] */
#define P_STOCK_COMPANY 0xeb0u    /* char[0x80] */
#define P_STOCK_VALUES 0xf30u     /* 0x40 bytes of numeric fields */
#define P_STOCK_CHANGE_PCT 0xf38u /* float */
#define P_STOCK_CURRENT 0xf3cu    /* float */
#define P_STOCK_DAY_HIGH 0xf40u   /* float */
#define P_STOCK_DAY_LOW 0xf44u    /* float */
#define P_STOCK_OPEN 0xf48u       /* float */
#define P_STOCK_TREND 0xf64u      /* int */
#define P_STOCK_POINT_TOTAL 0xf68u
#define P_STOCK_DARK_PRICE 0xf6cu /* float */
#define P_STOCK_POINTS 0xf70u     /* 0x2e4 bytes of chart points */
#define P_STOCK_TOTAL 0x1258u
#define P_STOCK_NUM 0x125cu
#define P_SCHED_TITLE 0x1264u     /* 0xb0 bytes */
#define P_SCHED_LOCATION 0x1314u  /* 0x11b bytes */
#define P_SCHED_TIME 0x142fu      /* 0x40 bytes */
#define P_SCHED_STAMP 0x1470u
#define P_SCHED_AUTHORITY 0x1474u
#define P_SCHED_TOTAL 0x1478u
#define P_SCHED_NUM 0x147cu
#define P_TILE_COUNT 0x1484u
#define P_TILES 0x1488u           /* uint8_t[] */
#define P_WIDGET_COUNT 0x1494u
#define P_WIDGETS 0x1498u         /* uint8_t[] */
#define P_TIME_FORMAT 0x14a4u
#define P_HAS_WEATHER 0x14b0u
#define P_HAS_NEWS 0x14b3u
#define P_HAS_STOCK 0x14b4u
#define P_HAS_SCHEDULE 0x14b5u
#define P_HAS_SETTINGS 0x14b6u
#define P_NEWS_INFO 0x14b8u
#define P_NEWS_V2 0x14b9u

/* Schedule record (staging RAM 0x200e67f8 / UI RAM 0x2011df34, after a u16 count). */
#define S_TITLE 0x000u
#define S_LOCATION 0x0b0u
#define S_TIME 0x1cbu
#define S_STAMP 0x20cu
#define SCHEDULE_UI_AUTHORITY 0x1084u

#define U8(p, o) (*(volatile uint8_t *)((p) + (o)))
#define U16(p, o) (*(uint16_t *)(void *)((p) + (o)))
#define U32(p, o) (*(uint32_t *)(void *)((p) + (o)))
#define F32(p, o) (*(const float *)(const void *)((p) + (o)))

extern void *g2_dashboard_mutex_200743a8;                 /* RAM 0x200743a8 osMutexId */
extern volatile uint32_t g2_dashboard_stock_received_200743ac; /* RAM 0x200743ac */
extern volatile uint32_t g2_dashboard_stock_total_200743b0;    /* RAM 0x200743b0 */
extern uint8_t g2_dashboard_state[];                      /* RAM 0x200e3e80 settings/weather block */
extern uint8_t g2_dashboard_event_buffer_200e3f20[0x1000]; /* RAM 0x200e3f20 */
extern uint8_t g2_dashboard_schedule_staging_200e67f8[];  /* RAM 0x200e67f8 */
extern uint8_t g2_dashboard_schedule_ui_2011df34[];       /* RAM 0x2011df34 */
extern volatile uint32_t g2_dashboard_schedule_authority_2011efb8; /* RAM 0x2011efb8 */
extern uint8_t g2_dashboard_stock_ui_20378974[0x424];     /* RAM 0x20378974 */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);
extern int32_t osMutexRelease(void *mutex);
extern void dashboard_clear_stock_ui_data_49c668(void);
extern void dashboard_clear_calendar_ui_data_49c728(void);
extern void stock_page_push_data_4e9e32(uint8_t *stock, uint32_t stock_num, uint32_t stock_total);
extern uint8_t *audio_setting_unit_record_get_466010(void);
extern void audio_uart_ring_unpair_commit_hand_466016(void);
extern uint32_t audio_uart_service_mode(void);            /* 0x45a570 device role byte */
extern uint32_t audio_log_wake_allowed(void);             /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t id);
extern int32_t audio_uart_master_display_refresh(uint32_t id, const void *payload, uint16_t length,
                                                 uint32_t extra); /* 0x464bb2 */
extern int32_t async_request_display_reflash_45aaca(uint32_t application, const void *payload,
                                                    uint32_t length, uint32_t delay);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);      /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len);  /* 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "dashboard"; /* ROM 0x78a6b8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard.c"; /* ROM 0x701624 */
static const char fn[] = "dashboard_async_update_data"; /* ROM 0x76a8f8 */
static const char off_news_v2[] = "\n\ndashboard_update_data_screen_off: news_protocol_v2\n\n"; /* ROM 0x71d420 */
static const char off_news_v2_short[] =
    "[dashboard]\n\ndashboard_update_data_screen_off: news_protocol_v2\n\n"; /* ROM 0x7017bc */
static const char off_settings[] = "\n\ndashboard_update_data_screen_off: display_setting\n\n"; /* ROM 0x71d458 */
static const char off_settings_short[] =
    "[dashboard]\n\ndashboard_update_data_screen_off: display_setting\n\n"; /* ROM 0x701800 */
static const char time_format[] = "receive time_format = %d"; /* ROM 0x76a914 */
static const char time_format_short[] = "[dashboard]receive time_format = %d"; /* ROM 0x7530f0 */
static const char update_ret[] = "dashboard async update_data: ret = %d\n"; /* ROM 0x748bc4 */
static const char update_ret_short[] = "[dashboard]dashboard async update_data: ret = %d\n"; /* ROM 0x7282dc */
static const char off_weather[] = "\n\ndashboard_update_data_screen_off: weather\n\n"; /* ROM 0x7329e4 */
static const char off_weather_short[] = "[dashboard]\n\ndashboard_update_data_screen_off: weather\n\n"; /* ROM 0x7139b4 */
static const char screen_on_ret[] = "dashboard_update_data_screen_on: ret = %d\n"; /* ROM 0x73d454 */
static const char screen_on_ret_short[] = "[dashboard]dashboard_update_data_screen_on: ret = %d\n"; /* ROM 0x71d340 */
static const char off_news[] = "\n\ndashboard_update_data_screen_off: news\n\n"; /* ROM 0x73d530 */
static const char off_news_short[] = "[dashboard]\n\ndashboard_update_data_screen_off: news\n\n"; /* ROM 0x71d490 */
static const char news_drop[] = "news protol has changed.drop it!"; /* ROM 0x753114 */
static const char news_drop_short[] = "[dashboard]news protol has changed.drop it!"; /* ROM 0x73d55c */
static const char off_stock[] = "\n\ndashboard update data screen off: stock\n\n"; /* ROM 0x73d588 */
static const char off_stock_short[] = "[dashboard]\n\ndashboard update data screen off: stock\n\n"; /* ROM 0x71d4c8 */
static const char stock_counts[] = "parsed_data->stock_total = %d, parsed_data->stock_num = %d\n"; /* ROM 0x7139f0 */
static const char stock_counts_short[] =
    "[dashboard]parsed_data->stock_total = %d, parsed_data->stock_num = %d\n"; /* ROM 0x6f97ac */
static const char stock_zero[] = "dashboard async update data: stock_total is 0, clearing stock UI data"; /* ROM 0x6f97f4 */
static const char stock_zero_short[] =
    "[dashboard]dashboard async update data: stock_total is 0, clearing stock UI data"; /* ROM 0x6e6ff4 */
static const char stock_clear_sent[] = "dashboard async update data: stock clear event sent, ret = %d\n"; /* ROM 0x70a664 */
static const char stock_clear_sent_short[] =
    "[dashboard]dashboard async update data: stock clear event sent, ret = %d\n"; /* ROM 0x6f28ec */
static const char stock_invalid[] = "Invalid stock_num: %d, ignore"; /* ROM 0x75ef10 */
static const char stock_invalid_short[] = "[dashboard]Invalid stock_num: %d, ignore"; /* ROM 0x73d5b4 */
static const char stock_code[] = "parsed_data->stock_code:%s, company_name:%s, point_total:%d"; /* ROM 0x713a2c */
static const char stock_code_short[] =
    "[dashboard]parsed_data->stock_code:%s, company_name:%s, point_total:%d"; /* ROM 0x6f983c */
static const char stock_range[] = "day_high:%f, day_low:%f, dark_price:%f"; /* ROM 0x748bec */
static const char stock_range_short[] = "[dashboard]day_high:%f, day_low:%f, dark_price:%f"; /* ROM 0x728310 */
static const char stock_price[] = "price_change_percent:%f, current_price:%f"; /* ROM 0x73d5e0 */
static const char stock_price_short[] = "[dashboard]price_change_percent:%f, current_price:%f"; /* ROM 0x71d500 */
static const char stock_trend[] = "changing_trend:%d, open_price:%f"; /* ROM 0x753138 */
static const char stock_trend_short[] = "[dashboard]changing_trend:%d, open_price:%f"; /* ROM 0x73d60c */
static const char stock_total_changed[] = "Stock total changed %d->%d, reset counter"; /* ROM 0x73d638 */
static const char stock_total_changed_short[] = "[dashboard]Stock total changed %d->%d, reset counter"; /* ROM 0x71d538 */
static const char counter_overflow[] = "Counter overflow %d/%d, force reset"; /* ROM 0x75315c */
static const char counter_overflow_short[] = "[dashboard]Counter overflow %d/%d, force reset"; /* ROM 0x732a14 */
static const char stock_received[] = "dashboard async received stock %d/%d"; /* ROM 0x748c14 */
static const char stock_received_short[] = "[dashboard]dashboard async received stock %d/%d"; /* ROM 0x732a44 */
static const char stock_refresh[] = "Stock UI refresh triggered, ret = %d"; /* ROM 0x748c3c */
static const char stock_refresh_short[] = "[dashboard]Stock UI refresh triggered, ret = %d"; /* ROM 0x732a74 */
static const char stock_waiting[] = "Stock data accumulated, waiting for more (%d/%d)"; /* ROM 0x728344 */
static const char stock_waiting_short[] = "[dashboard]Stock data accumulated, waiting for more (%d/%d)"; /* ROM 0x713a68 */
static const char stock_all[] = "All stocks received, reset counter"; /* ROM 0x753180 */
static const char stock_all_short[] = "[dashboard]All stocks received, reset counter"; /* ROM 0x732aa4 */
static const char off_schedule[] = "\n\ndashboard_update_data_screen_off: schedule\n\n"; /* ROM 0x732ad4 */
static const char off_schedule_short[] = "[dashboard]\n\ndashboard_update_data_screen_off: schedule\n\n"; /* ROM 0x713aa4 */
static const char sched_authority[] = "parsed_data->schedule_authority = %d\n"; /* ROM 0x748c64 */
static const char sched_authority_short[] = "[dashboard]parsed_data->schedule_authority = %d\n"; /* ROM 0x728378 */
static const char sched_counts[] = "parsed_data->schedule_num = %d, parsed_data->schedule_total = %d\n"; /* ROM 0x701844 */
static const char sched_counts_short[] =
    "[dashboard]parsed_data->schedule_num = %d, parsed_data->schedule_total = %d\n"; /* ROM 0x6ec7f8 */
static const char sched_zero[] =
    "dashboard async update data: schedule_total is 0, clearing calendar UI data"; /* ROM 0x6f2938 */
static const char sched_zero_short[] =
    "[dashboard]dashboard async update data: schedule_total is 0, clearing calendar UI data"; /* ROM 0x6e2cd0 */
static const char sched_clear_sent[] = "dashboard async update data: calendar clear event sent, ret = %d\n"; /* ROM 0x701888 */
static const char sched_clear_sent_short[] =
    "[dashboard]dashboard async update data: calendar clear event sent, ret = %d\n"; /* ROM 0x6ec848 */
static const char sched_update_sent[] = "dashboard async update data: calendar update event sent, ret = %d\n"; /* ROM 0x7018cc */
static const char sched_update_sent_short[] =
    "[dashboard]dashboard async update data: calendar update event sent, ret = %d\n"; /* ROM 0x6ec898 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

static void log_plain(uint8_t level, uint32_t line, uint32_t flags, const char *message, const char *compact)
{
    if (LOG_EXT_ON())
        audio_log_extended(level, module_tag, source_file, fn, line, message);
    if (LOG_CMP_ON())
        (void)compress_log_output(flags, compact, compact);
}

static void log_value(uint8_t level, uint32_t line, uint32_t flags, const char *message, const char *compact,
                      uint32_t value)
{
    if (LOG_EXT_ON())
        audio_log_extended(level, module_tag, source_file, fn, line, message, value);
    if (LOG_CMP_ON())
        (void)compress_log_output(flags, compact, compact, value);
}

static void log_pair(uint8_t level, uint32_t line, uint32_t flags, const char *message, const char *compact,
                     uint32_t first, uint32_t second)
{
    if (LOG_EXT_ON())
        audio_log_extended(level, module_tag, source_file, fn, line, message, first, second);
    if (LOG_CMP_ON())
        (void)compress_log_output(flags, compact, compact, first, second);
}

static bool dashboard_ui_ready(void)
{
    return (uint8_t)audio_uart_service_mode() == 1u && audio_log_wake_allowed() == 1u &&
           audio_quicklist_refresh_enabled_4434d0(DASHBOARD_APP) == 1u;
}

/* One-byte event in the shared 4 KiB event buffer. */
static int32_t post_event(uint8_t type)
{
    audio_uart_buffer_zero(g2_dashboard_event_buffer_200e3f20, sizeof g2_dashboard_event_buffer_200e3f20, 0u);
    g2_dashboard_event_buffer_200e3f20[0] = type;
    return audio_uart_master_display_refresh(DASHBOARD_APP, g2_dashboard_event_buffer_200e3f20, 1u, 0u);
}

static void update_settings(const uint8_t *p)
{
    uint8_t *const st = g2_dashboard_state;
    log_plain(4u, 0x1edu, 0x10000000u, off_settings, off_settings_short);
    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    U16(st, 0x0a) = (uint16_t)U32(p, P_TILE_COUNT);
    for (uint32_t i = 0u; i < U32(p, P_TILE_COUNT); i++)
        U16(st, 0x0c + 2u * i) = p[P_TILES + i];
    U16(st, 0x18) = (uint16_t)U32(p, P_WIDGET_COUNT);
    for (uint32_t i = 0u; i < U32(p, P_WIDGET_COUNT); i++)
        st[0x1a + i] = p[P_WIDGETS + i];
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);
    U32(audio_setting_unit_record_get_466010(), 0x18) = U32(p, P_TIME_FORMAT);
    log_value(3u, 0x1feu, 0x0c400000u, time_format, time_format_short, U32(p, P_TIME_FORMAT));
    audio_uart_ring_unpair_commit_hand_466016();
    if (dashboard_ui_ready()) {
        int32_t ret = post_event(DASHBOARD_MSG_SETTINGS);
        log_value(4u, 0x206u, 0x10400000u, update_ret, update_ret_short, (uint32_t)ret);
    }
}

static void update_weather(const uint8_t *p)
{
    uint8_t *const st = g2_dashboard_state;
    log_plain(4u, 0x20bu, 0x10000000u, off_weather, off_weather_short);
    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    st[0x20] = 1u;
    U32(st, 0x24) = U32(p, 0x24);
    U16(st, 0x28) = U16(p, 0x28);
    U16(st, 0x2a) = U16(p, 0x2a);
    U32(st, 0x30) = U32(p, 0x30);
    U32(st, 0x34) = U32(p, 0x34);
    (void)audio_settings_copy_text(st + 0x38, p + 0x38, 0x1fu);
    st[0x57] = 0u;
    U32(st, 0x58) = U32(p, 0x58);
    (void)audio_settings_copy_text(st + 0x5c, p + 0x5c, 0x1fu);
    st[0x7b] = 0u;
    U32(st, 0x7c) = U32(p, 0x7c);
    (void)audio_settings_copy_text(st + 0x80, p + 0x80, 0x1fu);
    st[0x9f] = 0u;
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);
    if (dashboard_ui_ready()) {
        int32_t ret = post_event(DASHBOARD_MSG_SETTINGS);
        log_value(4u, 0x222u, 0x10400000u, screen_on_ret, screen_on_ret_short, (uint32_t)ret);
    }
}

static uint32_t update_stock(const uint8_t *p)
{
    uint8_t *const ui = g2_dashboard_stock_ui_20378974;
    bool all_received;

    log_plain(4u, 0x27au, 0x10000000u, off_stock, off_stock_short);
    log_pair(4u, 0x27bu, 0x10800000u, stock_counts, stock_counts_short, U32(p, P_STOCK_TOTAL),
             U32(p, P_STOCK_NUM));
    if (U32(p, P_STOCK_TOTAL) == 0u) {
        log_plain(4u, 0x27fu, 0x10000000u, stock_zero, stock_zero_short);
        dashboard_clear_stock_ui_data_49c668();
        g2_dashboard_stock_received_200743ac = 0u;
        g2_dashboard_stock_total_200743b0 = 0u;
        if (dashboard_ui_ready()) {
            int32_t ret = post_event(DASHBOARD_MSG_STOCK);
            log_value(4u, 0x28cu, 0x10400000u, stock_clear_sent, stock_clear_sent_short, (uint32_t)ret);
        }
        return 0u;
    }
    if (U32(p, P_STOCK_NUM) >= STOCK_NUM_LIMIT) {
        log_value(1u, 0x293u, 0x04400000u, stock_invalid, stock_invalid_short, U32(p, P_STOCK_NUM));
        return 0u;
    }

    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    audio_uart_checksum_copy(ui, p + P_STOCK_CODE, 0x40u);
    audio_uart_checksum_copy(ui + 0x40, p + P_STOCK_NAME, 0x40u);
    audio_uart_checksum_copy(ui + 0x80, p + P_STOCK_COMPANY, 0x80u);
    /* Numeric block +0x100..+0x13f; the word at +0x11c is padding and is not copied. */
    U32(ui, 0x100) = U32(p, 0xf30);
    U32(ui, 0x104) = U32(p, 0xf34);
    for (uint32_t o = 0x08u; o <= 0x18u; o += 4u)
        U32(ui, 0x100 + o) = U32(p, P_STOCK_VALUES + o);
    for (uint32_t o = 0x20u; o <= 0x3cu; o += 4u)
        U32(ui, 0x100 + o) = U32(p, P_STOCK_VALUES + o);
    if (LOG_EXT_ON())
        audio_log_extended(3u, module_tag, source_file, fn, 0x2aau, stock_code, p + P_STOCK_CODE,
                           p + P_STOCK_COMPANY, U32(p, P_STOCK_POINT_TOTAL));
    if (LOG_CMP_ON())
        (void)compress_log_output(0x0cc00000u, stock_code_short, stock_code_short, p + P_STOCK_CODE,
                                  p + P_STOCK_COMPANY, U32(p, P_STOCK_POINT_TOTAL));
    if (LOG_EXT_ON())
        audio_log_extended(3u, module_tag, source_file, fn, 0x2abu, stock_range,
                           (double)F32(p, P_STOCK_DAY_HIGH), (double)F32(p, P_STOCK_DAY_LOW),
                           (double)F32(p, P_STOCK_DARK_PRICE));
    if (LOG_CMP_ON())
        (void)compress_log_output(0x0cc00000u, stock_range_short, stock_range_short,
                                  (double)F32(p, P_STOCK_DAY_HIGH), (double)F32(p, P_STOCK_DAY_LOW),
                                  (double)F32(p, P_STOCK_DARK_PRICE));
    if (LOG_EXT_ON())
        audio_log_extended(3u, module_tag, source_file, fn, 0x2acu, stock_price,
                           (double)F32(p, P_STOCK_CHANGE_PCT), (double)F32(p, P_STOCK_CURRENT));
    if (LOG_CMP_ON())
        (void)compress_log_output(0x0c800000u, stock_price_short, stock_price_short,
                                  (double)F32(p, P_STOCK_CHANGE_PCT), (double)F32(p, P_STOCK_CURRENT));
    if (LOG_EXT_ON())
        audio_log_extended(3u, module_tag, source_file, fn, 0x2adu, stock_trend, U32(p, P_STOCK_TREND),
                           (double)F32(p, P_STOCK_OPEN));
    if (LOG_CMP_ON())
        (void)compress_log_output(0x0c800000u, stock_trend_short, stock_trend_short, U32(p, P_STOCK_TREND),
                                  (double)F32(p, P_STOCK_OPEN));
    audio_uart_checksum_copy(ui + 0x140, p + P_STOCK_POINTS, 0x2e4u);
    stock_page_push_data_4e9e32(ui, U32(p, P_STOCK_NUM), U32(p, P_STOCK_TOTAL));
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);

    if (U32(p, P_STOCK_TOTAL) != 0u) {
        if (g2_dashboard_stock_total_200743b0 != U32(p, P_STOCK_TOTAL)) {
            log_pair(4u, 0x2b9u, 0x10800000u, stock_total_changed, stock_total_changed_short,
                     g2_dashboard_stock_total_200743b0, U32(p, P_STOCK_TOTAL));
            g2_dashboard_stock_total_200743b0 = U32(p, P_STOCK_TOTAL);
            g2_dashboard_stock_received_200743ac = 0u;
        } else if (g2_dashboard_stock_total_200743b0 < g2_dashboard_stock_received_200743ac) {
            log_pair(4u, 0x2bfu, 0x10800000u, counter_overflow, counter_overflow_short,
                     g2_dashboard_stock_received_200743ac, g2_dashboard_stock_total_200743b0);
            g2_dashboard_stock_received_200743ac = 0u;
        }
        g2_dashboard_stock_total_200743b0 = U32(p, P_STOCK_TOTAL);
    }
    g2_dashboard_stock_received_200743ac++;
    log_pair(4u, 0x2c7u, 0x10800000u, stock_received, stock_received_short,
             g2_dashboard_stock_received_200743ac, g2_dashboard_stock_total_200743b0);
    all_received = g2_dashboard_stock_total_200743b0 <= g2_dashboard_stock_received_200743ac;
    if (all_received && dashboard_ui_ready()) {
        int32_t ret = post_event(DASHBOARD_MSG_STOCK);
        log_value(3u, 0x2d8u, 0x0c400000u, stock_refresh, stock_refresh_short, (uint32_t)ret);
    } else if (!all_received) {
        log_pair(4u, 0x2dau, 0x10800000u, stock_waiting, stock_waiting_short,
                 g2_dashboard_stock_received_200743ac, g2_dashboard_stock_total_200743b0);
    }
    if (all_received) {
        log_plain(3u, 0x2dfu, 0x0c000000u, stock_all, stock_all_short);
        g2_dashboard_stock_received_200743ac = 0u;
    }
    return 0u;
}

static void update_schedule(const uint8_t *p)
{
    uint8_t *const staging = g2_dashboard_schedule_staging_200e67f8;
    uint8_t *const ui = g2_dashboard_schedule_ui_2011df34;

    log_plain(4u, 0x2e5u, 0x10000000u, off_schedule, off_schedule_short);
    log_value(4u, 0x2e6u, 0x10400000u, sched_authority, sched_authority_short, U32(p, P_SCHED_AUTHORITY));
    log_pair(4u, 0x2e7u, 0x10800000u, sched_counts, sched_counts_short, U32(p, P_SCHED_NUM),
             U32(p, P_SCHED_TOTAL));
    if (U32(p, P_SCHED_TOTAL) == 0u) {
        log_plain(4u, 0x2ebu, 0x10000000u, sched_zero, sched_zero_short);
        dashboard_clear_calendar_ui_data_49c728();
        (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
        g2_dashboard_schedule_authority_2011efb8 = U32(p, P_SCHED_AUTHORITY);
        (void)osMutexRelease(g2_dashboard_mutex_200743a8);
        if ((uint8_t)audio_uart_service_mode() == 1u && audio_log_wake_allowed() == 1u &&
            audio_quicklist_refresh_enabled_4434d0(DASHBOARD_APP) == 1u) {
            int32_t ret = post_event(DASHBOARD_MSG_CALENDAR);
            log_value(4u, 0x2f8u, 0x10400000u, sched_clear_sent, sched_clear_sent_short, (uint32_t)ret);
        }
        return;
    }

    uint8_t *rec = staging + 4u + U32(p, P_SCHED_NUM) * SCHEDULE_RECORD_SIZE;
    U16(staging, 0) = (uint16_t)U32(p, P_SCHED_TOTAL);
    U32(rec, S_STAMP) = U32(p, P_SCHED_STAMP);
    audio_uart_checksum_copy(rec + S_TITLE, p + P_SCHED_TITLE, 0xb0u);
    audio_uart_checksum_copy(rec + S_LOCATION, p + P_SCHED_LOCATION, 0x11bu);
    audio_uart_checksum_copy(rec + S_TIME, p + P_SCHED_TIME, 0x40u);
    if (U32(p, P_SCHED_TOTAL) == U32(p, P_SCHED_NUM) + 1u) {
        /* Last event of the batch: publish the staging copy to the UI copy. */
        (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
        for (uint32_t i = 0u; i < U32(p, P_SCHED_TOTAL); i++) {
            uint8_t *dst = ui + 4u + i * SCHEDULE_RECORD_SIZE;
            const uint8_t *src = staging + 4u + i * SCHEDULE_RECORD_SIZE;
            audio_uart_checksum_copy(dst + S_TITLE, src + S_TITLE, 0xb0u);
            audio_uart_checksum_copy(dst + S_LOCATION, src + S_LOCATION, 0x11bu);
            audio_uart_checksum_copy(dst + S_TIME, src + S_TIME, 0x40u);
            U32(dst, S_STAMP) = U32(src, S_STAMP);
        }
        U16(ui, 0) = (uint16_t)U32(p, P_SCHED_TOTAL);
        U32(ui, SCHEDULE_UI_AUTHORITY) = U32(p, P_SCHED_AUTHORITY);
        (void)osMutexRelease(g2_dashboard_mutex_200743a8);
    }
    if ((uint8_t)audio_uart_service_mode() == 1u && audio_log_wake_allowed() == 1u &&
        audio_quicklist_refresh_enabled_4434d0(DASHBOARD_APP) == 1u &&
        (uint32_t)U16(ui, 0) == U32(p, P_SCHED_NUM) + 1u) {
        audio_uart_buffer_zero(g2_dashboard_event_buffer_200e3f20, sizeof g2_dashboard_event_buffer_200e3f20, 0u);
        g2_dashboard_event_buffer_200e3f20[0] = DASHBOARD_MSG_CALENDAR;
        int32_t ret = async_request_display_reflash_45aaca(DASHBOARD_APP, g2_dashboard_event_buffer_200e3f20, 1u, 500u);
        log_value(4u, 0x317u, 0x10400000u, sched_update_sent, sched_update_sent_short, (uint32_t)ret);
    }
}

uint32_t dashboard_async_update_data_49ce14(uint8_t *parsed)
{
    const uint8_t *const p = parsed;

    if (U8(p, P_NEWS_INFO) != 0u)
        return 2u;
    if (U8(p, P_NEWS_V2) != 0u) {
        log_plain(4u, 0x1eau, 0x10000000u, off_news_v2, off_news_v2_short);
        return 0u;
    }
    if (U8(p, P_HAS_SETTINGS) != 0u) {
        update_settings(p);
        return 0u;
    }
    if (U8(p, P_HAS_WEATHER) != 0u) {
        update_weather(p);
        return 0u;
    }
    if (U8(p, P_HAS_NEWS) != 0u) {
        log_plain(4u, 0x226u, 0x10000000u, off_news, off_news_short);
        log_plain(3u, 0x227u, 0x0c000000u, news_drop, news_drop_short);
        return 2u;
    }
    if (U8(p, P_HAS_STOCK) != 0u)
        return update_stock(p);
    if (U8(p, P_HAS_SCHEDULE) != 0u)
        update_schedule(p);
    return 0u;
}
