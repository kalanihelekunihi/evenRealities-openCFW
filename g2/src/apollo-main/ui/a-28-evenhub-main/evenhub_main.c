/* EvenHub application main (page state, page input events, UI event handler), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_main.c (log tag "evenhub.main").
 * Native 0x4e0ca0..0x4e1441 and 0x4e1490..0x4e1955; literal pools 0x4e1444..0x4e148f and
 * 0x4e1958..0x4e1a47. evenhub_common_data_handler 0x4e1192 (float logging) is in
 * evenhub_main_fp.c.
 *
 * The EvenHub app is UI registry slot 7 (app id 0xe0, ROM 0x6a4520). Its page manager
 * (0x38 bytes, file heap) is created on DISPLAY_STARTUP and destroyed on DISPLAY_EXIT.
 * DISPLAY_AUTO_REFLASH ticks two counters while the page is in the foreground: 900 ticks
 * without a phone heartbeat report a heartbeat timeout, and 240 ticks on the timeout page
 * exit the app. Exit reasons are persisted as record key 0x40102 {widget, reason} and the
 * session length as key 0x40103 {widget, ms}. */
#include <stdint.h>
#include <stddef.h>

enum {
    UI_EVENT_DISPLAY_STARTUP = 2u,
    UI_EVENT_DISPLAY_REFLASH = 3u,
    UI_EVENT_DISPLAY_AUTO_REFLASH = 4u,
    UI_EVENT_DISPLAY_EXIT = 5u,
};

enum {
    PAGE_EVENT_CLICK = 0x0au,
    PAGE_EVENT_FOREGROUND_LOST = 0x42u, /* another app (foregroundID) covers the page */
    PAGE_EVENT_FOREGROUND = 0x43u,
    PAGE_EVENT_SCROLL_UP = 0x44u,
    PAGE_EVENT_SCROLL_DOWN = 0x45u,
    PAGE_EVENT_DOUBLE_CLICK = 0x48u,
    PAGE_EVENT_SYSTEM_EXIT_NOTIFY = 0x4fu,
};

#define EVENHUB_APP_ID 0xe0u
#define EVENHUB_RECORD_EXIT_REASON 0x40102u
#define EVENHUB_RECORD_SESSION_TIME 0x40103u
#define EVENHUB_HEARTBEAT_TICKS 900u
#define EVENHUB_TIMEOUT_PAGE_TICKS 240u
#define EVENHUB_MANAGER_SIZE 0x38u
#define AUDM_APP_EVENHUB 5u

/* Page manager (see ui/a-14-evenhub-ui/evenhub_ui_private.h, evenhub_manager_t). */
typedef struct {
    void *parent;           /* +0x00 page root object */
    void *head;             /* +0x04 container list */
    uint8_t reserved_08[0x2c];
    uint8_t bound;          /* +0x34 an event-capturing container is bound */
    uint8_t reserved_35[3];
} evenhub_main_manager_t;
_Static_assert(sizeof(evenhub_main_manager_t) == EVENHUB_MANAGER_SIZE, "evenhub manager");

/* lv_event_t: +0x10 points at the event parameter. */
typedef struct {
    uint32_t value;               /* +0x00 foregroundID for PAGE_EVENT_FOREGROUND_LOST */
    uint8_t reserved_04[0x0c];
    const uint16_t *param;        /* +0x10 input device type / list index */
} evenhub_page_event_t;

typedef struct {
    uint32_t widget; /* +0 startup widget id */
    uint32_t value;  /* +4 exit reason or session milliseconds */
} evenhub_record_t;

extern evenhub_main_manager_t *g2_evenhub_manager; /* RAM 0x200745a8 */
extern uint32_t g2_evenhub_heartbeat_ticks;        /* RAM 0x200745ac, cleared on phone heartbeat */
extern uint32_t g2_evenhub_timeout_page_ticks;     /* RAM 0x200745b0 */
extern uint32_t g2_evenhub_audio_acquired;         /* RAM 0x200745b4 */
extern uint32_t g2_evenhub_shutdown_state;         /* RAM 0x200745b8 */
extern uint32_t g2_evenhub_imu_enabled;            /* RAM 0x200745bc */
extern uint32_t g2_evenhub_dimmed;                 /* RAM 0x200745c0, root at 50% opacity */
extern uint32_t g2_evenhub_exit_pending;           /* RAM 0x200745c4 */
extern uint32_t g2_evenhub_start_tick;             /* RAM 0x200745c8 */
extern uint8_t g2_evenhub_foreground;              /* RAM 0x20074fc3 */
extern uint8_t g2_evenhub_timeout_page;            /* RAM 0x20074fc4 */
extern uint8_t audio_uart_registry_context_20000b38; /* RAM 0x20000b38, +4 page object */

extern uint32_t osKernelGetTickCount(void);                                 /* 0x4490cc */
extern uint32_t ulSetInterruptMask(void);                                   /* 0x5fa0a4 */
extern void *file_heap_allocate(uint32_t size);                             /* 0x474cd2 */
extern void file_heap_free(void *buffer);                                   /* 0x474d16 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern uint8_t audio_uart_device_role_get(void);                            /* 0x45a568 */
extern uint32_t audio_uart_service_mode(void);                              /* 0x45a570 */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* style opa */
extern void page_fade_in_anim_start_46410a(void *object);
extern void Common_Fadeout_Anim_Start_4641b6(void *object, uint32_t app);
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload,
                                            uint32_t length, uint32_t flags);
extern int32_t audio_settings_send_peer_packet(uint16_t app, const void *data, uint32_t len,
                                               uint32_t id, uint32_t event); /* 0x465480 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern uint32_t audio_even_ai_app_acquire_54f380(uint32_t app);        /* AUDM_appAcquire */
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t app); /* AUDM_appRelease */

/* evenhub_ui.c / evenhub_data_parser.c. */
extern uint32_t evenhub_main_widget_id_4935fe(void);
extern void evenhub_container_list_destroy_493d02(void *mgr);
extern void *evenhub_container_list_find_by_id_493fa8(void *mgr, uint32_t id);
extern int32_t evenhub_inject_event_to_container_494610(void *mgr, int32_t event_code, void *data);
extern void *evenhub_ui_create_root_container_494834(void *parent);
extern int32_t evenhub_ui_page_create_494bec(const void *data, int16_t len, void *mgr);
extern int32_t evenhub_ui_reflash_event_handler_496544(void *mgr, const void *data, int16_t len);
extern void evenhub_data_mutex_init_4d9b34(void);
extern int32_t evenhub_send_system_event_4d9d9a(uint8_t event, uint32_t value);
extern int32_t evenhub_send_system_exit_event_4da078(uint32_t value);
extern int32_t evenhub_send_container_event_4da16a(uint8_t type, uint32_t id, const char *name,
                                                   uint8_t sub, int32_t index, int16_t extra);
extern int32_t common_imu_setting_4da720(uint32_t enable, int32_t report_freq);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char eh_tag[] = "evenhub.main"; /* ROM 0x785e70 */
static const char eh_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_main.c"; /* ROM 0x702988 */

static const char fn_find[] = "evenhub_container_find_node_by_id"; /* ROM 0x75462c */
static const char fd_null[] = "evenhub_container_find_node_by_id: manager_ctx is NULL or container_list_head is NULL or evenhub_page_root_obj is NULL"; /* ROM 0x6d6128 */
static const char fd_null_s[] = "[evenhub.main]evenhub_container_find_node_by_id: manager_ctx is NULL or container_list_head is NULL or evenhub_page_root_obj is NULL"; /* ROM 0x6d47f0 */

static const char fn_page[] = "evenhub_page_event_handler"; /* ROM 0x76b82c */
static const char pg_fg[] = "foregroundID = %d"; /* ROM 0x77f400 */
static const char pg_fg_s[] = "[evenhub.main]foregroundID = %d"; /* ROM 0x75ff70 */
static const char pg_dim[] = "set navigation page root obj opacity to 50%%"; /* ROM 0x734034 */
static const char pg_dim_s[] = "[evenhub.main]set navigation page root obj opacity to 50%%"; /* ROM 0x714fbc */
static const char pg_full[] = "set evenhub page root obj opacity to 100%%"; /* ROM 0x73ed14 */
static const char pg_full_s[] = "[evenhub.main]set evenhub page root obj opacity to 100%%"; /* ROM 0x714ff8 */
static const char pg_stop[] = " stop process break,RequestDisplayStop again"; /* ROM 0x734064 */
static const char pg_stop_s[] = "[evenhub.main] stop process break,RequestDisplayStop again"; /* ROM 0x715034 */
static const char pg_dbl[] = "evenhub_page_event_handler PAGE_EVENT_DOUBLE_CLICK Event."; /* ROM 0x715070 */
static const char pg_dbl_s[] = "[evenhub.main]evenhub_page_event_handler PAGE_EVENT_DOUBLE_CLICK Event."; /* ROM 0x6fa40c */
static const char pg_dev[] = "Input_Device_Type = %d"; /* ROM 0x7775dc */
static const char pg_dev_s[] = "[evenhub.main]Input_Device_Type = %d"; /* ROM 0x749fc4 */
static const char pg_exit[] = "PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x749fec */
static const char pg_exit_s[] = "[evenhub.main]PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x7296f8 */
static const char pg_shut[] = "evenhub_page_event_handler send shutdown packet to UI"; /* ROM 0x71ee60 */
static const char pg_shut_s[] = "[evenhub.main]evenhub_page_event_handler send shutdown packet to UI"; /* ROM 0x7029cc */

static const char fn_ui[] = "evenhub_ui_event_handler"; /* ROM 0x76b864 */
static const char ui_root[] = "evenhub_ui_page_create create root container failed"; /* ROM 0x72972c */
static const char ui_root_s[] = "[evenhub.main]evenhub_ui_page_create create root container failed"; /* ROM 0x702a10 */
static const char ui_create[] = "evenhub_ui_event_handler DISPLAY_STARTUP evenhub_ui_page_create failed"; /* ROM 0x6fa454 */
static const char ui_create_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_STARTUP evenhub_ui_page_create failed"; /* ROM 0x6e3408 */
static const char ui_master[] = "evenhub_ui_event_handler DISPLAY_STARTUP current role is MASTER_ROLE, request display stop"; /* ROM 0x6e03a8 */
static const char ui_master_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_STARTUP current role is MASTER_ROLE, request display stop"; /* ROM 0x6ca83c */
static const char ui_slave[] = "evenhub_ui_event_handler DISPLAY_STARTUP current role is SLAVE_ROLE, send abnormal exit event to master"; /* ROM 0x6d8a04 */
static const char ui_slave_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_STARTUP current role is SLAVE_ROLE, send abnormal exit event to master"; /* ROM 0x6d61a0 */
static const char ui_hb[] = "evenhub_ui_event_handler DISPLAY_AUTO_REFLASH heartbeat timeout"; /* ROM 0x70b6e4 */
static const char ui_hb_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_AUTO_REFLASH heartbeat timeout"; /* ROM 0x6ed1f8 */
static const char ui_to[] = "evenhub_ui_event_handler DISPLAY_AUTO_REFLASH timeout exit.exit app."; /* ROM 0x6fa49c */
static const char ui_to_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_AUTO_REFLASH timeout exit.exit app."; /* ROM 0x6e7cc0 */
static const char ui_exit[] = "evenhub_ui_event_handler DISPLAY_EXIT"; /* ROM 0x74a03c */
static const char ui_exit_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_EXIT"; /* ROM 0x729760 */
static const char ui_imu[] = "evenhub_ui_event_handler DISPLAY_EXIT close IMU"; /* ROM 0x734094 */
static const char ui_imu_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_EXIT close IMU"; /* ROM 0x70b724 */
static const char ui_clean[] = "evenhub_ui_event_handler DISPLAY_EXIT: resources cleaned"; /* ROM 0x7150e8 */
static const char ui_clean_s[] = "[evenhub.main]evenhub_ui_event_handler DISPLAY_EXIT: resources cleaned"; /* ROM 0x6fa4e4 */

#define EH_LOG(level, func, line, cflags, text, short_text, ...)                                 \
    do {                                                                                         \
        if ((audio_log_flags() & 2u) != 0u)                                                      \
            audio_log_extended((level), eh_tag, eh_file, (func), (line), (text), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                    \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);      \
    } while (0)

/* configASSERT-style trap. */
#define EH_ASSERT(cond)                                         \
    do {                                                        \
        if (!(cond)) {                                          \
            (void)ulSetInterruptMask();                         \
            *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;   \
            for (;;) {                                          \
            }                                                   \
        }                                                       \
    } while (0)

void evenhub_main_exit_pending_set_4e0ca0(void)
{
    g2_evenhub_exit_pending = 1u;
}

/* 0x4e0caa..0x4e0ccd: four accessors with no inventory row (callers in evenhub_ui.c). */
uint32_t evenhub_main_shutdown_state_get_4e0caa(void)
{
    return g2_evenhub_shutdown_state;
}

void evenhub_main_shutdown_state_set_4e0cb2(uint32_t v)
{
    g2_evenhub_shutdown_state = v;
}

void evenhub_main_audio_ack_clear_4e0cba(void)
{
    g2_evenhub_heartbeat_ticks = 0u;
}

void evenhub_main_timeout_page_set_4e0cc4(void)
{
    g2_evenhub_timeout_page = 1u;
}

/* evenhub_container_find_node_by_id */
void *evenhub_container_find_node_by_id_4e0cce(uint32_t id)
{
    if (g2_evenhub_manager == NULL || g2_evenhub_manager->head == NULL ||
        g2_evenhub_manager->parent == NULL) {
        EH_LOG(1u, fn_find, 0x65u, 0x04000000u, fd_null, fd_null_s);
        return NULL;
    }
    return evenhub_container_list_find_by_id_493fa8(g2_evenhub_manager, id);
}

/* evenhub_page_event_handler: page-level input and focus events; always consumed. */
uint32_t evenhub_page_event_handler_4e0d3a(void *obj, void *user, uint32_t code,
                                           evenhub_page_event_t *event)
{
    (void)obj;
    (void)user;

    if (code == PAGE_EVENT_FOREGROUND_LOST) {
        uint32_t foreground_id = 0u;
        if (event != NULL)
            foreground_id = event->value;
        EH_LOG(3u, fn_page, 0x76u, 0x0c400000u, pg_fg, pg_fg_s, foreground_id);
        if (g2_evenhub_manager != NULL && g2_evenhub_manager->parent != NULL &&
            foreground_id != 0u && foreground_id != 0x21u) {
            EH_LOG(4u, fn_page, 0x79u, 0x10000000u, pg_dim, pg_dim_s);
            g2_evenhub_dimmed = 1u;
            audio_uart_display_audio_reset_441488(g2_evenhub_manager->parent, 0x7fu, 0u);
        }
        (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 4u, 0, 0);
        g2_evenhub_foreground = 0u;
        return 1u;
    }
    if (code == PAGE_EVENT_FOREGROUND) {
        (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 5u, 0, 0);
        if (g2_evenhub_manager != NULL && g2_evenhub_manager->parent != NULL) {
            EH_LOG(4u, fn_page, 0x84u, 0x10000000u, pg_full, pg_full_s);
            if (g2_evenhub_dimmed == 1u) {
                g2_evenhub_dimmed = 0u;
                audio_uart_display_audio_reset_441488(g2_evenhub_manager->parent, 0xffu, 0u);
            }
        }
        g2_evenhub_foreground = 1u;
        if (g2_evenhub_exit_pending == 1u && audio_uart_device_role_get() == 1u) {
            g2_evenhub_exit_pending = 0u;
            EH_LOG(3u, fn_page, 0x8eu, 0x0c000000u, pg_stop, pg_stop_s);
            audio_system_alert_close_464c36(EVENHUB_APP_ID, 0u, 0u, 0u);
        }
        return 1u;
    }
    if (code == PAGE_EVENT_CLICK) {
        if (g2_evenhub_manager != NULL && g2_evenhub_manager->parent != NULL &&
            g2_evenhub_manager->bound == 1u &&
            evenhub_inject_event_to_container_494610(g2_evenhub_manager, (int32_t)code, event) == 1) {
            uint16_t index = 0u;
            if (event != NULL && event->param != NULL)
                index = *event->param;
            (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 0u, 0, (int16_t)index);
        }
        return 1u;
    }
    if (code == PAGE_EVENT_SCROLL_UP) {
        if (g2_evenhub_manager != NULL && g2_evenhub_manager->parent != NULL &&
            g2_evenhub_manager->bound == 1u &&
            evenhub_inject_event_to_container_494610(g2_evenhub_manager, (int32_t)code, event) == 1)
            (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 1u, 0, 0);
        return 1u;
    }
    if (code == PAGE_EVENT_SCROLL_DOWN) {
        if (g2_evenhub_manager != NULL && g2_evenhub_manager->parent != NULL &&
            g2_evenhub_manager->bound == 1u &&
            evenhub_inject_event_to_container_494610(g2_evenhub_manager, (int32_t)code, event) == 1)
            (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 2u, 0, 0);
        return 1u;
    }
    if (code == PAGE_EVENT_DOUBLE_CLICK) {
        if (g2_evenhub_manager != NULL && g2_evenhub_manager->parent != NULL) {
            EH_LOG(4u, fn_page, 0xb7u, 0x10000000u, pg_dbl, pg_dbl_s);
            uint16_t device = 0u;
            if (event != NULL && event->param != NULL)
                device = *event->param;
            EH_LOG(3u, fn_page, 0xbfu, 0x0c400000u, pg_dev, pg_dev_s, device);
            (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 3u, 0, (int16_t)device);
        }
        return 1u;
    }
    if (code == PAGE_EVENT_SYSTEM_EXIT_NOTIFY) {
        EH_LOG(4u, fn_page, 0xc4u, 0x10000000u, pg_exit, pg_exit_s);
        if (g2_evenhub_manager != NULL && g2_evenhub_manager->parent != NULL) {
            Common_Fadeout_Anim_Start_4641b6(g2_evenhub_manager->parent, EVENHUB_APP_ID);
            evenhub_record_t record = {0u, 1u}; /* initializer at ROM 0x78d5ac */
            record.widget = evenhub_main_widget_id_4935fe();
            audio_uart_ring_wear_persist_48eb32(EVENHUB_RECORD_EXIT_REASON, 2u, &record);
            evenhub_main_exit_pending_set_4e0ca0();
            EH_LOG(4u, fn_page, 0xcbu, 0x10000000u, pg_shut, pg_shut_s);
        }
        return 1u;
    }
    return 1u;
}

/* Audio-manager hold for the EvenHub app (AUDM app 5); returns the held flag. */
uint32_t evenhub_audio_acquire_set_4e1406(uint32_t on)
{
    if (on == 1u && g2_evenhub_audio_acquired == 0u) {
        g2_evenhub_audio_acquired = 1u;
        (void)audio_even_ai_app_acquire_54f380(AUDM_APP_EVENHUB);
    } else if (on == 0u && g2_evenhub_audio_acquired == 1u) {
        g2_evenhub_audio_acquired = 0u;
        (void)audio_terminal_reset_mode_notice_54f50e(AUDM_APP_EVENHUB);
    }
    return g2_evenhub_audio_acquired;
}

/* evenhub_ui_event_handler: UI registry slot 7 (ROM 0x6a4520). */
uint32_t audio_uart_registry_callback_4e1490(uint32_t event, const void *data, uint32_t len,
                                             void *parent)
{
    if (event == UI_EVENT_DISPLAY_STARTUP) {
        int32_t failed;

        g2_evenhub_start_tick = osKernelGetTickCount();
        g2_evenhub_audio_acquired = 0u;
        g2_evenhub_imu_enabled = 0u;
        g2_evenhub_shutdown_state = 0u;
        g2_evenhub_dimmed = 0u;
        g2_evenhub_exit_pending = 0u;
        evenhub_data_mutex_init_4d9b34();
        g2_evenhub_manager = (evenhub_main_manager_t *)file_heap_allocate(EVENHUB_MANAGER_SIZE);
        EH_ASSERT(g2_evenhub_manager != NULL);
        audio_uart_buffer_zero(g2_evenhub_manager, EVENHUB_MANAGER_SIZE, 0u);
        g2_evenhub_manager->parent = evenhub_ui_create_root_container_494834(parent);
        if (g2_evenhub_manager->parent == NULL) {
            EH_LOG(1u, fn_ui, 0x11du, 0x04000000u, ui_root, ui_root_s);
            EH_ASSERT(0);
        }
        failed = evenhub_ui_page_create_494bec(data, (int16_t)len, g2_evenhub_manager);
        if (failed != 0) {
            EH_LOG(1u, fn_ui, 0x124u, 0x04000000u, ui_create, ui_create_s);
            if (audio_uart_service_mode() == 1u) {
                EH_LOG(1u, fn_ui, 0x126u, 0x04000000u, ui_master, ui_master_s);
                (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 6u, 0, 0);
                audio_system_alert_close_464c36(EVENHUB_APP_ID, 0u, 0u, 0u);
            } else {
                uint8_t abnormal[5];
                EH_LOG(1u, fn_ui, 0x12bu, 0x04000000u, ui_slave, ui_slave_s);
                audio_uart_buffer_zero(abnormal, 5u, 0u);
                abnormal[0] = 0u;
                (void)audio_settings_send_peer_packet(EVENHUB_APP_ID, abnormal, 1u, 0u, 5u);
            }
        }
        *(void **)(void *)(&audio_uart_registry_context_20000b38 + 4) = g2_evenhub_manager->parent;
        if (failed == 0)
            page_fade_in_anim_start_46410a(g2_evenhub_manager->parent);
        g2_evenhub_foreground = 1u;
        g2_evenhub_heartbeat_ticks = 0u;
        g2_evenhub_timeout_page_ticks = 0u;
        g2_evenhub_timeout_page = 0u;
    } else if (event == UI_EVENT_DISPLAY_REFLASH) {
        (void)evenhub_ui_reflash_event_handler_496544(g2_evenhub_manager, data, (int16_t)len);
    } else if (event == UI_EVENT_DISPLAY_AUTO_REFLASH) {
        if (g2_evenhub_foreground == 1u &&
            ++g2_evenhub_heartbeat_ticks >= EVENHUB_HEARTBEAT_TICKS) {
            g2_evenhub_heartbeat_ticks = 0u;
            EH_LOG(3u, fn_ui, 0x144u, 0x0c000000u, ui_hb, ui_hb_s);
            if (audio_uart_service_mode() == 1u)
                (void)evenhub_send_system_event_4d9d9a(0u, 0u);
        }
        if (g2_evenhub_timeout_page == 1u && g2_evenhub_foreground == 1u &&
            ++g2_evenhub_timeout_page_ticks >= EVENHUB_TIMEOUT_PAGE_TICKS) {
            g2_evenhub_timeout_page_ticks = 0u;
            EH_LOG(3u, fn_ui, 0x14fu, 0x0c000000u, ui_to, ui_to_s);
            if (audio_uart_service_mode() == 1u) {
                (void)evenhub_send_system_event_4d9d9a(1u, 0u);
                evenhub_record_t record = {0u, 3u}; /* initializer at ROM 0x78d5b4 */
                record.widget = evenhub_main_widget_id_4935fe();
                audio_uart_ring_wear_persist_48eb32(EVENHUB_RECORD_EXIT_REASON, 2u, &record);
            }
        }
    } else if (event == UI_EVENT_DISPLAY_EXIT) {
        EH_LOG(3u, fn_ui, 0x159u, 0x0c000000u, ui_exit, ui_exit_s);
        if (g2_evenhub_audio_acquired == 1u)
            (void)evenhub_audio_acquire_set_4e1406(0u);
        if (g2_evenhub_imu_enabled == 1u) {
            EH_LOG(4u, fn_ui, 0x15fu, 0x10000000u, ui_imu, ui_imu_s);
            g2_evenhub_imu_enabled = 0u;
            (void)common_imu_setting_4da720(0u, 0);
        }
        if (evenhub_main_shutdown_state_get_4e0caa() == 1u)
            (void)evenhub_send_system_exit_event_4da078(1u);
        else
            (void)evenhub_send_system_exit_event_4da078(0u);
        if (g2_evenhub_manager != NULL) {
            evenhub_container_list_destroy_493d02(g2_evenhub_manager);
            file_heap_free(g2_evenhub_manager);
            g2_evenhub_manager = NULL;
            EH_LOG(4u, fn_ui, 0x16eu, 0x10000000u, ui_clean, ui_clean_s);
        }
        g2_evenhub_foreground = 0u;
        g2_evenhub_heartbeat_ticks = 0u;
        g2_evenhub_timeout_page_ticks = 0u;
        g2_evenhub_timeout_page = 0u;
        g2_evenhub_exit_pending = 0u;
        g2_evenhub_audio_acquired = 0u;
        g2_evenhub_imu_enabled = 0u;
        g2_evenhub_shutdown_state = 0u;
        g2_evenhub_dimmed = 0u;
        /* Tick-to-ms conversion (1000 Hz tick, 64-bit intermediate). */
        uint32_t rate = 1000u;
        uint32_t ticks = osKernelGetTickCount() - g2_evenhub_start_tick;
        if (rate == 0u)
            rate = 1000u;
        uint32_t elapsed_ms = (uint32_t)(((uint64_t)ticks * 1000u) / rate);
        evenhub_record_t session;
        session.widget = evenhub_main_widget_id_4935fe();
        session.value = elapsed_ms;
        audio_uart_ring_wear_persist_48eb32(EVENHUB_RECORD_SESSION_TIME, 2u, &session);
    }
    return 0u;
}
