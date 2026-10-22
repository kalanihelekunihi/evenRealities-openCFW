/* Navigation app main module, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation.c (log tag "navigation.main").
 * Native 0x585cba..0x586389 (page-manager getters, navigation_page_event_handler,
 * navigation_ui_event_handler); literal pool 0x58638c..0x586447 ("AM"/"PM" at
 * 0x58638c/0x586390). The registry pair at 0x585cca (data callback, in
 * system/registry-callback) and the mutex helper 0x585ca4 (rtos-glue-gaps)
 * belong to the same address run.
 *
 * navigation_ui_event_handler is the UI callback of display registry row 14
 * (ROM 0x6a4590, app id 8, context 0x20002ce0), declared there as
 * audio_uart_registry_callback_58607a; that name is kept so the table links.
 * Its events: 2 init (create the startup page), 3 data refresh, 4 periodic
 * tick (heartbeat / exit countdown / clock labels / calibration animation),
 * 5 display exit (tear down, report the session length). */
#include <stdint.h>
#include <stddef.h>

#define NAV_APP_ID                  8u
#define DEVICE_ROLE_MASTER          1u
#define DEVICE_ROLE_SINGLE          2u   /* role 2: input events are not forwarded */
#define SYSTEM_ALERT_APP_ID         0x21u

enum {
    PAGE_EVENT_INPUT_0A          = 0x0a,
    PAGE_EVENT_IMU_REFLASH       = 0x40,
    PAGE_EVENT_IMU_COMPASS       = 0x41,
    PAGE_EVENT_FOREGROUND_ENTER  = 0x42,
    PAGE_EVENT_FOREGROUND_LEAVE  = 0x43,
    PAGE_EVENT_INPUT_44          = 0x44,
    PAGE_EVENT_INPUT_45          = 0x45,
    PAGE_EVENT_INPUT_48          = 0x48,
    PAGE_EVENT_SYSTEM_EXIT_NOTIFY = 0x4f,
    PAGE_EVENT_IMU_COMPASS_50    = 0x50,
};

enum {
    UI_EVENT_TYPE_INIT    = 2,
    UI_EVENT_TYPE_REFRESH = 3,
    UI_EVENT_TYPE_TICK    = 4,
    UI_EVENT_DISPLAY_EXIT = 5,
};

#define LV_OPA_50   0x7fu
#define LV_OPA_COVER 0xffu

#define HEARTBEAT_TICKS      61   /* tick events per heartbeat step */
#define HEARTBEAT_RELOAD     20u
#define EXIT_COUNTDOWN_RELOAD 240u
#define NAV_SESSION_EVENT_ID 0x40103u

/* am_hal_rtc_time_t word layout as filled by service_time. */
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
_Static_assert(sizeof(g2_calendar_t) == 40, "calendar is 10 words");

/* Only the first field of the generic animation is touched here. */
typedef struct {
    void *image; /* +0 lv image object */
} g2_nav_anim_head_t;

/* Session-length report: ROM template 0x78dd2c {4, 0}, word 1 replaced. */
typedef struct {
    uint32_t kind;     /* +0 */
    uint32_t seconds;  /* +4 */
} g2_nav_session_report_t;

extern void *g2_navigation_page_root_20074718;          /* RAM 0x20074718 page root (576x288) */
extern uint32_t g2_navigation_var_20074720;            /* RAM 0x20074720 page manager */
extern uint32_t g2_nav_opacity_lowered_20074724;       /* RAM 0x20074724 1 after opacity set to 50% */
extern uint32_t g2_nav_start_tick_20074728;            /* RAM 0x20074728 tick at UI init */
extern uint32_t g2_nav_fadeout_pending_2007472c;       /* RAM 0x2007472c */
extern void *g2_nav_ui_context_20074730;               /* RAM 0x20074730 registry context of the last init */
extern uint32_t g2_navigation_var_20074744;            /* RAM 0x20074744 tick counter */
extern uint32_t g2_nav_var_20074748;                   /* RAM 0x20074748 exit countdown 0xf0 */
extern uint32_t g2_nav_var_2007474c;                   /* RAM 0x2007474c exit page active */
extern g2_nav_anim_head_t *g2_nav_calibrate_anim_20074750; /* RAM 0x20074750 */
extern uint32_t g2_navigation_clock_hour_2007475c;     /* RAM 0x2007475c */
extern uint32_t g2_navigation_clock_minute_20074760;   /* RAM 0x20074760 */
extern void *g2_nav_b_clock_label_20074764;            /* RAM 0x20074764 */
extern void *g2_nav_a_clock_label_200747e0;            /* RAM 0x200747e0 */
extern uint8_t g2_navigation_flag_20074fe6;            /* RAM 0x20074fe6 foreground layer active */
extern uint8_t g2_navigation_ui_state_20074fed;        /* RAM 0x20074fed */
extern uint32_t g2_nav_var_20002cfc;                   /* RAM 0x20002cfc (.data) heartbeat counter */
extern uint8_t audio_uart_registry_context_20002ce0;   /* RAM 0x20002ce0 registry row 14 context; +4 page root */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t selector); /* lv_obj_set_style_opa */
extern uint32_t display_driver_uled_mode_45a568(void);   /* device role, 1 = master */
extern uint32_t audio_uart_service_mode(void);           /* 0x45a570, 1 = master */
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len, uint32_t context); /* RequestDisplayStop */
extern void audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len, uint32_t flags); /* 0x464bb2 */
extern int32_t NavigationInputEventHandler_548f80(uint32_t event, const void *param);
extern uint32_t osKernelGetTickCount(void); /* 0x4490cc */
extern void ble_state_skip_manual_start(uint8_t value); /* 0x478110 */
extern int32_t navigation_ui_startup_page_create_545d18(void *parent, const uint8_t *msg, uint16_t wait_map);
extern void page_fade_in_anim_start_46410a(void *root);
extern int32_t navigation_ui_reflash_page_handler_549c24(const uint8_t *data, uint16_t length);
extern void aeabi_memset_43c0e4(void *dst, uint32_t len, uint32_t fill); /* memset (dst, n, c) */
extern uint32_t service_time_current_epoch_get(void); /* 0x44a1c6 */
extern void service_time_epoch_to_calendar(uint32_t epoch, g2_calendar_t *out); /* 0x44a100 */
extern uint32_t audio_time_format_mode_46650c(void); /* 1 = 12-hour */
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj); /* lv_obj_is_valid */
extern void audio_lv_label_text_49942e(void *label, const char *text); /* lv_label_set_text */
extern void generic_animation_update_463f34(void *anim);
extern uint32_t generic_animation_get_frame_463fa4(const void *anim);
extern void generic_animation_destroy_463e1c(void *anim, uint8_t delete_image);
extern uint32_t navigation_ui_exit_page_handler_54c268(void);
extern void audio_ble_param_reset_delayed_event(uint32_t delay); /* 0x478252 */
extern int32_t StopIMUCompassFunc_54566c(void);
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t lo, uint32_t hi, uint32_t dlo, uint32_t dhi); /* u64 / u64 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload); /* event report */

void *navigation_page_manager_get_585cba(void);
uint8_t navigation_foreground_layer_active_585cc2(void);
uint32_t navigation_page_event_handler_585ce0(uint32_t unused, uint32_t manager, uint32_t event, const uint32_t *data);
int32_t audio_uart_registry_callback_58607a(int32_t event, const uint8_t *payload, uint32_t length, void *context);

static const char module_tag[] = "navigation.main"; /* ROM 0x787a90 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation.c"; /* ROM 0x703c64 */
static const char page_event_fn[] = "navigation_page_event_handler"; /* ROM 0x762510 */
static const char ui_event_fn[] = "navigation_ui_event_handler"; /* ROM 0x76e6a8 */
static const char fg_id_fmt[] = "foregroundID = %d"; /* ROM 0x781304 */
static const char fg_id_fmt_short[] = "[navigation.main]foregroundID = %d"; /* ROM 0x756bb8 */
static const char opa_50_msg[] = "set navigation page root obj opacity to 50%%"; /* ROM 0x735804 */
static const char opa_50_msg_short[] = "[navigation.main]set navigation page root obj opacity to 50%%"; /* ROM 0x70cca4 */
static const char opa_100_msg[] = "set navigation page root obj opacity to 100%%"; /* ROM 0x735834 */
static const char opa_100_msg_short[] = "[navigation.main]set navigation page root obj opacity to 100%%"; /* ROM 0x70cce4 */
static const char stop_again_msg[] = " stop process break,RequestDisplayStop again"; /* ROM 0x735864 */
static const char stop_again_msg_short[] = "[navigation.main] stop process break,RequestDisplayStop again"; /* ROM 0x70cd24 */
static const char imu_reflash_msg[] = "IMU Reflash Event."; /* ROM 0x781318 */
static const char imu_reflash_msg_short[] = "[navigation.main]IMU Reflash Event."; /* ROM 0x756bdc */
static const char imu_compass_msg[] = "IMU compass Event."; /* ROM 0x78132c */
static const char imu_compass_msg_short[] = "[navigation.main]IMU compass Event."; /* ROM 0x756c00 */
static const char exit_notify_msg[] = "PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x74b52c */
static const char exit_notify_msg_short[] = "[navigation.main]PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x720478 */
static const char ui_init_msg[] = "navigation_ui_event_handler UI_EVENT_TYPE_INIT"; /* ROM 0x735894 */
static const char ui_init_msg_short[] = "[navigation.main]navigation_ui_event_handler UI_EVENT_TYPE_INIT"; /* ROM 0x70cd64 */
static const char ui_exit_msg[] = "navigation_ui_event_handler DISPLAY_EXIT"; /* ROM 0x740264 */
static const char ui_exit_msg_short[] = "[navigation.main]navigation_ui_event_handler DISPLAY_EXIT"; /* ROM 0x716510 */
static const char clock_12h_fmt[] = "%02d:%02d %s"; /* ROM 0x787aa0 */
static const char clock_24h_fmt[] = "%02d:%02d"; /* ROM 0x78b5d0 */
static const char am_text[] = "AM"; /* ROM 0x58638c */
static const char pm_text[] = "PM"; /* ROM 0x586390 */
static const g2_nav_session_report_t session_report_template = {4u, 0u}; /* ROM 0x78dd2c */

static void log_line(const char *fn, uint8_t level, uint32_t line, uint32_t code, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(code, msg_short, msg_short);
}

void *navigation_page_manager_get_585cba(void)
{
    return (void *)(uintptr_t)g2_navigation_var_20074720;
}

uint8_t navigation_foreground_layer_active_585cc2(void)
{
    return g2_navigation_flag_20074fe6;
}

/* Page-manager callback. Remembers the manager on first use, dims the page to
 * 50% while another app (other than the system alert 0x21) is in front and
 * restores it on leave; input / IMU events go to the navigation UI unless the
 * device role is 2. Always returns 1. */
uint32_t navigation_page_event_handler_585ce0(uint32_t unused, uint32_t manager, uint32_t event, const uint32_t *data)
{
    (void)unused;
    if (g2_navigation_var_20074720 == 0u && manager != 0u)
        g2_navigation_var_20074720 = manager;

    if (event == PAGE_EVENT_FOREGROUND_ENTER) {
        uint32_t foreground_id;
        g2_navigation_flag_20074fe6 = 1u;
        foreground_id = 0u;
        if (data != NULL)
            foreground_id = *data;
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, page_event_fn, 0x85u, fg_id_fmt, foreground_id);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x0c400000u, fg_id_fmt_short, fg_id_fmt_short, foreground_id);
        if (g2_navigation_page_root_20074718 != NULL && foreground_id != 0u && foreground_id != SYSTEM_ALERT_APP_ID) {
            log_line(page_event_fn, 4u, 0x88u, 0x10000000u, opa_50_msg, opa_50_msg_short);
            audio_uart_display_audio_reset_441488(g2_navigation_page_root_20074718, LV_OPA_50, 0u);
            g2_nav_opacity_lowered_20074724 = 1u;
        }
    } else if (event == PAGE_EVENT_FOREGROUND_LEAVE) {
        g2_navigation_flag_20074fe6 = 0u;
        if (g2_navigation_page_root_20074718 != NULL && g2_nav_opacity_lowered_20074724 == 1u) {
            log_line(page_event_fn, 4u, 0x92u, 0x10000000u, opa_100_msg, opa_100_msg_short);
            audio_uart_display_audio_reset_441488(g2_navigation_page_root_20074718, LV_OPA_COVER, 0u);
            g2_nav_opacity_lowered_20074724 = 0u;
        }
        if (g2_nav_fadeout_pending_2007472c == 1u && display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
            log_line(page_event_fn, 3u, 0x99u, 0x0c000000u, stop_again_msg, stop_again_msg_short);
            audio_system_alert_close_464c36(NAV_APP_ID, 0u, 0u, 0u);
        }
    } else if (event == PAGE_EVENT_INPUT_0A) {
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    } else if (event == PAGE_EVENT_INPUT_44) {
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    } else if (event == PAGE_EVENT_INPUT_45) {
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    } else if (event == PAGE_EVENT_INPUT_48) {
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    } else if (event == PAGE_EVENT_IMU_REFLASH) {
        log_line(page_event_fn, 4u, 0xbbu, 0x10000000u, imu_reflash_msg, imu_reflash_msg_short);
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    } else if (event == PAGE_EVENT_IMU_COMPASS) {
        log_line(page_event_fn, 4u, 0xc3u, 0x10000000u, imu_compass_msg, imu_compass_msg_short);
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    } else if (event == PAGE_EVENT_IMU_COMPASS_50) {
        /* Same "IMU compass Event." strings as 0x41, own line number. */
        log_line(page_event_fn, 4u, 0xcbu, 0x10000000u, imu_compass_msg, imu_compass_msg_short);
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    } else if (event == PAGE_EVENT_SYSTEM_EXIT_NOTIFY) {
        log_line(page_event_fn, 4u, 0xd3u, 0x10000000u, exit_notify_msg, exit_notify_msg_short);
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_SINGLE)
            (void)NavigationInputEventHandler_548f80(event, data);
    }
    return 1u;
}

static void nav_tick(void)
{
    /* Heartbeat to the peer: every 61 ticks count down; at 0 reload 20 and,
     * as master, refresh {0xf0, 0}. */
    g2_navigation_var_20074744++;
    if ((int32_t)g2_navigation_var_20074744 >= HEARTBEAT_TICKS) {
        g2_navigation_var_20074744 = 0u;
        g2_nav_var_20002cfc--;
        if ((int32_t)g2_nav_var_20002cfc < 1) {
            g2_nav_var_20002cfc = HEARTBEAT_RELOAD;
            if ((uint8_t)audio_uart_service_mode() == DEVICE_ROLE_MASTER) {
                uint8_t heartbeat[2];
                heartbeat[0] = 0xf0u;
                heartbeat[1] = 0u;
                audio_uart_master_display_refresh(NAV_APP_ID, heartbeat, 2u, 0u);
            }
        }
    }

    /* Exit page countdown: 240 ticks, then {0xf3, 0, 0, 0, 0, 0}. */
    if (g2_nav_var_2007474c == 1u) {
        g2_nav_var_20074748--;
        if ((int32_t)g2_nav_var_20074748 < 1) {
            g2_nav_var_20074748 = EXIT_COUNTDOWN_RELOAD;
            if ((uint8_t)audio_uart_service_mode() == DEVICE_ROLE_MASTER) {
                uint8_t exit_msg[10];
                aeabi_memset_43c0e4(exit_msg, sizeof exit_msg, 0u);
                exit_msg[0] = 0xf3u;
                exit_msg[1] = 0u;
                audio_uart_master_display_refresh(NAV_APP_ID, exit_msg, 6u, 0u);
            }
        }
    }

    /* Clock labels: re-render when hour or minute changed. */
    if (g2_nav_b_clock_label_20074764 != NULL || g2_nav_a_clock_label_200747e0 != NULL) {
        g2_calendar_t now;
        service_time_epoch_to_calendar(service_time_current_epoch_get(), &now);
        if (g2_navigation_clock_hour_2007475c != now.hour || g2_navigation_clock_minute_20074760 != now.minute) {
            char text[10];
            aeabi_memset_43c0e4(text, sizeof text, 0u);
            g2_navigation_clock_hour_2007475c = now.hour;
            g2_navigation_clock_minute_20074760 = now.minute;
            if (audio_time_format_mode_46650c() == 1u) {
                uint32_t hour12 = now.hour % 12u;
                if (hour12 == 0u)
                    hour12 = 12u;
                (void)audio_ble_format_to_buffer(text, clock_12h_fmt, hour12, now.minute,
                                                 now.hour < 12u ? am_text : pm_text);
            } else {
                (void)audio_ble_format_to_buffer(text, clock_24h_fmt, now.hour, now.minute);
            }
            if (audio_terminal_ui_object_valid_43e2ea(g2_nav_b_clock_label_20074764) != 0u)
                audio_lv_label_text_49942e(g2_nav_b_clock_label_20074764, text);
            if (audio_terminal_ui_object_valid_43e2ea(g2_nav_a_clock_label_200747e0) != 0u)
                audio_lv_label_text_49942e(g2_nav_a_clock_label_200747e0, text);
        }
    }

    /* Compass-calibration animation (UI state 10 or 1): step it and, as
     * master, mirror every 4th frame as {0xf6, frame, 0, 0, 0, 0}. */
    if ((g2_navigation_ui_state_20074fed == 10u || g2_navigation_ui_state_20074fed == 1u) &&
        g2_nav_calibrate_anim_20074750 != NULL &&
        audio_terminal_ui_object_valid_43e2ea(g2_nav_calibrate_anim_20074750->image) != 0u) {
        generic_animation_update_463f34(g2_nav_calibrate_anim_20074750);
        if (audio_uart_service_mode() == DEVICE_ROLE_MASTER) {
            int32_t frame = (int32_t)generic_animation_get_frame_463fa4(g2_nav_calibrate_anim_20074750);
            if (frame >= 1 && ((uint32_t)(frame + 1) & 3u) == 0u) {
                uint8_t frame_msg[10];
                aeabi_memset_43c0e4(frame_msg, sizeof frame_msg, 0u);
                frame_msg[0] = 0xf6u;
                frame_msg[1] = (uint8_t)frame;
                frame_msg[2] = 0u;
                frame_msg[3] = 0u;
                frame_msg[4] = 0u;
                frame_msg[5] = 0u;
                audio_uart_master_display_refresh(NAV_APP_ID, frame_msg, 6u, 0u);
            }
        }
    }
}

int32_t audio_uart_registry_callback_58607a(int32_t event, const uint8_t *payload, uint32_t length, void *context)
{
    if (event == UI_EVENT_TYPE_INIT) {
        log_line(ui_event_fn, 4u, 0xe5u, 0x10000000u, ui_init_msg, ui_init_msg_short);
        g2_nav_start_tick_20074728 = osKernelGetTickCount();
        g2_nav_opacity_lowered_20074724 = 0u;
        g2_nav_fadeout_pending_2007472c = 0u;
        ble_state_skip_manual_start(0u);
        g2_nav_ui_context_20074730 = context;
        (void)navigation_ui_startup_page_create_545d18(context, payload, (uint16_t)length);
        *(void **)(void *)(&audio_uart_registry_context_20002ce0 + 4) = g2_navigation_page_root_20074718;
        page_fade_in_anim_start_46410a(g2_navigation_page_root_20074718);
        return 0;
    }
    if (event == UI_EVENT_TYPE_REFRESH) {
        (void)navigation_ui_reflash_page_handler_549c24(payload, (uint16_t)length);
        return 0;
    }
    if (event == UI_EVENT_TYPE_TICK) {
        nav_tick();
        return 0;
    }
    if (event == UI_EVENT_DISPLAY_EXIT) {
        g2_nav_session_report_t report;
        uint32_t elapsed;
        log_line(ui_event_fn, 3u, 0x14au, 0x0c000000u, ui_exit_msg, ui_exit_msg_short);
        if (g2_nav_calibrate_anim_20074750 != NULL) {
            generic_animation_destroy_463e1c(g2_nav_calibrate_anim_20074750, 1u);
            g2_nav_calibrate_anim_20074750 = NULL;
        }
        /* Stock passes (payload, length) in r0/r1; the callee ignores them. */
        (void)navigation_ui_exit_page_handler_54c268();
        audio_ble_param_reset_delayed_event(10000u);
        (void)StopIMUCompassFunc_54566c();
        g2_nav_opacity_lowered_20074724 = 0u;
        g2_nav_fadeout_pending_2007472c = 0u;
        /* Session length in seconds: ticks * 1000 / tick rate (1000 Hz). */
        elapsed = osKernelGetTickCount() - g2_nav_start_tick_20074728;
        {
            uint64_t scaled = (uint64_t)elapsed * 1000u;
            report = session_report_template;
            report.seconds = (uint32_t)audio_uart_ring_u64_div_47cc60((uint32_t)scaled, (uint32_t)(scaled >> 32), 1000u, 0u);
        }
        audio_uart_ring_wear_persist_48eb32(NAV_SESSION_EVENT_ID, 2u, &report);
        return 0;
    }
    return event;
}
