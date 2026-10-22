/* Teleprompt application controller, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt.c
 * (path ROM 0x70665c, module tag "teleprompt" ROM 0x78c4d0).
 * Native 0x5899a4..0x58a30b; literal pool 0x58a30c..0x58a3fb.
 *
 * Registry entry 31 (ROM 0x6a46a0, app 6) points its data callback at
 * Teleprompt_common_data_handler (0x589fe6) and its UI callback at
 * Teleprompt_ui_event_handler (0x58a130); both run under the "teleprompt
 * action" mutex (RAM 0x20074a68, created with the priority-inherit attributes
 * at ROM 0x7896e0). Received frames are decoded by pb_service_teleprompt.c,
 * dispatched by command_id to the teleprompt FSM (teleprompt_fsm.c,
 * teleprompt_machine_handler 0x58c89e) and answered with a common response
 * (status 0 ok / 1 error; duplicates are acknowledged as ok). The UI is
 * driven through 8-byte {event, value} display requests to app 6
 * (teleprompt_request_display). While the page is in front, a 20 s phone
 * heartbeat watchdog closes it. */
#include <stdint.h>
#include <stddef.h>

#define WAIT_FOREVER 0xffffffffu

#define TP_APP_ID                 6u
#define TP_HEARTBEAT_TIMEOUT_MS   20000u
#define TP_EXIT_RECORD_KEY        0x40102u
#define TP_DURATION_RECORD_KEY    0x40103u
#define TP_RX_MSG_SIZE            0xf58u
#define TP_RX_DUPLICATE           0x0du
#define TP_UI_STATE_3             3u

/* teleprompt_request_display events (UI FSM events, see teleprompt_ui.c). */
enum {
    TP_REQ_EXIT = 0x09u,
    TP_REQ_ELAPSED = 0x12u,
};

/* UI events of the registry UI callback. */
enum {
    TP_UI_EVT_STARTUP = 2u,
    TP_UI_EVT_REQUEST = 3u,
    TP_UI_EVT_TICK = 4u,
    TP_UI_EVT_EXIT = 5u,
};

/* Input codes of the page event handler. */
enum {
    TP_INPUT_CLICK = 0x0au,
    TP_INPUT_FOREGROUND_COVERED = 0x42u,
    TP_INPUT_FOREGROUND_RESTORED = 0x43u,
    TP_INPUT_SCROLL_UP = 0x44u,
    TP_INPUT_SCROLL_DOWN = 0x45u,
    TP_INPUT_CLOSE = 0x48u,
    TP_INPUT_SCROLL_STOP = 0x4au,
    TP_INPUT_SYSTEM_EXIT = 0x4fu,
};

/* Teleprompt FSM control block (RAM 0x20109390, cleared as 0x44 bytes on exit). */
typedef struct {
    uint8_t state;              /* +0x00 0 idle, 1 running (app connected) */
    uint8_t reserved_01[0x3b];
    uint8_t page_covered;       /* +0x3c another page is in front, heartbeat paused */
    uint8_t reserved_3d[7];
} g2_teleprompt_fsm_ctrl_t;
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, page_covered) == 0x3c, "covered at +0x3c");
_Static_assert(sizeof(g2_teleprompt_fsm_ctrl_t) == 0x44, "stock memset size");

/* Display request to app 6 (8 bytes). */
typedef struct {
    uint8_t event;
    uint8_t reserved_01[3];
    uint32_t value;
} g2_teleprompt_request_t;
_Static_assert(sizeof(g2_teleprompt_request_t) == 8u, "stock record is 8 bytes");

/* Usage record {app, value}. */
typedef struct {
    uint32_t app;
    uint32_t value;
} g2_teleprompt_usage_record_t;

/* Registry context of entry 31 (RAM 0x20003da4). */
typedef struct {
    uint32_t reserved_00;
    void *root;                 /* +0x04 page root after startup */
} g2_teleprompt_registry_ctx_t;

extern void *g2_teleprompt_action_mutex_20074a68;               /* RAM 0x20074a68 */
extern uint32_t g2_teleprompt_heartbeat_tick_20074a64;          /* RAM 0x20074a64 */
extern uint32_t g2_teleprompt_start_tick_20074a60;              /* RAM 0x20074a60 */
extern void *g2_teleprompt_root_20074a7c;                       /* RAM 0x20074a7c */
extern uint8_t g2_teleprompt_rx_result_2010938c;                /* RAM 0x2010938c */
extern uint8_t g2_teleprompt_pb_rx_msg_20060154[TP_RX_MSG_SIZE]; /* RAM 0x20060154 */
extern g2_teleprompt_fsm_ctrl_t g2_teleprompt_fsm_ctrl;         /* RAM 0x20109390 */
extern g2_teleprompt_registry_ctx_t audio_uart_registry_context_20003da4; /* RAM 0x20003da4 */
extern const uint8_t g2_teleprompt_action_mutex_attr_7896e0[];  /* ROM 0x7896e0 osMutexAttr_t */

extern uint32_t audio_log_flags(void);                                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);      /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *osMutexNew(const void *attr);                                      /* 0x44971c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                     /* 0x44981c */
extern uint32_t osKernelGetTickCount(void);                                     /* 0x4490cc */
extern uint8_t audio_uart_device_role_get(void);                                /* 0x45a568, 1 = master */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags);              /* 0x464bb2 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* style opa */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t low, uint32_t high, uint32_t div_low,
                                               uint32_t div_high);              /* __aeabi_uldivmod */
extern void ble_state_skip_manual_start(uint8_t value);                         /* 0x478110 */
extern void audio_ble_param_reset_delayed_event(uint32_t delay);                /* ble_param_reset_delayed_event 0x478252 */
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t app);          /* AUDM_appRelease */
extern void teleprompt_file_list_reset(void);                                   /* 0x58bd74 */
extern void teleprompt_page_data_deinit(void);                                  /* 0x58b370 */
extern uint8_t teleprompt_ui_state_get_5540b2(void);
extern const char *teleprompt_ui_event_name_5540d6(uint8_t event);
extern void teleprompt_ui_fsm_handler_554170(uint8_t event, uint32_t arg);
extern void teleprompt_ui_init_55448e(void *parent);
extern void teleprompt_ui_deinit_55462e(void);
extern void teleprompt_ui_elapsed_time_update_55468c(void);
extern void teleprompt_ui_input_handler_555178(uint32_t code, const uint8_t *event);
extern void teleprompt_ui_pause_hint_show_556ad4(void);
extern void teleprompt_ui_pause_hint_hide_556b00(void);
extern void teleprompt_timer_mgr_process_auto_reflash_58922c(void);
extern int32_t teleprompt_machine_handler_58c89e(uint8_t event, const void *data, uint32_t len);
extern uint32_t APP_PbRxTelepromptFrameDataProcess(const uint8_t *data, uint16_t len, void *msg); /* 0x5885b4 */
extern uint32_t APP_PbTelepromptTxEncodeCommResp(uint8_t magic, const uint8_t *status);           /* 0x588792 */
extern uint32_t APP_PbTxEncodeStatusNotify(const uint16_t *status);                               /* 0x58887a */

static const char module_tag[] = "teleprompt"; /* ROM 0x78c4d0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt.c"; /* ROM 0x70665c */

static const char fn_mutex_init[] = "teleprompt_action_mutex_init_internal"; /* ROM 0x74eed4 */
static const char fn_lock[] = "teleprompt_action_lock"; /* ROM 0x77c2bc */
static const char fn_unlock[] = "teleprompt_action_unlock"; /* ROM 0x77297c */
static const char fn_request_display[] = "teleprompt_request_display"; /* ROM 0x772998 */
static const char fn_heartbeat[] = "teleprompt_heartbeat_check"; /* ROM 0x7729b4 */
static const char fn_data_recv[] = "teleprompt_data_recv_handler"; /* ROM 0x765c70 */
static const char fn_page_event[] = "teleprompt_page_event_handler"; /* ROM 0x765cb0 */
static const char fn_common_data[] = "Teleprompt_common_data_handler"; /* ROM 0x765cf0 */
static const char fn_ui_event[] = "Teleprompt_ui_event_handler"; /* ROM 0x7729d0 */

static const char msg_mutex_failed[] = "Failed to create teleprompt action mutex"; /* ROM 0x7444bc */
static const char msg_mutex_failed_s[] = "[teleprompt]Failed to create teleprompt action mutex"; /* ROM 0x723c78 */
static const char msg_mutex_created[] = "Teleprompt action mutex created successfully with priority inherit"; /* ROM 0x7066a0 */
static const char msg_mutex_created_s[] = "[teleprompt]Teleprompt action mutex created successfully with priority inherit"; /* ROM 0x6f0038 */
static const char msg_lock_init_failed[] = "Failed to initialize teleprompt action mutex"; /* ROM 0x739044 */
static const char msg_lock_init_failed_s[] = "[teleprompt]Failed to initialize teleprompt action mutex"; /* ROM 0x719378 */
static const char msg_acquire_failed[] = "Failed to acquire teleprompt action mutex, status: %d"; /* ROM 0x723cb0 */
static const char msg_acquire_failed_s[] = "[teleprompt]Failed to acquire teleprompt action mutex, status: %d"; /* ROM 0x7066e4 */
static const char msg_release_failed[] = "Failed to release teleprompt action mutex, status: %d"; /* ROM 0x723ce8 */
static const char msg_release_failed_s[] = "[teleprompt]Failed to release teleprompt action mutex, status: %d"; /* ROM 0x706728 */
static const char msg_request[] = "teleprompt request reflash, event: %d|%s, value: %d"; /* ROM 0x72e4c4 */
static const char msg_request_s[] = "[teleprompt]teleprompt request reflash, event: %d|%s, value: %d"; /* ROM 0x70fba4 */
static const char msg_not_running[] = "teleprompt is not running, ignore reflash request"; /* ROM 0x72e4f8 */
static const char msg_not_running_s[] = "[teleprompt]teleprompt is not running, ignore reflash request"; /* ROM 0x70fbe4 */
static const char msg_heartbeat_timeout[] = "Heartbeat timeout! Time diff: %u ms, timeout: %u ms"; /* ROM 0x72e52c */
static const char msg_heartbeat_timeout_s[] = "[teleprompt]Heartbeat timeout! Time diff: %u ms, timeout: %u ms"; /* ROM 0x70fc24 */
static const char msg_unknown_ctrl[] = "unknown ctrl cmd=%d"; /* ROM 0x783d98 */
static const char msg_unknown_ctrl_s[] = "[teleprompt]unknown ctrl cmd=%d"; /* ROM 0x765c90 */
static const char msg_unknown_command[] = "unknown command id=%d"; /* ROM 0x77c2d4 */
static const char msg_unknown_command_s[] = "[teleprompt]unknown command id=%d"; /* ROM 0x75ab6c */
static const char msg_foreground[] = "foregroundID = %d"; /* ROM 0x783dac */
static const char msg_foreground_s[] = "[teleprompt]foregroundID = %d"; /* ROM 0x765cd0 */
static const char msg_duplicate[] = "teleprompt duplicate packet, ignore and send success response"; /* ROM 0x70fc64 */
static const char msg_duplicate_s[] = "[teleprompt]teleprompt duplicate packet, ignore and send success response"; /* ROM 0x6f6790 */
static const char msg_rx_error[] = "teleprompt error: %d, send error response"; /* ROM 0x7444e8 */
static const char msg_rx_error_s[] = "[teleprompt]teleprompt error: %d, send error response"; /* ROM 0x723d20 */
static const char msg_recv_failed[] = "teleprompt data recv handler failed, ret: %d"; /* ROM 0x739074 */
static const char msg_recv_failed_s[] = "[teleprompt]teleprompt data recv handler failed, ret: %d"; /* ROM 0x7193b4 */
static const char msg_startup[] = "Teleprompt display startup"; /* ROM 0x7729ec */
static const char msg_startup_s[] = "[teleprompt]Teleprompt display startup"; /* ROM 0x74eefc */
static const char msg_exit[] = "Teleprompt display exit"; /* ROM 0x77c2ec */
static const char msg_exit_s[] = "[teleprompt]Teleprompt display exit"; /* ROM 0x75ab90 */
static const char msg_notify_close[] = "notify app to close"; /* ROM 0x783dc0 */
static const char msg_notify_close_s[] = "[teleprompt]notify app to close"; /* ROM 0x765d10 */

/* Usage records (ROM initialisers); the duration record's second word is
 * replaced by the session length in ms. */
static const g2_teleprompt_usage_record_t heartbeat_exit_record = {3u, 3u}; /* ROM 0x78eaac */
static const g2_teleprompt_usage_record_t system_exit_record = {3u, 1u};    /* ROM 0x78eab4 */
static const g2_teleprompt_usage_record_t duration_record = {3u, 0u};       /* ROM 0x78eabc */
static const uint16_t close_status = 4u;                                    /* ROM 0x78f6be */

#define TP_LOG(level, fn, line, cflags, name, ...)                                                 \
    do {                                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                                       \
            audio_log_extended((level), module_tag, source_file, (fn), (line), name,              \
                               ##__VA_ARGS__);                                                    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                     \
            (void)compress_log_output((cflags), name##_s, name##_s, ##__VA_ARGS__);              \
    } while (0)

int32_t teleprompt_action_mutex_init_internal_5899a4(void)
{
    if (g2_teleprompt_action_mutex_20074a68 == NULL) {
        g2_teleprompt_action_mutex_20074a68 = osMutexNew(g2_teleprompt_action_mutex_attr_7896e0);
        if (g2_teleprompt_action_mutex_20074a68 == NULL) {
            TP_LOG(1u, fn_mutex_init, 0x4eu, 0x04000000u, msg_mutex_failed);
            return -1;
        }
        TP_LOG(4u, fn_mutex_init, 0x51u, 0x10000000u, msg_mutex_created);
    }
    return 0;
}

/* 1 when the action mutex is held. */
uint32_t teleprompt_action_lock_589a4e(void)
{
    int32_t status;

    if (g2_teleprompt_action_mutex_20074a68 == NULL && teleprompt_action_mutex_init_internal_5899a4() != 0) {
        TP_LOG(1u, fn_lock, 0x60u, 0x04000000u, msg_lock_init_failed);
        return 0u;
    }
    status = osMutexAcquire(g2_teleprompt_action_mutex_20074a68, WAIT_FOREVER);
    if (status == 0)
        return 1u;
    TP_LOG(1u, fn_lock, 0x67u, 0x04400000u, msg_acquire_failed, status);
    return 0u;
}

void teleprompt_action_unlock_589b08(void)
{
    int32_t status;

    if (g2_teleprompt_action_mutex_20074a68 == NULL)
        return;
    status = osMutexRelease(g2_teleprompt_action_mutex_20074a68);
    if (status != 0)
        TP_LOG(1u, fn_unlock, 0x75u, 0x04400000u, msg_release_failed, status);
}

/* Stock teleprompt_request_display: send {event, value} to the app 6 page
 * on the master side while app 6 refresh is enabled. */
uint32_t teleprompt_controller_post_589b68(uint8_t event, uint32_t arg)
{
    g2_teleprompt_request_t request;

    if (audio_uart_device_role_get() != 1u)
        return 0u;
    request.event = event;
    request.value = arg;
    if (audio_quicklist_refresh_enabled_4434d0(TP_APP_ID) != 1u) {
        TP_LOG(2u, fn_request_display, 0x8eu, 0x08000000u, msg_not_running);
        return 0u;
    }
    if (event == TP_REQ_ELAPSED)
        TP_LOG(4u, fn_request_display, 0x87u, 0x10c00000u, msg_request, TP_REQ_ELAPSED,
               teleprompt_ui_event_name_5540d6(TP_REQ_ELAPSED), arg);
    else
        TP_LOG(3u, fn_request_display, 0x89u, 0x0cc00000u, msg_request, event,
               teleprompt_ui_event_name_5540d6(event), arg);
    return audio_uart_master_display_refresh(TP_APP_ID, &request, sizeof request, 0u);
}

/* Heartbeat refresh: any accepted frame or page restore re-arms the watchdog. */
void teleprompt_activity_tick_update_589cb4(void)
{
    if (audio_uart_device_role_get() == 1u)
        g2_teleprompt_heartbeat_tick_20074a64 = osKernelGetTickCount();
}

void teleprompt_heartbeat_check_589cca(void)
{
    uint32_t diff;
    g2_teleprompt_usage_record_t record;

    if (audio_uart_device_role_get() != 1u)
        return;
    if (g2_teleprompt_fsm_ctrl.page_covered != 0u)
        return;
    diff = osKernelGetTickCount() - g2_teleprompt_heartbeat_tick_20074a64;
    if (diff <= TP_HEARTBEAT_TIMEOUT_MS)
        return;
    TP_LOG(1u, fn_heartbeat, 0xb2u, 0x04800000u, msg_heartbeat_timeout, diff,
           TP_HEARTBEAT_TIMEOUT_MS);
    teleprompt_activity_tick_update_589cb4();
    record = heartbeat_exit_record;
    audio_uart_ring_wear_persist_48eb32(TP_EXIT_RECORD_KEY, 2u, &record);
    (void)teleprompt_controller_post_589b68(TP_REQ_EXIT, 1u);
}

/* command_id -> teleprompt FSM event (payload after the 4-byte header):
 * 1 control (sub-command byte 1..4 -> events 1..4, 0x30 bytes),
 * 2 page data (5, 0xf52), 3 file list (6, 0x40c), 4 AI sync (7, 0xc),
 * 0xa5 scroll sync (8, 0xc), 0xff heartbeat (9, 0x10). */
int32_t teleprompt_data_recv_handler_589d74(const uint8_t *msg)
{
    const uint8_t *payload = msg + 4;

    switch (msg[0]) {
    case 0x01u:
        switch (payload[0]) {
        case 1u: return teleprompt_machine_handler_58c89e(1u, payload, 0x30u);
        case 2u: return teleprompt_machine_handler_58c89e(2u, payload, 0x30u);
        case 3u: return teleprompt_machine_handler_58c89e(3u, payload, 0x30u);
        case 4u: return teleprompt_machine_handler_58c89e(4u, payload, 0x30u);
        default:
            TP_LOG(2u, fn_data_recv, 0xcdu, 0x08400000u, msg_unknown_ctrl, payload[0]);
            return -1;
        }
    case 0x02u: return teleprompt_machine_handler_58c89e(5u, payload, 0xf52u);
    case 0x03u: return teleprompt_machine_handler_58c89e(6u, payload, 0x40cu);
    case 0x04u: return teleprompt_machine_handler_58c89e(7u, payload, 0x0cu);
    case 0xa5u: return teleprompt_machine_handler_58c89e(8u, payload, 0x0cu);
    case 0xffu: return teleprompt_machine_handler_58c89e(9u, payload, 0x10u);
    default:
        TP_LOG(2u, fn_data_recv, 0xdbu, 0x08400000u, msg_unknown_command, msg[0]);
        return -1;
    }
}

/* Page input / foreground callback; scroll directions are swapped before
 * they reach the UI. Always returns 1 (handled). */
uint32_t teleprompt_page_event_handler_589eb6(void *ctx, uint32_t arg, uint32_t code,
                                              const uint32_t *event)
{
    uint32_t mapped = code;
    uint32_t foreground_id;
    g2_teleprompt_usage_record_t record;

    (void)ctx;
    (void)arg;
    if (code == TP_INPUT_SCROLL_UP)
        mapped = TP_INPUT_SCROLL_DOWN;
    else if (code == TP_INPUT_SCROLL_DOWN)
        mapped = TP_INPUT_SCROLL_UP;

    switch (code) {
    case TP_INPUT_CLICK:
    case TP_INPUT_SCROLL_UP:
    case TP_INPUT_SCROLL_DOWN:
    case TP_INPUT_CLOSE:
    case TP_INPUT_SCROLL_STOP:
        teleprompt_ui_input_handler_555178(mapped, (const uint8_t *)event);
        break;

    case TP_INPUT_FOREGROUND_COVERED:
        if (teleprompt_ui_state_get_5540b2() == TP_UI_STATE_3)
            break;
        foreground_id = event != NULL ? *event : 0u;
        TP_LOG(3u, fn_page_event, 0xf7u, 0x0c400000u, msg_foreground, foreground_id);
        if (g2_teleprompt_root_20074a7c != NULL && foreground_id != 0u && foreground_id != 0x21u)
            audio_uart_display_audio_reset_441488(g2_teleprompt_root_20074a7c, 0x7fu, 0u);
        if (foreground_id == 0x22u)
            teleprompt_ui_pause_hint_show_556ad4();
        g2_teleprompt_fsm_ctrl.page_covered = 1u;
        break;

    case TP_INPUT_FOREGROUND_RESTORED:
        if (teleprompt_ui_state_get_5540b2() == TP_UI_STATE_3)
            break;
        audio_uart_display_audio_reset_441488(g2_teleprompt_root_20074a7c, 0xffu, 0u);
        teleprompt_ui_pause_hint_hide_556b00();
        teleprompt_activity_tick_update_589cb4();
        g2_teleprompt_fsm_ctrl.page_covered = 0u;
        break;

    case TP_INPUT_SYSTEM_EXIT:
        if (audio_uart_device_role_get() == 1u) {
            record = system_exit_record;
            audio_uart_ring_wear_persist_48eb32(TP_EXIT_RECORD_KEY, 2u, &record);
        }
        (void)teleprompt_controller_post_589b68(TP_REQ_EXIT, 0u);
        break;

    default:
        break;
    }
    return 1u;
}

/* Stock Teleprompt_common_data_handler (registry data callback). */
uint32_t audio_uart_registry_callback_589fe6(uint32_t event, const uint8_t *data, uint32_t len)
{
    uint8_t *result = &g2_teleprompt_rx_result_2010938c;
    const uint8_t *msg = g2_teleprompt_pb_rx_msg_20060154;
    int32_t ret;

    (void)teleprompt_action_lock_589a4e();
    if (event == 0u) {
        *result = (uint8_t)APP_PbRxTelepromptFrameDataProcess(data, (uint16_t)len,
                                                              g2_teleprompt_pb_rx_msg_20060154);
        if (*result == TP_RX_DUPLICATE) {
            TP_LOG(2u, fn_common_data, 0x12au, 0x08000000u, msg_duplicate);
            *result = 0u;
            (void)APP_PbTelepromptTxEncodeCommResp(msg[1], result);
        } else if (*result == 0u) {
            ret = teleprompt_data_recv_handler_589d74(msg);
            if (ret == 0) {
                *result = 0u;
                (void)APP_PbTelepromptTxEncodeCommResp(msg[1], result);
                teleprompt_activity_tick_update_589cb4();
            } else {
                TP_LOG(2u, fn_common_data, 0x137u, 0x08400000u, msg_recv_failed, ret);
                *result = 1u;
                (void)APP_PbTelepromptTxEncodeCommResp(msg[1], result);
            }
        } else {
            TP_LOG(2u, fn_common_data, 0x130u, 0x08400000u, msg_rx_error, *result);
            *result = 1u;
            (void)APP_PbTelepromptTxEncodeCommResp(msg[1], result);
        }
    }
    teleprompt_action_unlock_589b08();
    return 0u;
}

/* Stock Teleprompt_ui_event_handler (registry UI callback). */
uint32_t audio_uart_registry_callback_58a130(uint32_t event, const void *payload, uint32_t length,
                                             void *parent)
{
    g2_teleprompt_request_t request;
    g2_teleprompt_usage_record_t record;
    uint16_t status;
    uint32_t duration_ms;
    uint64_t scaled;

    (void)length;
    (void)aeabi_memset_43c0e4(&request, sizeof request, 0);
    (void)teleprompt_action_lock_589a4e();
    switch (event) {
    case TP_UI_EVT_STARTUP:
        TP_LOG(3u, fn_ui_event, 0x14du, 0x0c000000u, msg_startup);
        g2_teleprompt_start_tick_20074a60 = osKernelGetTickCount();
        request.event = g2_teleprompt_fsm_ctrl.state == 0u ? 1u : 2u;
        ble_state_skip_manual_start(0u);
        teleprompt_activity_tick_update_589cb4();
        teleprompt_ui_init_55448e(parent);
        teleprompt_ui_fsm_handler_554170(request.event, request.value);
        audio_uart_registry_context_20003da4.root = g2_teleprompt_root_20074a7c;
        break;

    case TP_UI_EVT_REQUEST:
        (void)audio_queue_copy_bytes(&request, payload, sizeof request);
        teleprompt_ui_fsm_handler_554170(request.event, request.value);
        break;

    case TP_UI_EVT_TICK:
        teleprompt_timer_mgr_process_auto_reflash_58922c();
        teleprompt_heartbeat_check_589cca();
        teleprompt_ui_elapsed_time_update_55468c();
        break;

    case TP_UI_EVT_EXIT:
        TP_LOG(3u, fn_ui_event, 0x164u, 0x0c000000u, msg_exit);
        teleprompt_file_list_reset();
        teleprompt_page_data_deinit();
        teleprompt_ui_deinit_55462e();
        audio_ble_param_reset_delayed_event(10000u);
        (void)audio_terminal_reset_mode_notice_54f50e(2u);
        if (g2_teleprompt_fsm_ctrl.state == 1u && audio_uart_device_role_get() == 1u) {
            TP_LOG(3u, fn_ui_event, 0x16cu, 0x0c000000u, msg_notify_close);
            status = close_status;
            (void)APP_PbTxEncodeStatusNotify(&status);
        }
        (void)aeabi_memset_43c0e4(&g2_teleprompt_fsm_ctrl, sizeof g2_teleprompt_fsm_ctrl, 0);
        /* ticks -> ms through a u64 multiply and divide by the 1000 Hz tick rate */
        scaled = (uint64_t)(osKernelGetTickCount() - g2_teleprompt_start_tick_20074a60) * 1000u;
        duration_ms = (uint32_t)audio_uart_ring_u64_div_47cc60((uint32_t)scaled,
                                                               (uint32_t)(scaled >> 32), 1000u, 0u);
        if (audio_uart_device_role_get() == 1u) {
            record = duration_record;
            record.value = duration_ms;
            audio_uart_ring_wear_persist_48eb32(TP_DURATION_RECORD_KEY, 2u, &record);
        }
        break;

    default:
        break;
    }
    teleprompt_action_unlock_589b08();
    return 0u;
}
