/* Dashboard application handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard.c.
 * Native 0x49ddb8..0x49e114, 0x49e144..0x49e40a, 0x49e448..0x49e650 and
 * 0x49e68c..0x49ea04; literal pools 0x49e114..0x49e144, 0x49e40c..0x49e448,
 * 0x49e650..0x49e68c and 0x49ea04..0x49eae2.
 *
 * UI registry row 3 (id 1, ROM 0x6a44e0) points its data handler at
 * Dashboard_common_data_handler and its UI handler at Dashboard_ui_event_handler.
 * Messages to the dashboard UI application (sync app 1) start with a type byte:
 *   1 display settings / weather   2 calendar        4 stock
 *   7 time {hour, minute, epoch hour}                8 auto-close timeout
 *   9 BLE link state               0x0f news cache   0x12 clear all
 *   0x13 ring status {connected, battery}
 * dashboard_async_update_data 0x49ce14 is in dashboard_async_update_data.c. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define DASHBOARD_APP 1u
#define ROLE_1 1u
#define ROLE_2 2u
#define AUTO_CLOSE_DISABLED 0xff55u
#define AUTO_CLOSE_TICKS_PER_UNIT 0x41u
#define FOREGROUND_DASHBOARD 0x21u

enum {
    DASHBOARD_MSG_TIME = 7u,
    DASHBOARD_MSG_AUTO_CLOSE = 8u,
    DASHBOARD_MSG_BLE_STATE = 9u,
    DASHBOARD_MSG_NEWS_CACHE = 0x0fu,
    DASHBOARD_MSG_CLEAR_ALL = 0x12u,
    DASHBOARD_MSG_RING_STATUS = 0x13u,
};
enum { /* Dashboard_common_data_handler sub-events (event 5) */
    DASHBOARD_NEWS_LOAD_CACHE_NEWS_DATA_EVENT = 0x10u,
    DASHBOARD_CLEAR_ALL_DATA_EVENT = 0x11u,
    DASHBOARD_RING_STATUS_CHANGE_EVENT = 0x13u,
};
enum { /* Dashboard_ui_event_handler */
    UI_EVENT_TYPE_INIT = 2,
    UI_EVENT_TYPE_REFLASH = 3,
    UI_EVENT_TYPE_TICK = 4,
    UI_EVENT_TYPE_EXIT = 5,
};
enum { /* dashboard_page_event_handler */
    PAGE_EVENT_REFRESH_0A = 0x0a,
    PAGE_EVENT_IMU_REFLASH = 0x40,
    PAGE_EVENT_FOREGROUND = 0x42,
    PAGE_EVENT_BACKGROUND = 0x43,
    PAGE_EVENT_44 = 0x44,
    PAGE_EVENT_45 = 0x45,
    PAGE_EVENT_48 = 0x48,
    PAGE_EVENT_49 = 0x49,
    PAGE_EVENT_4A = 0x4a,
};

/* am_hal_rtc_time_t word layout as filled by service_time_current_calendar_get. */
typedef struct {
    uint32_t read_error; /* +0 */
    uint32_t weekday;    /* +4 */
    uint32_t century;    /* +8 */
    uint32_t year;       /* +12 */
    uint32_t month;      /* +16 */
    uint32_t day;        /* +20 */
    uint32_t hour;       /* +24 */
    uint32_t minute;     /* +28 */
    uint32_t second;     /* +32 */
    uint32_t hundredths; /* +36 */
} g2_calendar_t;
_Static_assert(sizeof(g2_calendar_t) == 40u, "am_hal_rtc_time_t");

typedef void (*g2_status_cb_t)(uint32_t event, const void *data);

extern uint8_t g2_dashboard_parsed_data_20366718[];        /* RAM 0x20366718 parsed package (0x14ba+ bytes) */
extern uint8_t g2_dashboard_news_cache_20132f74[0x8ef8];   /* RAM 0x20132f74 */
extern volatile uint32_t g2_dashboard_widgets_darkened_200743b4; /* RAM 0x200743b4 */
extern void *volatile g2_dashboard_root_200743b8;          /* RAM 0x200743b8 dashboard screen object */
extern volatile uint32_t g2_dashboard_last_hour_200743bc;  /* RAM 0x200743bc */
extern volatile uint32_t g2_dashboard_last_minute_200743c0; /* RAM 0x200743c0 */
extern volatile uint32_t g2_dashboard_last_month_200743c4; /* RAM 0x200743c4 */
extern volatile uint32_t g2_dashboard_last_day_200743c8;   /* RAM 0x200743c8 */
extern volatile uint32_t g2_dashboard_last_weekday_200743cc; /* RAM 0x200743cc */
extern volatile uint32_t audio_dashboard_auto_close_current_200743d0; /* RAM 0x200743d0 countdown */
extern volatile uint32_t audio_dashboard_auto_close_default_200743d4; /* RAM 0x200743d4 */
extern volatile uint32_t g2_dashboard_auto_close_enabled_200743d8;    /* RAM 0x200743d8 */
extern volatile uint32_t g2_dashboard_auto_close_hold_20074ba0;       /* RAM 0x20074ba0 */
extern volatile uint8_t g2_dashboard_auto_close_fired_20074fa3;       /* RAM 0x20074fa3 */
extern volatile uint8_t g2_dashboard_backgrounded_20074fa4;           /* RAM 0x20074fa4 */
extern uint8_t audio_uart_registry_context_200005bc;       /* RAM 0x200005bc registry row 3 context, +4 root */

extern uint32_t dashboard_async_update_data_49ce14(uint8_t *parsed);
extern void dashboard_data_mutex_init_49c09a(void);
extern void dashboard_send_initial_notification_status_to_app_49c25a(void);
extern void darken_tile_indicators_49c7fe(void);
extern void resume_tile_indicators_49c89e(void);
extern void darken_widget_colors_recursive_49c93e(void *obj);
extern void resume_widget_colors_recursive_49cb50(void *obj);
extern void dashboard_msg_count_callback_49c2b0(uint32_t event, const void *data);
extern void dashboard_battery_callback_49c3d8(uint32_t event, uint32_t *value);
extern void dashboard_ring_battery_callback_49c5c4(uint32_t event, uint32_t *value);
extern uint8_t dashboard_parse_data_package_4fe318(const uint8_t *data, uint32_t length, uint8_t *parsed);
extern void dashboard_respond_NewsInfo_to_app_4fedcc(uint32_t ret);
extern void dashboard_respond_to_app_serialize_4fec98(uint32_t ret);
extern void load_news_cache_data_to_disp_buffer_4fdf74(uint8_t *news_widget_data);
extern void clear_news_cache_data_to_disp_buffer_4fdf08(void);
extern void dashboard_main_screen_event_4e814c(int32_t event, const void *param);
extern int32_t Dashboard_ReflashEventHandler_4e8dec(uint32_t arg0, uint32_t arg1);
extern void dashboard_main_screen_tick_4e923c(uint32_t arg0, uint32_t arg1);
extern void ui_Screen1_Deinit_4e8000(void);
extern void Calendar_expire_check_4efa78(void);
extern void page_state_sync_init_4ffe14(void);
extern void audio_uart_service_prepare9(uint32_t);           /* dashboard.ext 0x501066 */
extern uint8_t *settings_get_config(void);                   /* 0x46b44c */
extern void setting_notify_device_status_to_app(void);       /* 0x49be04 */
extern uint32_t quicklist_data_mutex_init(void);             /* 0x4ffa70 */
extern uint32_t health_data_mutex_init(void);                /* 0x4ffbd8 */
extern void cb_ring_battery_forwarder(void *context);        /* 0x500378 */
extern uint32_t CB_BLE_STATUS_RegisterCallback(g2_status_cb_t callback);   /* 0x4abcc6 */
extern void CB_BLE_STATUS_UnregisterCallback(g2_status_cb_t callback);     /* 0x4abd14 */
extern uint32_t CB_ANCC_RegisterMsgCountCallback(g2_status_cb_t callback); /* 0x4e1a5e */
extern void CB_ANCC_UnregisterMsgCountCallback(g2_status_cb_t callback);   /* 0x4e1aac */
extern uint32_t CB_CHG_RegisterBatInfoCallback(void (*callback)(uint32_t, uint32_t *)); /* 0x4aea56 */
extern void CB_CHG_UnregisterBatInfoCallback(void (*callback)(uint32_t, uint32_t *));   /* 0x4aeaa4 */
extern uint32_t CB_RING_BAT_RegisterCallback(void (*callback)(uint32_t, uint32_t *));   /* 0x500396 */
extern void dashboard_watchface_manager_call_10(uint32_t weekday, uint32_t month, uint32_t day,
                                                uint8_t date_format); /* 0x500660 */
extern uint8_t svc_universal_setting_get_date_format_466500(void);
extern uint32_t get_dashboard_auto_close_value_47121c(void);
extern void service_time_current_calendar_get(g2_calendar_t *calendar); /* 0x44a19a */
extern uint32_t service_time_current_epoch_get(void);                   /* 0x44a1c6 */
extern uint8_t audio_uart_device_role_get(void);                        /* 0x45a568 */
extern uint32_t audio_log_wake_allowed(void);                           /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t id);
/* Stock returns the request status; the current g2/src definition is void. */
extern int32_t audio_uart_master_display_refresh(uint32_t id, const void *payload, uint16_t length,
                                                 uint32_t extra); /* 0x464bb2 */
extern int32_t async_request_display_reflash_45aaca(uint32_t application, const void *payload,
                                                    uint32_t length, uint32_t delay);
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t length,
                                                   uint32_t id, uint32_t event);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);     /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "dashboard"; /* ROM 0x78a6b8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard.c"; /* ROM 0x701624 */
static const char data_handler_fn[] = "Dashboard_common_data_handler"; /* ROM 0x75ef30 */
static const char recv_data[] = "Dashboard recv data len = %d, raw_data=%p"; /* ROM 0x73d664 */
static const char recv_data_short[] = "[dashboard]Dashboard recv data len = %d, raw_data=%p"; /* ROM 0x71d570 */
static const char parse_failed[] = "dashboard_parse_data_package failed!\n"; /* ROM 0x748c8c */
static const char parse_failed_short[] = "[dashboard]dashboard_parse_data_package failed!\n"; /* ROM 0x7283ac */
static const char load_news[] = "DASHBOARD_NEWS_LOAD_CACHE_NEWS_DATA_EVENT, load cache news data"; /* ROM 0x70a6a4 */
static const char load_news_short[] =
    "[dashboard]DASHBOARD_NEWS_LOAD_CACHE_NEWS_DATA_EVENT, load cache news data"; /* ROM 0x6f2984 */
static const char news_sent[] = "dashboard send news event to UI application, ret = %d"; /* ROM 0x71d5a8 */
static const char news_sent_short[] = "[dashboard]dashboard send news event to UI application, ret = %d"; /* ROM 0x701910 */
static const char clear_all[] = "DASHBOARD_CLEAR_ALL_DATA_EVENT, clear all data"; /* ROM 0x732b04 */
static const char clear_all_short[] = "[dashboard]DASHBOARD_CLEAR_ALL_DATA_EVENT, clear all data"; /* ROM 0x713ae0 */
static const char ring_change[] = "DASHBOARD_RING_STATUS_CHANGE_EVENT, ring status change"; /* ROM 0x71d5e0 */
static const char ring_change_short[] =
    "[dashboard]DASHBOARD_RING_STATUS_CHANGE_EVENT, ring status change"; /* ROM 0x701954 */
static const char page_handler_fn[] = "dashboard_page_event_handler"; /* ROM 0x75ef50 */
static const char foreground[] = "foregroundID = %d"; /* ROM 0x77eb40 */
static const char foreground_short[] = "[dashboard]foregroundID = %d"; /* ROM 0x75ef70 */
static const char darken[] = "darken_widget_colors_recursive"; /* ROM 0x75ef90 */
static const char darken_short[] = "[dashboard]darken_widget_colors_recursive"; /* ROM 0x73d690 */
static const char resume[] = "resume_widget_colors_recursive"; /* ROM 0x75efb0 */
static const char resume_short[] = "[dashboard]resume_widget_colors_recursive"; /* ROM 0x73d6bc */
static const char imu_reflash[] = "IMU Reflash Event."; /* ROM 0x77eb54 */
static const char imu_reflash_short[] = "[dashboard]IMU Reflash Event."; /* ROM 0x75efd0 */
static const char ble_cb_fn[] = "BleConnectStatusNotifyCallback"; /* ROM 0x75eff0 */
static const char ble_event[] = "BleConnectStatusNotifyCallback eventType = %d"; /* ROM 0x732b34 */
static const char ble_event_short[] = "[dashboard]BleConnectStatusNotifyCallback eventType = %d"; /* ROM 0x713b1c */
static const char ble_data[] = "BleConnectStatusNotifyCallback _data = %d"; /* ROM 0x73d6e8 */
static const char ble_data_short[] = "[dashboard]BleConnectStatusNotifyCallback _data = %d"; /* ROM 0x71d618 */
static const char ble_unsupported[] = "BleConnectStatusNotifyCallback _data = %d, not supported"; /* ROM 0x713b58 */
static const char ble_unsupported_short[] =
    "[dashboard]BleConnectStatusNotifyCallback _data = %d, not supported"; /* ROM 0x701998 */
static const char ui_handler_fn[] = "Dashboard_ui_event_handler"; /* ROM 0x76a930 */
static const char ui_init[] = "Dashboard_ui_event_handler UI_EVENT_TYPE_INIT"; /* ROM 0x732b64 */
static const char ui_init_short[] = "[dashboard]Dashboard_ui_event_handler UI_EVENT_TYPE_INIT"; /* ROM 0x713b94 */
static const char no_auto_close[] =
    "dashboard_ui_event_handler Dashboard auto close value is 0xFF55, not auto close"; /* ROM 0x6ec8e8 */
static const char no_auto_close_short[] =
    "[dashboard]dashboard_ui_event_handler Dashboard auto close value is 0xFF55, not auto close"; /* ROM 0x6dfe44 */
static const char auto_close_exit[] = "dashboard_ui_event_handler DISPLAY_AUTO_REFLASH timeout exit"; /* ROM 0x70a6e4 */
static const char auto_close_exit_short[] =
    "[dashboard]dashboard_ui_event_handler DISPLAY_AUTO_REFLASH timeout exit"; /* ROM 0x6f9884 */
static const char ui_exit[] = "Dashboard_ui_event_handler UI_EVENT_TYPE_EXIT"; /* ROM 0x732b94 */
static const char ui_exit_short[] = "[dashboard]Dashboard_ui_event_handler UI_EVENT_TYPE_EXIT"; /* ROM 0x713bd0 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

static bool dashboard_ui_ready(void)
{
    return audio_uart_device_role_get() == ROLE_1 && audio_log_wake_allowed() == 1u &&
           audio_quicklist_refresh_enabled_4434d0(DASHBOARD_APP) == 1u;
}

/* {DASHBOARD_MSG_TIME, hour, minute, hour of the epoch clock}. */
static void dashboard_time_message(uint8_t msg[4], uint32_t hour, uint32_t minute, uint32_t epoch)
{
    audio_uart_buffer_zero(msg, 4u, 0u);
    audio_uart_buffer_zero(msg, 4u, 0u);
    msg[0] = DASHBOARD_MSG_TIME;
    msg[1] = (uint8_t)hour;
    msg[2] = (uint8_t)minute;
    msg[3] = (uint8_t)((epoch / 3600u) % 24u);
}

uint32_t Dashboard_common_data_handler_49ddb8(uint32_t event, const uint8_t *data, uint32_t length)
{
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, data_handler_fn, 0x320u, recv_data, length, data);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10800000u, recv_data_short, recv_data_short, length, data);
    dashboard_data_mutex_init_49c09a();
    if (event == 0u) {
        uint8_t *const parsed = g2_dashboard_parsed_data_20366718;
        if (data == NULL || length == 0u)
            return 0u;
        if (dashboard_parse_data_package_4fe318(data, length, parsed) == 0u) {
            if (LOG_EXT_ON())
                audio_log_extended(1u, module_tag, source_file, data_handler_fn, 0x327u, parse_failed);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x04000000u, parse_failed_short, parse_failed_short);
            return 0u;
        }
        uint32_t ret = dashboard_async_update_data_49ce14(parsed);
        if (parsed[0x14b8] == 1u)
            dashboard_respond_NewsInfo_to_app_4fedcc(ret);
        else if (parsed[0x14b9] != 1u)
            dashboard_respond_to_app_serialize_4fec98(parsed[0x14b3] == 1u ? 1u : ret);
        return 0u;
    }
    if (event != 5u)
        return 0u;
    if (data[0] == DASHBOARD_NEWS_LOAD_CACHE_NEWS_DATA_EVENT) {
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, data_handler_fn, 0x34bu, load_news);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c000000u, load_news_short, load_news_short);
        load_news_cache_data_to_disp_buffer_4fdf74(g2_dashboard_news_cache_20132f74);
        if (dashboard_ui_ready()) {
            uint8_t msg[5];
            audio_uart_buffer_zero(msg, sizeof msg, 0u);
            msg[0] = DASHBOARD_MSG_NEWS_CACHE;
            int32_t ret = async_request_display_reflash_45aaca(DASHBOARD_APP, msg, 1u, 100u);
            if (LOG_EXT_ON())
                audio_log_extended(4u, module_tag, source_file, data_handler_fn, 0x355u, news_sent, ret);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x10400000u, news_sent_short, news_sent_short, ret);
        }
    } else if (data[0] == DASHBOARD_CLEAR_ALL_DATA_EVENT) {
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, data_handler_fn, 0x35bu, clear_all);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c000000u, clear_all_short, clear_all_short);
        clear_news_cache_data_to_disp_buffer_4fdf08();
        audio_uart_buffer_zero(g2_dashboard_news_cache_20132f74, sizeof g2_dashboard_news_cache_20132f74, 0u);
        if (dashboard_ui_ready()) {
            uint8_t msg[5];
            audio_uart_buffer_zero(msg, sizeof msg, 0u);
            msg[0] = DASHBOARD_MSG_CLEAR_ALL;
            int32_t ret = async_request_display_reflash_45aaca(DASHBOARD_APP, msg, 1u, 100u);
            if (LOG_EXT_ON())
                audio_log_extended(4u, module_tag, source_file, data_handler_fn, 0x365u, news_sent, ret);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x10400000u, news_sent_short, news_sent_short, ret);
        }
    } else if (data[0] == DASHBOARD_RING_STATUS_CHANGE_EVENT) {
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, data_handler_fn, 0x36bu, ring_change);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c000000u, ring_change_short, ring_change_short);
        if (dashboard_ui_ready()) {
            /* The whole payload (stock: `length` bytes) is forwarded as a 3-byte message. */
            uint8_t msg[3];
            audio_uart_buffer_zero(msg, sizeof msg, 0u);
            audio_uart_buffer_zero(msg, sizeof msg, 0u);
            audio_uart_checksum_copy(msg, data, length);
            (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, 3u, 0u);
        }
    }
    return 0u;
}

uint32_t dashboard_page_event_handler_49e144(uint32_t arg0, uint32_t arg1, int32_t event,
                                            const int32_t *param)
{
    (void)arg0;
    (void)arg1;
    if (event == PAGE_EVENT_FOREGROUND) {
        int32_t foreground_id = 0;
        if (param != NULL)
            foreground_id = *param;
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, page_handler_fn, 0x38au, foreground, foreground_id);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c400000u, foreground_short, foreground_short, foreground_id);
        /* Another application came to the foreground: dim the dashboard. */
        if (g2_dashboard_root_200743b8 != NULL && foreground_id != 0 &&
            foreground_id != (int32_t)FOREGROUND_DASHBOARD) {
            if (LOG_EXT_ON())
                audio_log_extended(4u, module_tag, source_file, page_handler_fn, 0x38cu, darken);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x10000000u, darken_short, darken_short);
            darken_tile_indicators_49c7fe();
            darken_widget_colors_recursive_49c93e(g2_dashboard_root_200743b8);
            g2_dashboard_widgets_darkened_200743b4 = 1u;
        }
        if (audio_uart_device_role_get() == ROLE_1) {
            g2_dashboard_backgrounded_20074fa4 = 1u;
            audio_dashboard_auto_close_current_200743d0 = audio_dashboard_auto_close_default_200743d4;
        }
        return 1u;
    }
    if (event == PAGE_EVENT_BACKGROUND) {
        /* Stock also loads param[3] here and discards it. */
        if (g2_dashboard_root_200743b8 != NULL && g2_dashboard_widgets_darkened_200743b4 == 1u) {
            if (LOG_EXT_ON())
                audio_log_extended(4u, module_tag, source_file, page_handler_fn, 0x39cu, resume);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x10000000u, resume_short, resume_short);
            resume_tile_indicators_49c89e();
            resume_widget_colors_recursive_49cb50(g2_dashboard_root_200743b8);
            g2_dashboard_widgets_darkened_200743b4 = 0u;
        }
        if (audio_uart_device_role_get() == ROLE_1) {
            g2_calendar_t now;
            uint8_t msg[4];
            g2_dashboard_backgrounded_20074fa4 = 0u;
            audio_dashboard_auto_close_current_200743d0 = audio_dashboard_auto_close_default_200743d4;
            service_time_current_calendar_get(&now);
            uint32_t epoch = service_time_current_epoch_get();
            dashboard_time_message(msg, now.hour, now.minute, epoch);
            (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, 4u, 0u);
        }
        return 1u;
    }
    if (event == PAGE_EVENT_REFRESH_0A || event == PAGE_EVENT_48 || event == PAGE_EVENT_44 ||
        event == PAGE_EVENT_45) {
        if (audio_uart_device_role_get() == ROLE_2)
            return 1u;
        dashboard_main_screen_event_4e814c(event, param);
        audio_dashboard_auto_close_current_200743d0 = audio_dashboard_auto_close_default_200743d4;
        return 1u;
    }
    if (event == PAGE_EVENT_49)
        return 1u;
    if (event == PAGE_EVENT_4A) {
        (void)audio_uart_device_role_get();
        return 1u;
    }
    if (event == PAGE_EVENT_IMU_REFLASH) {
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, page_handler_fn, 1000u, imu_reflash);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10000000u, imu_reflash_short, imu_reflash_short);
    }
    return 1u;
}

/* Post a ring status record {0x13, connected, battery} to both arms. */
void dashboard_ring_status_post_49e448(uint8_t connected, uint8_t battery)
{
    uint8_t msg[3];
    audio_uart_buffer_zero(msg, sizeof msg, 0u);
    audio_uart_buffer_zero(msg, sizeof msg, 0u);
    msg[0] = DASHBOARD_MSG_RING_STATUS;
    msg[1] = connected;
    msg[2] = battery;
    (void)audio_sync_send_to_both_ext_464f76(DASHBOARD_APP, msg, sizeof msg, 0u, 5u);
}

/* CB_BLE_STATUS callback: event 0 is the phone link, event 1 the ring link. */
void BleConnectStatusNotifyCallback_49e486(uint32_t event, const void *payload)
{
    const uint8_t *data = payload;
    if (LOG_EXT_ON())
        audio_log_extended(3u, module_tag, source_file, ble_cb_fn, 0x422u, ble_event, event);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x0c400000u, ble_event_short, ble_event_short, event);
    if (event == 0u) {
        uint8_t state = data[0];
        uint8_t msg[2];
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, ble_cb_fn, 0x425u, ble_data, state);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c400000u, ble_data_short, ble_data_short, state);
        audio_uart_buffer_zero(msg, sizeof msg, 0u);
        audio_uart_buffer_zero(msg, sizeof msg, 0u);
        msg[0] = DASHBOARD_MSG_BLE_STATE;
        msg[1] = state;
        (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, 2u, 0u);
    } else if (event == 1u) {
        uint8_t state = data[0];
        uint8_t msg[3];
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, ble_cb_fn, 0x42du, ble_data, state);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c400000u, ble_data_short, ble_data_short, state);
        audio_uart_buffer_zero(msg, sizeof msg, 0u);
        audio_uart_buffer_zero(msg, sizeof msg, 0u);
        msg[0] = DASHBOARD_MSG_RING_STATUS;
        if (state == 0u) {
            msg[1] = 0u;
        } else if (state == 1u) {
            msg[1] = 1u;
        } else {
            if (LOG_EXT_ON())
                audio_log_extended(2u, module_tag, source_file, ble_cb_fn, 0x436u, ble_unsupported, state);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x08400000u, ble_unsupported_short, ble_unsupported_short, state);
            return;
        }
        msg[2] = 0u;
        (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, 3u, 0u);
    }
}

int32_t Dashboard_ui_event_handler_49e68c(int32_t event, uint32_t arg1, uint32_t arg2, void *context)
{
    if (event == UI_EVENT_TYPE_INIT) {
        g2_dashboard_widgets_darkened_200743b4 = 0u;
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, ui_handler_fn, 0x443u, ui_init);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10000000u, ui_init_short, ui_init_short);
        *(uint32_t *)(void *)(settings_get_config() + 0x34) = 1u;
        setting_notify_device_status_to_app();
        dashboard_data_mutex_init_49c09a();
        (void)quicklist_data_mutex_init();
        (void)health_data_mutex_init();
        page_state_sync_init_4ffe14();
        cb_ring_battery_forwarder(context);
        *(void **)(void *)(&audio_uart_registry_context_200005bc + 4) = g2_dashboard_root_200743b8;
        if (audio_uart_device_role_get() == ROLE_1) {
            g2_calendar_t now;
            uint8_t msg[4];
            (void)CB_BLE_STATUS_RegisterCallback(BleConnectStatusNotifyCallback_49e486);
            (void)CB_ANCC_RegisterMsgCountCallback(dashboard_msg_count_callback_49c2b0);
            (void)CB_CHG_RegisterBatInfoCallback(dashboard_battery_callback_49c3d8);
            (void)CB_RING_BAT_RegisterCallback(dashboard_ring_battery_callback_49c5c4);
            dashboard_send_initial_notification_status_to_app_49c25a();
            service_time_current_calendar_get(&now);
            uint32_t epoch = service_time_current_epoch_get();
            dashboard_time_message(msg, now.hour, now.minute, epoch);
            (void)async_request_display_reflash_45aaca(DASHBOARD_APP, msg, 4u, 400u);
            uint32_t auto_close = get_dashboard_auto_close_value_47121c();
            if (auto_close == AUTO_CLOSE_DISABLED) {
                g2_dashboard_auto_close_enabled_200743d8 = 0u;
                if (LOG_EXT_ON())
                    audio_log_extended(3u, module_tag, source_file, ui_handler_fn, 0x46eu, no_auto_close);
                if (LOG_CMP_ON())
                    (void)compress_log_output(0x0c000000u, no_auto_close_short, no_auto_close_short);
            } else {
                g2_dashboard_auto_close_enabled_200743d8 = 1u;
            }
            audio_dashboard_auto_close_current_200743d0 = auto_close * AUTO_CLOSE_TICKS_PER_UNIT;
            audio_dashboard_auto_close_default_200743d4 = audio_dashboard_auto_close_current_200743d0;
            g2_dashboard_auto_close_fired_20074fa3 = 0u;
            g2_dashboard_backgrounded_20074fa4 = 0u;
        }
        return 0;
    }
    if (event == UI_EVENT_TYPE_REFLASH)
        return Dashboard_ReflashEventHandler_4e8dec(arg1, arg2);
    if (event == UI_EVENT_TYPE_TICK) {
        g2_calendar_t now;
        service_time_current_calendar_get(&now);
        if (audio_uart_device_role_get() == ROLE_1) {
            if (g2_dashboard_backgrounded_20074fa4 == 0u && g2_dashboard_auto_close_hold_20074ba0 == 0u &&
                (int32_t)--audio_dashboard_auto_close_current_200743d0 < 1 &&
                g2_dashboard_auto_close_fired_20074fa3 == 0u && g2_dashboard_auto_close_enabled_200743d8 == 1u) {
                uint8_t msg[2];
                g2_dashboard_auto_close_fired_20074fa3 = 1u;
                if (LOG_EXT_ON())
                    audio_log_extended(3u, module_tag, source_file, ui_handler_fn, 0x484u, auto_close_exit);
                if (LOG_CMP_ON())
                    (void)compress_log_output(0x0c000000u, auto_close_exit_short, auto_close_exit_short);
                audio_uart_buffer_zero(msg, sizeof msg, 0u);
                audio_uart_buffer_zero(msg, sizeof msg, 0u);
                msg[0] = DASHBOARD_MSG_AUTO_CLOSE;
                (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, 2u, 0u);
            }
            if (g2_dashboard_last_hour_200743bc != now.hour || g2_dashboard_last_minute_200743c0 != now.minute) {
                g2_dashboard_last_hour_200743bc = now.hour;
                g2_dashboard_last_minute_200743c0 = now.minute;
                if (audio_uart_device_role_get() == ROLE_1) {
                    uint8_t msg[4];
                    uint32_t epoch = service_time_current_epoch_get();
                    dashboard_time_message(msg, now.hour, now.minute, epoch);
                    (void)audio_uart_master_display_refresh(DASHBOARD_APP, msg, 4u, 0u);
                }
            }
            Calendar_expire_check_4efa78();
        }
        if (g2_dashboard_last_month_200743c4 != now.month || g2_dashboard_last_day_200743c8 != now.day ||
            g2_dashboard_last_weekday_200743cc != now.weekday) {
            g2_dashboard_last_month_200743c4 = now.month;
            g2_dashboard_last_day_200743c8 = now.day;
            g2_dashboard_last_weekday_200743cc = now.weekday;
            dashboard_watchface_manager_call_10(now.weekday, now.month, now.day,
                                                svc_universal_setting_get_date_format_466500());
        }
        dashboard_main_screen_tick_4e923c(arg1, arg2);
        return 0;
    }
    if (event == UI_EVENT_TYPE_EXIT) {
        if (LOG_EXT_ON())
            audio_log_extended(4u, module_tag, source_file, ui_handler_fn, 0x4afu, ui_exit);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x10000000u, ui_exit_short, ui_exit_short);
        if (audio_uart_device_role_get() == ROLE_1) {
            CB_BLE_STATUS_UnregisterCallback(BleConnectStatusNotifyCallback_49e486);
            CB_ANCC_UnregisterMsgCountCallback(dashboard_msg_count_callback_49c2b0);
            CB_CHG_UnregisterBatInfoCallback(dashboard_battery_callback_49c3d8);
            *(uint32_t *)(void *)(settings_get_config() + 0x34) = 0u;
            setting_notify_device_status_to_app();
        }
        audio_uart_service_prepare9(0u);
        ui_Screen1_Deinit_4e8000();
        g2_dashboard_widgets_darkened_200743b4 = 0u;
        return 0;
    }
    return event;
}
