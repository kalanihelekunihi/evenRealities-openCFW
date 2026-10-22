/* Translate app core, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate.c.
 * Native 0x59e9e2..0x59f3fe; literal pool 0x59f400..0x59f50c.
 *
 * The two registry callbacks (Translate_common_data_handler 0x59f0ea and
 * Translate_ui_event_handler 0x59f236) are installed by app registry row 35
 * (ROM 0x6a46e0, app id 5); they keep the names already used by
 * system/ui-registry/ui_registry_table.c. translate_page_event_handler 0x59efe0
 * is referenced from ROM 0x794174. Every entry point except the mutex helpers
 * is serialised by the "TranslateActionMutex". */
#include <stdint.h>
#include <stddef.h>

/* CMSIS-RTOS2 osMutexAttr_t. */
typedef struct {
    const char *name;   /* +0x0 */
    uint32_t attr_bits; /* +0x4 */
    void *cb_mem;       /* +0x8 */
    uint32_t cb_size;   /* +0xc */
} g2_os_mutex_attr_t;

/* Decoded translate protobuf message (RX buffer RAM 0x2006496c, 0x854 bytes). */
typedef struct {
    uint8_t command_id;     /* +0x000 1 ctrl, 2 result, 0xff heartbeat */
    uint8_t magic_random;   /* +0x001 */
    uint16_t which_payload; /* +0x002 */
    uint8_t payload[0x850]; /* +0x004 ctrl: byte 0 = ctrl cmd (0x14 bytes); result: 0x850 bytes */
} g2_translate_pb_msg_t;
_Static_assert(sizeof(g2_translate_pb_msg_t) == 0x854u, "stock memset length");

/* Display-sync request sent to the peer (stack, 8 bytes). */
typedef struct {
    uint8_t event;  /* +0x0 */
    uint32_t value; /* +0x4 */
} g2_translate_display_req_t;
_Static_assert(sizeof(g2_translate_display_req_t) == 8u, "stock request size");

/* UI event block copied from the registry argument (stack, 8 bytes). */
typedef struct {
    uint8_t event;  /* +0x0 */
    uint32_t value; /* +0x4 */
} g2_translate_ui_event_t;

extern void *g2_translate_action_mutex;                 /* RAM 0x20074af0 */
extern uint32_t g2_translate_heartbeat_tick;            /* RAM 0x20074aec */
extern uint32_t g2_translate_display_start_tick;        /* RAM 0x20074ae8 */
extern void *g2_translate_root_object;                  /* RAM 0x20074afc, LVGL page object */
extern uint8_t g2_translate_session[16];                /* RAM 0x2011df24, byte 0 = phone app active */
extern uint8_t g2_translate_ui_context[];                /* RAM 0x2000418c, +4 receives the page object */
extern uint8_t g2_translate_pb_status;                  /* RAM 0x20119efc */
extern g2_translate_pb_msg_t g2_translate_pb_rx_msg;    /* RAM 0x2006496c */
extern uint8_t g2_translate_text_buffer[0x2012];        /* RAM 0x20119f00 */
extern uint8_t g2_translate_source_buffer[0x1008];      /* RAM 0x2011bf14 */
extern uint8_t g2_translate_target_buffer[0x1008];      /* RAM 0x2011cf1c */

extern void *osMutexNew(const void *attr);
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);
extern int32_t osMutexRelease(void *mutex);
extern uint32_t osKernelGetTickCount(void);
extern uint32_t audio_log_flags(void);                                       /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);                 /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);              /* memset(p, n, c) 0x43c0e4 */
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);        /* memcpy 0x439be4 */
extern uint8_t audio_uart_device_role_get(void);                             /* 0x45a568, 1 = master */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);        /* app running query */
extern uint32_t audio_uart_master_display_refresh(uint32_t, const void *, uint16_t, uint32_t); /* 0x464bb2 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t, uint32_t, const void *); /* event report */
extern void audio_uart_display_audio_reset_441488(uint32_t, uint32_t, uint32_t); /* lv opa set */
extern void audio_tracepoint_reset_pull_478110(uint8_t);                     /* ble_state_skip_manual_start */
extern void audio_ble_param_reset_delayed_event(uint32_t);                   /* 0x478252 */
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t);           /* AUDM_appRelease */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t, uint32_t, uint32_t, uint32_t);
extern int32_t translate_machine_handler_596b0c(uint32_t event, const void *data, uint32_t length);
extern void translate_ui_0059d8f0(uint32_t);                                 /* translate_ui_init */
extern void translate_ui_0059d9d4(void);                                     /* translate_ui_deinit */
extern void translate_ui_0059da94(uint32_t event, const void *param);        /* translate_input_event_handler */
extern uint8_t translate_ui_0059db5c(void);                                  /* UI state getter */
extern const char *translate_ui_0059db80(uint8_t event);                     /* display event name */
extern void translate_ui_0059db9a(uint8_t event, uint32_t value);            /* translate_ui_fsm_handler */
extern void translate_ui_0059df04(void);                                     /* translate_ui_text_refresh_check */
extern uint32_t APP_PbTranslateTxEncodeNotify(const uint16_t *notify);
extern uint32_t APP_PbTranslateTxEncodeCommResp(const uint8_t *resp, uint8_t magic);
extern uint32_t APP_PbTranslateRxFrameDataProcess(const uint8_t *data, uint16_t length,
                                                  g2_translate_pb_msg_t *msg);

#define TRANSLATE_APP_ID 5u
#define TRANSLATE_HEARTBEAT_TIMEOUT_MS 20000u
#define TRANSLATE_EVENT_REPORT_KEY 0x40102u   /* ROM 0x59f46c */
#define TRANSLATE_DURATION_REPORT_KEY 0x40103u /* ROM 0x59f50c */

static const char mutex_name[] = "TranslateActionMutex"; /* ROM 0x77cde4 */
static const g2_os_mutex_attr_t translate_mutex_attr = { /* ROM 0x789c30 */
    mutex_name, 0u, NULL, 0u
};
static const uint32_t heartbeat_timeout_report[2] = { 2u, 3u }; /* ROM 0x78ec34 */
static const uint32_t page_exit_report[2] = { 2u, 1u };         /* ROM 0x78ec3c */
static const uint32_t duration_report_head = 2u;                /* ROM 0x78ec44 */
static const uint16_t close_notify = 2u;                        /* ROM 0x78f6c2 */

static const char module[] = "translate"; /* ROM 0x78c77c */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\translate\\translate.c"; /* ROM 0x70764c */

static const char fn_mutex_init[] = "translate_action_mutex_init_internal"; /* ROM 0x7502d4 */
static const char msg_mutex_fail[] = "Failed to create translate action mutex"; /* ROM 0x7502fc */
static const char short_mutex_fail[] = "[translate]Failed to create translate action mutex"; /* ROM 0x72f774 */
static const char msg_mutex_ok[] =
    "Translate action mutex created successfully with priority inherit"; /* ROM 0x707690 */
static const char short_mutex_ok[] =
    "[translate]Translate action mutex created successfully with priority inherit"; /* ROM 0x6f0858 */

static const char fn_lock[] = "translate_action_lock"; /* ROM 0x77cdfc */
static const char msg_lock_init[] = "Failed to initialize translate action mutex"; /* ROM 0x745988 */
static const char short_lock_init[] = "[translate]Failed to initialize translate action mutex"; /* ROM 0x724d50 */
static const char msg_lock_fail[] = "Failed to acquire translate action mutex, status: %d"; /* ROM 0x724d88 */
static const char short_lock_fail[] =
    "[translate]Failed to acquire translate action mutex, status: %d"; /* ROM 0x7108a4 */

static const char fn_unlock[] = "translate_action_unlock"; /* ROM 0x77ce14 */
static const char msg_unlock_fail[] = "Failed to release translate action mutex, status: %d"; /* ROM 0x724dc0 */
static const char short_unlock_fail[] =
    "[translate]Failed to release translate action mutex, status: %d"; /* ROM 0x7108e4 */

static const char fn_request[] = "translate_request_display"; /* ROM 0x773a1c */
static const char msg_request[] = "translate request reflash, event: %d|%s, value: %d"; /* ROM 0x72f7a8 */
static const char short_request[] =
    "[translate]translate request reflash, event: %d|%s, value: %d"; /* ROM 0x710924 */
static const char msg_not_running[] = "translate is not running, ignore reflash request"; /* ROM 0x72f7dc */
static const char short_not_running[] =
    "[translate]translate is not running, ignore reflash request"; /* ROM 0x71a584 */

static const char fn_heartbeat[] = "translate_heartbeat_check"; /* ROM 0x773a38 */
static const char msg_heartbeat[] = "Heartbeat timeout! Time diff: %u ms, timeout: %u ms"; /* ROM 0x72f810 */
static const char short_heartbeat[] =
    "[translate]Heartbeat timeout! Time diff: %u ms, timeout: %u ms"; /* ROM 0x710964 */

static const char fn_recv[] = "translate_data_recv_handler"; /* ROM 0x773a54 */
static const char msg_recv[] = "translate pb handler: command_id =%d"; /* ROM 0x750324 */
static const char short_recv[] = "[translate]translate pb handler: command_id =%d"; /* ROM 0x73a364 */
static const char msg_ctrl[] = "translate ctrl: cmd = %d"; /* ROM 0x773a70 */
static const char short_ctrl[] = "[translate]translate ctrl: cmd = %d"; /* ROM 0x75beb0 */
static const char msg_ctrl_unknown[] = "unknown ctrl cmd=%d"; /* ROM 0x784518 */
static const char short_ctrl_unknown[] = "[translate]unknown ctrl cmd=%d"; /* ROM 0x766e50 */
static const char msg_result[] = "translate result received"; /* ROM 0x773a8c */
static const char short_result[] = "[translate]translate result received"; /* ROM 0x75034c */
static const char msg_hb_rx[] = "translate heartbeat received"; /* ROM 0x766e70 */
static const char short_hb_rx[] = "[translate]translate heartbeat received"; /* ROM 0x750374 */
static const char msg_cmd_unknown[] = "unknown command id=%d"; /* ROM 0x77ce2c */
static const char short_cmd_unknown[] = "[translate]unknown command id=%d"; /* ROM 0x75bed4 */

static const char fn_page[] = "translate_page_event_handler"; /* ROM 0x766e90 */
static const char msg_foreground[] = "foregroundID = %d"; /* ROM 0x78452c */
static const char short_foreground[] = "[translate]foregroundID = %d"; /* ROM 0x766eb0 */

static const char fn_common[] = "Translate_common_data_handler"; /* ROM 0x766ed0 */
static const char msg_duplicate[] =
    "translate duplicate packet, ignore and send success response"; /* ROM 0x7109a4 */
static const char short_duplicate[] =
    "[translate]translate duplicate packet, ignore and send success response"; /* ROM 0x6fe54c */
static const char msg_error[] = "translate error: %d, send error response"; /* ROM 0x7459b4 */
static const char short_error[] = "[translate]translate error: %d, send error response"; /* ROM 0x72f844 */
static const char msg_recv_fail[] = "translate data recv handler failed, ret: %d"; /* ROM 0x7459e0 */
static const char short_recv_fail[] =
    "[translate]translate data recv handler failed, ret: %d"; /* ROM 0x724df8 */

static const char fn_ui[] = "Translate_ui_event_handler"; /* ROM 0x773aa8 */
static const char msg_startup[] = "Translate display startup"; /* ROM 0x773ac4 */
static const char short_startup[] = "[translate]Translate display startup"; /* ROM 0x75039c */
static const char msg_exit[] = "Translate display exit"; /* ROM 0x77ce44 */
static const char short_exit[] = "[translate]Translate display exit"; /* ROM 0x75bef8 */
static const char msg_close[] = "notify app to close"; /* ROM 0x784540 */
static const char short_close[] = "[translate]notify app to close"; /* ROM 0x766ef0 */

/* Stock logging pattern: full record when flag bit1 is set, compressed record when
 * bit0 or bit2 is set. */
#define LOG0(level, fn, line, msg, code, short_msg)                                \
    do {                                                                           \
        if ((audio_log_flags() & 2u) != 0u)                                        \
            audio_log_extended((level), module, path, (fn), (line), (msg));        \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)      \
            (void)compress_log_output((code), (short_msg), (short_msg));           \
    } while (0)
#define LOGN(level, fn, line, msg, code, short_msg, ...)                           \
    do {                                                                           \
        if ((audio_log_flags() & 2u) != 0u)                                        \
            audio_log_extended((level), module, path, (fn), (line), (msg),         \
                               __VA_ARGS__);                                       \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)      \
            (void)compress_log_output((code), (short_msg), (short_msg),            \
                                      __VA_ARGS__);                                \
    } while (0)

/* Clears the three translate text buffers (called from the FSM and the UI). */
void translate_buffers_reset_59e9e2(void)
{
    audio_uart_buffer_zero(g2_translate_text_buffer, sizeof g2_translate_text_buffer, 0u);
    audio_uart_buffer_zero(g2_translate_source_buffer, sizeof g2_translate_source_buffer, 0u);
    audio_uart_buffer_zero(g2_translate_target_buffer, sizeof g2_translate_target_buffer, 0u);
}

int32_t translate_action_mutex_init_internal_59ea64(void)
{
    if (g2_translate_action_mutex == NULL) {
        g2_translate_action_mutex = osMutexNew(&translate_mutex_attr);
        if (g2_translate_action_mutex == NULL) {
            LOG0(1u, fn_mutex_init, 0x4au, msg_mutex_fail, 0x4000000u, short_mutex_fail);
            return -1;
        }
        LOG0(4u, fn_mutex_init, 0x4du, msg_mutex_ok, 0x10000000u, short_mutex_ok);
    }
    return 0;
}

/* Returns 1 when the mutex is held, 0 on failure (lazily creates it). */
uint32_t translate_action_lock_59eb0e(void)
{
    if (g2_translate_action_mutex == NULL && translate_action_mutex_init_internal_59ea64() != 0) {
        LOG0(1u, fn_lock, 0x5cu, msg_lock_init, 0x4000000u, short_lock_init);
        return 0u;
    }
    int32_t status = osMutexAcquire(g2_translate_action_mutex, 0xffffffffu);
    if (status == 0)
        return 1u;
    LOGN(1u, fn_lock, 99u, msg_lock_fail, 0x4400000u, short_lock_fail, status);
    return 0u;
}

void translate_action_unlock_59ebc8(void)
{
    if (g2_translate_action_mutex == NULL)
        return;
    int32_t status = osMutexRelease(g2_translate_action_mutex);
    if (status != 0)
        LOGN(1u, fn_unlock, 0x71u, msg_unlock_fail, 0x4400000u, short_unlock_fail, status);
}

/* Master only: forwards a display event to the peer if the translate app runs. */
uint32_t translate_request_display_59ec28(uint8_t event, uint32_t value)
{
    if (audio_uart_device_role_get() != 1u)
        return 0u;
    g2_translate_display_req_t req;
    req.event = event;
    req.value = value;
    if (audio_quicklist_refresh_enabled_4434d0(TRANSLATE_APP_ID) != 1u) {
        LOG0(2u, fn_request, 0x86u, msg_not_running, 0x8000000u, short_not_running);
        return 0u;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_request, 0x82u, msg_request, event,
                           translate_ui_0059db80(event), value);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0xcc00000u, short_request, short_request, event,
                                  translate_ui_0059db80(event), value);
    return audio_uart_master_display_refresh(TRANSLATE_APP_ID, &req, sizeof req, 0u);
}

void translate_heartbeat_refresh_59ed06(void)
{
    if (audio_uart_device_role_get() == 1u)
        g2_translate_heartbeat_tick = osKernelGetTickCount();
}

void translate_heartbeat_check_59ed1c(void)
{
    if (audio_uart_device_role_get() != 1u)
        return;
    uint32_t diff = osKernelGetTickCount() - g2_translate_heartbeat_tick;
    if (diff <= TRANSLATE_HEARTBEAT_TIMEOUT_MS)
        return;
    LOGN(1u, fn_heartbeat, 0xa4u, msg_heartbeat, 0x4800000u, short_heartbeat, diff,
         TRANSLATE_HEARTBEAT_TIMEOUT_MS);
    translate_heartbeat_refresh_59ed06();
    uint32_t report[2] = { heartbeat_timeout_report[0], heartbeat_timeout_report[1] };
    audio_uart_ring_wear_persist_48eb32(TRANSLATE_EVENT_REPORT_KEY, 2u, report);
    (void)translate_request_display_59ec28(7u, 1u);
}

/* Maps a decoded phone message onto translate FSM events
 * (ctrl 1/2/3/4 -> 1/4/2/3, result -> 5, heartbeat -> 6). */
int32_t translate_data_recv_handler_59edba(const g2_translate_pb_msg_t *msg)
{
    LOGN(4u, fn_recv, 0xb3u, msg_recv, 0x10400000u, short_recv, msg->command_id);
    switch (msg->command_id) {
    case 1u:
        LOGN(4u, fn_recv, 0xb6u, msg_ctrl, 0x10400000u, short_ctrl, msg->payload[0]);
        switch (msg->payload[0]) {
        case 1u:
            return translate_machine_handler_596b0c(1u, msg->payload, 0x14u);
        case 2u:
            return translate_machine_handler_596b0c(4u, msg->payload, 0x14u);
        case 3u:
            return translate_machine_handler_596b0c(2u, msg->payload, 0x14u);
        case 4u:
            return translate_machine_handler_596b0c(3u, msg->payload, 0x14u);
        default:
            break;
        }
        LOGN(2u, fn_recv, 0xc1u, msg_ctrl_unknown, 0x8400000u, short_ctrl_unknown,
             msg->payload[0]);
        return -1;
    case 2u:
        LOG0(4u, fn_recv, 0xc5u, msg_result, 0x10000000u, short_result);
        return translate_machine_handler_596b0c(5u, msg->payload, 0x850u);
    case 0xffu:
        LOG0(4u, fn_recv, 200u, msg_hb_rx, 0x10000000u, short_hb_rx);
        return translate_machine_handler_596b0c(6u, NULL, 0u);
    default:
        LOGN(2u, fn_recv, 0xcbu, msg_cmd_unknown, 0x8400000u, short_cmd_unknown,
             msg->command_id);
        return -1;
    }
}

/* Page input handler. Events 0x44/0x45 are swapped before dispatch. */
uint32_t translate_page_event_handler_59efe0(uint32_t unused0, uint32_t unused1,
                                             uint32_t event, const uint32_t *param)
{
    (void)unused0;
    (void)unused1;
    if (event == 0x44u)
        event = 0x45u;
    else if (event == 0x45u)
        event = 0x44u;

    switch (event) {
    case 0x0au:
    case 0x44u:
    case 0x45u:
    case 0x48u:
        translate_ui_0059da94(event, param);
        break;
    case 0x42u:
        if (translate_ui_0059db5c() != 2u) {
            uint32_t foreground = 0u;
            if (param != NULL)
                foreground = *param;
            LOGN(3u, fn_page, 0xe4u, msg_foreground, 0xc400000u, short_foreground, foreground);
            if (g2_translate_root_object != NULL && foreground != 0u && foreground != 0x21u)
                audio_uart_display_audio_reset_441488((uint32_t)(uintptr_t)g2_translate_root_object,
                                                      0x7fu, 0u);
        }
        break;
    case 0x43u:
        if (translate_ui_0059db5c() != 2u)
            audio_uart_display_audio_reset_441488((uint32_t)(uintptr_t)g2_translate_root_object,
                                                  0xffu, 0u);
        break;
    case 0x4fu:
        if (audio_uart_device_role_get() == 1u) {
            uint32_t report[2] = { page_exit_report[0], page_exit_report[1] };
            audio_uart_ring_wear_persist_48eb32(TRANSLATE_EVENT_REPORT_KEY, 2u, report);
        }
        (void)translate_request_display_59ec28(7u, 0u);
        break;
    default:
        break;
    }
    return 1u;
}

/* Translate_common_data_handler: type 0 = protobuf frame from the phone. The
 * response echoes the request magic; status 13 (duplicate) is answered as 0. */
uint32_t audio_uart_registry_callback_59f0ea(uint32_t type, const uint8_t *data, uint32_t length)
{
    (void)translate_action_lock_59eb0e();
    if (type == 0u) {
        g2_translate_pb_msg_t *msg = &g2_translate_pb_rx_msg;
        g2_translate_pb_status =
            (uint8_t)APP_PbTranslateRxFrameDataProcess(data, (uint16_t)length, msg);
        if (g2_translate_pb_status == 13u) {
            LOG0(2u, fn_common, 0x107u, msg_duplicate, 0x8000000u, short_duplicate);
            g2_translate_pb_status = 0u;
            (void)APP_PbTranslateTxEncodeCommResp(&g2_translate_pb_status, msg->magic_random);
        } else if (g2_translate_pb_status != 0u) {
            LOGN(2u, fn_common, 0x10du, msg_error, 0x8400000u, short_error,
                 g2_translate_pb_status);
            g2_translate_pb_status = 7u;
            (void)APP_PbTranslateTxEncodeCommResp(&g2_translate_pb_status, msg->magic_random);
        } else {
            int32_t ret = translate_data_recv_handler_59edba(msg);
            if (ret == 0) {
                g2_translate_pb_status = 0u;
                (void)APP_PbTranslateTxEncodeCommResp(&g2_translate_pb_status, msg->magic_random);
                translate_heartbeat_refresh_59ed06();
            } else {
                LOGN(2u, fn_common, 0x114u, msg_recv_fail, 0x8400000u, short_recv_fail, ret);
                g2_translate_pb_status = 7u;
                (void)APP_PbTranslateTxEncodeCommResp(&g2_translate_pb_status, msg->magic_random);
            }
        }
    }
    translate_action_unlock_59ebc8();
    return 0u;
}

/* Translate_ui_event_handler: 2 startup, 3 UI event block, 4 periodic tick, 5 exit. */
uint32_t audio_uart_registry_callback_59f236(uint32_t event, const void *data, uint32_t unused,
                                             uint32_t init_arg)
{
    (void)unused;
    g2_translate_ui_event_t ui;
    audio_uart_buffer_zero(&ui, sizeof ui, 0u);
    (void)translate_action_lock_59eb0e();
    switch (event) {
    case 2u:
        LOG0(3u, fn_ui, 0x12au, msg_startup, 0xc000000u, short_startup);
        g2_translate_display_start_tick = osKernelGetTickCount();
        ui.event = (g2_translate_session[0] == 0u) ? 3u : 4u;
        audio_tracepoint_reset_pull_478110(0u);
        translate_heartbeat_refresh_59ed06();
        translate_ui_0059d8f0(init_arg);
        translate_ui_0059db9a(ui.event, ui.value);
        *(void **)(void *)(g2_translate_ui_context + 4) = g2_translate_root_object;
        break;
    case 3u:
        audio_uart_checksum_copy(&ui, data, sizeof ui);
        translate_ui_0059db9a(ui.event, ui.value);
        break;
    case 4u:
        translate_heartbeat_check_59ed1c();
        translate_ui_0059df04();
        break;
    case 5u: {
        LOG0(3u, fn_ui, 0x141u, msg_exit, 0xc000000u, short_exit);
        translate_ui_0059d9d4();
        audio_ble_param_reset_delayed_event(10000u);
        (void)audio_terminal_reset_mode_notice_54f50e(1u);
        if (g2_translate_session[0] == 1u) {
            LOG0(3u, fn_ui, 0x146u, msg_close, 0xc000000u, short_close);
            uint16_t notify = close_notify;
            (void)APP_PbTranslateTxEncodeNotify(&notify);
        }
        audio_uart_buffer_zero(g2_translate_session, sizeof g2_translate_session, 0u);
        /* Display time in ms: ticks * 1000 / configTICK_RATE_HZ (1000). */
        uint64_t scaled = (uint64_t)(osKernelGetTickCount() - g2_translate_display_start_tick) * 1000u;
        uint32_t duration = (uint32_t)audio_uart_ring_u64_div_47cc60((uint32_t)scaled,
                                                                    (uint32_t)(scaled >> 32),
                                                                    1000u, 0u);
        if (audio_uart_device_role_get() == 1u) {
            uint32_t report[2];
            report[0] = duration_report_head;
            report[1] = duration;
            audio_uart_ring_wear_persist_48eb32(TRANSLATE_DURATION_REPORT_KEY, 2u, report);
        }
        break;
    }
    default:
        break;
    }
    translate_action_unlock_59ebc8();
    return 0u;
}
