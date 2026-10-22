/* Sync schedule-manager thread (_SyncScheduleManagerThreadHandler),
 * stock D:\01_workspace\s200_ap510b_iar_git\framework\sync\sync_framework.c.
 * Native 0x45c058..0x45d1b7; literal pools 0x45cd18..0x45cd9f, 0x45ceb0..0x45cebf,
 * 0x45cf60..0x45cf6b, 0x45cfec..0x45cff7, 0x45d064..0x45d06f, 0x45d0c4..0x45d0cf,
 * 0x45d138..0x45d147 and further shared words up to 0x45dd34.
 *
 * Started by SyncScheduleManagerInit (0x45d1ec, app/master-prepare). It drains
 * the schedule queue (RAM 0x200749d0), arbitrates display packets against the
 * system display status byte (RAM 0x20075023: 0 idle, 1 app running), retags
 * accepted packets as sync send type 2 (display) or 3 (input) and forwards them
 * to the sync send queue (RAM 0x200749cc), then wakes the UART sync thread with
 * event bit 2 (SyncModuleSendDataHandler 0x45e664). Idle input events start
 * apps locally through MasterDisplayStart (0x464b2e). */
#include <stdint.h>
#include <stddef.h>

/* Sync packet node; same layout as the send-queue node consumed by 0x45e664. */
typedef struct {
    uint32_t id;      /* +0x0 */
    uint16_t type;    /* +0x4 SyncEventType; rewritten to 2 (display) or 3 (input) */
    uint16_t size;    /* +0x6 payload length */
    uint8_t *payload; /* +0x8 heap buffer */
} sync_packet_t;
_Static_assert(sizeof(sync_packet_t) == 12, "sync packet node");

/* Payload head: byte 0 sub-code, byte 1 command, u16 app id (input source for
 * command 7), u32 input event id (command 7 only). */
typedef struct {
    uint8_t sub;      /* +0x0 */
    uint8_t command;  /* +0x1 */
    uint16_t app_id;  /* +0x2 */
    uint32_t event;   /* +0x4 */
} sync_payload_t;

typedef struct {
    const char *name;   /* +0x0 */
    uint32_t attr_bits; /* +0x4 osMutexPrioInherit */
    void *cb_mem;       /* +0x8 */
    uint32_t cb_size;   /* +0xc */
} g2_os_mutex_attr_t;   /* osMutexAttr_t */
_Static_assert(sizeof(g2_os_mutex_attr_t) == 16, "osMutexAttr_t");

enum {
    SYNC_TYPE_DISPLAY = 2u,
    SYNC_TYPE_INPUT = 3u,
};
enum {
    CMD_START = 0x01u,
    CMD_REFRESH = 0x03u,
    CMD_EXIT = 0x05u,
    CMD_INPUT = 0x07u,
    CMD_PAGE_CLOSE = 0x0eu,
    CMD_PAGE_STARTUP = 0x0fu,
    CMD_EXIT_ALT = 0x10u,
};
enum {
    INPUT_DOUBLE_CLICK = 1u,
    INPUT_LONG_PRESS = 3u,
    INPUT_IMU_LOOKUP = 6u,
};
#define APP_ID_TERMINAL 0x30u
#define APP_ID_DASHBOARD 1u
#define APP_ID_MENU 3u
#define START_UP_APP_MENU 3u /* SID_UI_FOREGROUND_MEUN_ID */

extern void *audio_uart_master_schedule_queue;          /* RAM 0x200749d0 */
extern void *g2_uart_send_queue;                         /* RAM 0x200749cc */
extern void *g2_uart_thread_event;                       /* RAM 0x20074b10 */
extern void *g2_disp_start_blocking_mutex;               /* RAM 0x200749e0 */
extern void *g2_disp_start_blocking_timer;               /* RAM 0x200749dc */
extern volatile uint16_t g2_disp_start_blocking_flag;    /* RAM 0x20074f48 */
extern volatile uint8_t g2_sync_system_disp_status;      /* RAM 0x20075023 */
extern volatile uint32_t g2_sync_schedule_startup_word;  /* RAM 0x200749e8, cleared on startup */
extern volatile uint32_t audio_uart_display_audio_flag_cell; /* RAM 0x200749e4, global input closed */

extern void initGlobalVariableMutex_45ba46(uint32_t unused);
extern uint8_t imu_startup_enable_get_45ba3c(void);
extern void DispStartBlocking_TimerCb_45bc06(void *argument);
extern void audio_uart_display_audio_acquire_45baf0(void);   /* lockGlobalVariable */
extern void audio_uart_display_audio_release_45bb58(void);   /* unlockGlobalVariable */
extern void audio_uart_display_audio_finalize(void);         /* 0x45bbd2 */
extern uint32_t audio_uart_display_audio_terminal_mode_45bbf4(void);
extern uint32_t SVC_Settings_AppLaunchCheck(void);           /* 0x46b334 */
extern uint32_t display_input_gated_442d64(void);
/* Stock call site loads r2 = input event id; the callee reads r0/r1 only. */
extern uint32_t getStartUpAppID_442ba8(uint8_t sys_status, uint32_t input_type,
                                       uint32_t event_id);
extern void sync_send_input_command_460424(uint8_t command);
extern void audio_uart_master_display_start(uint32_t id, const void *payload,
                                            uint16_t length, uint32_t extra); /* 0x464b2e */
extern void file_heap_free(void *);
extern void *osMutexNew(const void *attr);
extern void *osTimerNew(void (*func)(void *), uint32_t type, void *argument, const void *attr);
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout);
extern int32_t osMessageQueuePut(void *queue, const void *msg, uint8_t prio, uint32_t timeout);
extern uint32_t osEventFlagsSet(void *ef_id, uint32_t flags);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "sync.module.framework"; /* ROM 0x77c07c */
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"; /* ROM 0x705fb8 */
static const char function_name[] = "_SyncScheduleManagerThreadHandler"; /* ROM 0x75a680 */
static const char mutex_name[] = "DispStartBlkMutex"; /* ROM 0x783b7c */

static const g2_os_mutex_attr_t disp_start_mutex_attr = { /* ROM 0x7895f0 */
    mutex_name, 2u, NULL, 0u};

static const char e_mutex_failed[] = "create DispStartBlocking mutex failed."; /* ROM 0x74eb64 */
static const char c_mutex_failed[] =
    "[sync.module.framework]create DispStartBlocking mutex failed."; /* ROM 0x70f6a4 */
static const char e_timer_failed[] = "create DispStartBlocking timer failed."; /* ROM 0x74eb8c */
static const char c_timer_failed[] =
    "[sync.module.framework]create DispStartBlocking timer failed."; /* ROM 0x70f6e4 */
static const char e_null_data[] = "schedule manager received null data, ignore it..."; /* ROM 0x72e0e8 */
static const char c_null_data[] =
    "[sync.module.framework]schedule manager received null data, ignore it..."; /* ROM 0x6f6660 */
static const char e_packet_ptr[] = "_pSyncPacketStruct = %p"; /* ROM 0x77c10c */
static const char c_packet_ptr[] =
    "[sync.module.framework]_pSyncPacketStruct = %p"; /* ROM 0x738d44 */
static const char e_event_type[] = "SyncEventType = %d"; /* ROM 0x783be0 */
static const char c_event_type[] = "[sync.module.framework]SyncEventType = %d"; /* ROM 0x743f94 */
static const char e_length[] = "len = %d"; /* ROM 0x78c4b8 */
static const char c_length[] = "[sync.module.framework]len = %d"; /* ROM 0x7657f0 */
static const char e_packet_cmd[] = "packet cmd = %d"; /* ROM 0x7895c0 */
static const char c_packet_cmd[] = "[sync.module.framework]packet cmd = %d"; /* ROM 0x74ebb4 */
static const char e_terminal_app[] = "terminal mode,drop it,app id = %d"; /* ROM 0x75a6a4 */
static const char c_terminal_app[] =
    "[sync.module.framework]terminal mode,drop it,app id = %d"; /* ROM 0x719030 */
static const char e_put_failed[] = "send msg to g_syncScheduleMgr_queue failed,errno = %d"; /* ROM 0x723700 */
static const char c_put_failed[] =
    "[sync.module.framework]send msg to g_syncScheduleMgr_queue failed,errno = %d"; /* ROM 0x6efdb8 */
static const char e_startup_done[] = "schedule manager processing data done,exec display startup"; /* ROM 0x71906c */
static const char c_startup_done[] =
    "[sync.module.framework]schedule manager processing data done,exec display startup"; /* ROM 0x6ea180 */
static const char e_launch_failed[] = "app launch check failed,drop it"; /* ROM 0x765810 */
static const char c_launch_failed[] =
    "[sync.module.framework]app launch check failed,drop it"; /* ROM 0x723738 */
static const char e_blocking_set[] = "display start blocking flag is 1"; /* ROM 0x75a6c8 */
static const char c_blocking_set[] =
    "[sync.module.framework]display start blocking flag is 1"; /* ROM 0x723770 */
static const char e_double_click[] = "received touch bar double click event"; /* ROM 0x74ebdc */
static const char c_double_click[] =
    "[sync.module.framework]received touch bar double click event"; /* ROM 0x70f724 */
static const char e_terminal_input[] = "terminal mode,drop it,input event id = %d"; /* ROM 0x743fc0 */
static const char c_terminal_input[] =
    "[sync.module.framework]terminal mode,drop it,input event id = %d"; /* ROM 0x7061d8 */
static const char e_imu_lookup[] = "received imu sensor lookup event"; /* ROM 0x75a6ec */
static const char c_imu_lookup[] =
    "[sync.module.framework]received imu sensor lookup event"; /* ROM 0x7237a8 */
static const char e_imu_dashboard[] = "imu startup enable,start up dashboard app"; /* ROM 0x743fec */
static const char c_imu_dashboard[] =
    "[sync.module.framework]imu startup enable,start up dashboard app"; /* ROM 0x70621c */
static const char e_onboarding[] = "onboarding is running,drop it"; /* ROM 0x765830 */
static const char c_onboarding[] =
    "[sync.module.framework]onboarding is running,drop it"; /* ROM 0x7237e0 */
static const char e_long_press[] = "received touch bar long press event"; /* ROM 0x75a710 */
static const char c_long_press[] =
    "[sync.module.framework]received touch bar long press event"; /* ROM 0x7190a8 */
static const char e_startup_app[] = "startUpAppID = %d"; /* ROM 0x783bf4 */
static const char c_startup_app[] = "[sync.module.framework]startUpAppID = %d"; /* ROM 0x744018 */
static const char e_startup_zero[] = "startUpAppID is 0,drop it"; /* ROM 0x7726dc */
static const char c_startup_zero[] =
    "[sync.module.framework]startUpAppID is 0,drop it"; /* ROM 0x72e11c */
static const char e_startup_menu[] = "startUpAppID is SID_UI_FOREGROUND_MEUN_ID,start menu"; /* ROM 0x723818 */
static const char c_startup_menu[] =
    "[sync.module.framework]startUpAppID is SID_UI_FOREGROUND_MEUN_ID,start menu"; /* ROM 0x6f66ac */
static const char e_startup_invalid[] = "startUpAppID is invalid = %d"; /* ROM 0x765850 */
static const char c_startup_invalid[] =
    "[sync.module.framework]startUpAppID is invalid = %d"; /* ROM 0x72e150 */
static const char e_idle_input_only[] = "idle only support touch bar double click event"; /* ROM 0x738d74 */
static const char c_idle_input_only[] =
    "[sync.module.framework]idle only support touch bar double click event"; /* ROM 0x6fd544 */
static const char e_page_startup[] = "received page manager startup info to sync schedule manager command"; /* ROM 0x706260 */
static const char c_page_startup[] =
    "[sync.module.framework]received page manager startup info to sync schedule manager command"; /* ROM 0x6e1a4c */
static const char e_idle_unsupported[] = "idle status unsupport command = %d"; /* ROM 0x75a734 */
static const char c_idle_unsupported[] =
    "[sync.module.framework]idle status unsupport command = %d"; /* ROM 0x7190e4 */
static const char e_start_app[] = "start app id = %d"; /* ROM 0x783c08 */
static const char c_start_app[] = "[sync.module.framework]start app id = %d"; /* ROM 0x744044 */
static const char e_same_app[] = "received same app id = %d,drop it"; /* ROM 0x75a758 */
static const char c_same_app[] =
    "[sync.module.framework]received same app id = %d,drop it"; /* ROM 0x719120 */
static const char e_restart[] = "send reStart command to both, app id = %d"; /* ROM 0x744070 */
static const char c_restart[] =
    "[sync.module.framework]send reStart command to both, app id = %d"; /* ROM 0x7062a4 */
static const char e_refresh_done[] = "schedule manager processing Reflash command done"; /* ROM 0x72e184 */
static const char c_refresh_done[] =
    "[sync.module.framework]schedule manager processing Reflash command done"; /* ROM 0x6fd58c */
static const char e_exit_cmd[] = "received display sync exit command,app id = %d"; /* ROM 0x738da4 */
static const char c_exit_cmd[] =
    "[sync.module.framework]received display sync exit command,app id = %d"; /* ROM 0x6fd5d4 */
static const char e_exit_error[] = "!!! received error display sync exit command,app id = %d"; /* ROM 0x71915c */
static const char c_exit_error[] =
    "[sync.module.framework]!!! received error display sync exit command,app id = %d"; /* ROM 0x6efe08 */
static const char e_exit_done[] = "schedule manager processing exit command done"; /* ROM 0x738dd4 */
static const char c_exit_done[] =
    "[sync.module.framework]schedule manager processing exit command done"; /* ROM 0x6fd61c */
static const char e_input_closed[] = "global input event is closed,drop it"; /* ROM 0x74ec04 */
static const char c_input_closed[] =
    "[sync.module.framework]global input event is closed,drop it"; /* ROM 0x719198 */
static const char e_data_done[] = "schedule manager processing data done"; /* ROM 0x74ec2c */
static const char c_data_done[] =
    "[sync.module.framework]schedule manager processing data done"; /* ROM 0x70f764 */
static const char e_page_close[] = "received page manager close info to sync schedule manager command"; /* ROM 0x7062e8 */
static const char c_page_close[] =
    "[sync.module.framework]received page manager close info to sync schedule manager command"; /* ROM 0x6e1aa8 */
static const char e_status_invalid[] = "system disp status is invalid"; /* ROM 0x765870 */
static const char c_status_invalid[] =
    "[sync.module.framework]system disp status is invalid"; /* ROM 0x723850 */

static void log0(uint8_t level, uint32_t line, const char *e, const char *c)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, function_name, line, e);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, c, c);
}

static void log1(uint8_t level, uint32_t line, const char *e, const char *c, uint32_t value)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, function_name, line, e, value);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x400000u, c, c, value);
}

static void packet_free(sync_packet_t *packet)
{
    file_heap_free(packet->payload);
    file_heap_free(packet);
}

/* Queue the (retagged) packet for the UART sync thread; frees it on failure. */
static int32_t forward(sync_packet_t **packet, uint32_t line)
{
    int32_t status = osMessageQueuePut(g2_uart_send_queue, packet, 0u, 2000u);
    if (status != 0) {
        log1(2u, line, e_put_failed, c_put_failed, (uint32_t)status);
        packet_free(*packet);
        return status;
    }
    (void)osEventFlagsSet(g2_uart_thread_event, 2u);
    return 0;
}

/* Stock 0x45C058 (_SyncScheduleManagerThreadHandler); thread entry passed to
 * osThreadNew by SyncScheduleManagerInit. */
void audio_uart_master_scheduler_thread(void *argument)
{
    (void)argument;
    uint16_t current_app = 0u; /* app id of the running display session */
    uint16_t pending = 0u;     /* restarts sent while an app is running */
    sync_packet_t *packet;

    initGlobalVariableMutex_45ba46(0u);
    if (g2_disp_start_blocking_mutex == NULL) {
        g2_disp_start_blocking_mutex = osMutexNew(&disp_start_mutex_attr);
        if (g2_disp_start_blocking_mutex == NULL)
            log0(1u, 0x307u, e_mutex_failed, c_mutex_failed);
    }
    if (g2_disp_start_blocking_timer == NULL) {
        g2_disp_start_blocking_timer = osTimerNew(DispStartBlocking_TimerCb_45bc06, 0u, NULL, NULL);
        if (g2_disp_start_blocking_timer == NULL)
            log0(1u, 0x30du, e_timer_failed, c_timer_failed);
    }

    for (;;) {
        packet = NULL;
        if (osMessageQueueGet(audio_uart_master_schedule_queue, &packet, NULL, UINT32_MAX) != 0)
            continue;
        log1(4u, 0x314u, e_packet_ptr, c_packet_ptr, (uint32_t)(uintptr_t)packet);
        if (packet == NULL) {
            log0(2u, 0x316u, e_null_data, c_null_data);
            continue;
        }
        log1(4u, 0x31bu, e_event_type, c_event_type, packet->type);
        log1(4u, 0x31cu, e_length, c_length, packet->size);
        for (int32_t i = 0; i < (int32_t)packet->size; i++) {
            /* per-byte dump compiled out in stock; the empty loop remains */
        }
        uint16_t command_word = (uint16_t)(packet->payload[0] | (packet->payload[1] << 8));
        log1(4u, 0x322u, e_packet_cmd, c_packet_cmd, command_word);
        uint8_t command = (uint8_t)(command_word >> 8);

        if (g2_sync_system_disp_status == 0u) {
            if (command == CMD_START) {
                if (SVC_Settings_AppLaunchCheck() == 1u && g2_disp_start_blocking_flag == 0u) {
                    packet->type = SYNC_TYPE_DISPLAY;
                    const sync_payload_t *payload = (const sync_payload_t *)packet->payload;
                    if (audio_uart_display_audio_terminal_mode_45bbf4() == 1u &&
                        payload->app_id != APP_ID_TERMINAL) {
                        log1(3u, 0x32cu, e_terminal_app, c_terminal_app, payload->app_id);
                        packet_free(packet);
                    } else if (forward(&packet, 0x333u) == 0) {
                        current_app = payload->app_id;
                        pending = 0u;
                        log0(3u, 0x33bu, e_startup_done, c_startup_done);
                        g2_sync_system_disp_status = 1u;
                        audio_uart_display_audio_finalize();
                        g2_sync_schedule_startup_word = 0u;
                    }
                } else {
                    log0(3u, 0x340u, e_launch_failed, c_launch_failed);
                    if (g2_disp_start_blocking_flag == 1u)
                        log0(3u, 0x342u, e_blocking_set, c_blocking_set);
                    packet_free(packet);
                }
            } else if (command == CMD_INPUT) {
                if (SVC_Settings_AppLaunchCheck() != 1u) {
                    log0(3u, 0x39au, e_launch_failed, c_launch_failed);
                    packet_free(packet);
                    continue;
                }
                packet->type = SYNC_TYPE_INPUT;
                const sync_payload_t *payload = (const sync_payload_t *)packet->payload;
                if (audio_uart_display_audio_terminal_mode_45bbf4() == 1u) {
                    if (payload->event == INPUT_DOUBLE_CLICK) {
                        log0(3u, 0x34eu, e_double_click, c_double_click);
                        packet_free(packet);
                        audio_uart_master_display_start(APP_ID_TERMINAL, NULL, 0u, 0u);
                        current_app = APP_ID_TERMINAL;
                        pending = 0u;
                    } else {
                        log1(3u, 0x356u, e_terminal_input, c_terminal_input, payload->event);
                        packet_free(packet);
                    }
                } else if (payload->event == INPUT_DOUBLE_CLICK) {
                    log0(3u, 0x35du, e_double_click, c_double_click);
                    packet_free(packet);
                    audio_uart_master_display_start(APP_ID_DASHBOARD, NULL, 0u, 0u);
                    current_app = APP_ID_DASHBOARD;
                    pending = 0u;
                } else if (payload->event == INPUT_IMU_LOOKUP) {
                    log0(4u, 0x365u, e_imu_lookup, c_imu_lookup);
                    packet_free(packet);
                    if (imu_startup_enable_get_45ba3c() > 0u) {
                        if (display_input_gated_442d64() == 0u) {
                            log0(4u, 0x36au, e_imu_dashboard, c_imu_dashboard);
                            audio_uart_master_display_start(APP_ID_DASHBOARD, NULL, 0u, 0u);
                            current_app = APP_ID_DASHBOARD;
                            pending = 0u;
                        } else {
                            log0(4u, 0x370u, e_onboarding, c_onboarding);
                        }
                    }
                } else if (payload->event == INPUT_LONG_PRESS) {
                    log0(4u, 0x376u, e_long_press, c_long_press);
                    uint16_t source_id = payload->app_id;
                    uint32_t event = payload->event;
                    packet_free(packet);
                    uint32_t app = getStartUpAppID_442ba8(0u, source_id, event);
                    log1(4u, 0x37cu, e_startup_app, c_startup_app, app);
                    if (app == 0u) {
                        log0(4u, 0x37fu, e_startup_zero, c_startup_zero);
                    } else if (app == START_UP_APP_MENU) {
                        log0(4u, 0x383u, e_startup_menu, c_startup_menu);
                        sync_send_input_command_460424(0x1eu);
                        current_app = APP_ID_DASHBOARD;
                        audio_uart_master_display_start(APP_ID_DASHBOARD, NULL, 0u, 0u);
                        audio_uart_master_display_start(APP_ID_MENU, NULL, 0u, 0u);
                        pending = 0u;
                    } else {
                        log1(2u, 0x38cu, e_startup_invalid, c_startup_invalid, app);
                    }
                } else {
                    packet_free(packet);
                    log0(4u, 0x396u, e_idle_input_only, c_idle_input_only);
                }
            } else if (command == CMD_PAGE_STARTUP) {
                log0(3u, 0x3a1u, e_page_startup, c_page_startup);
                g2_sync_system_disp_status = 1u;
                audio_uart_display_audio_finalize();
                current_app = (uint16_t)(packet->payload[2] | (packet->payload[3] << 8));
                pending = 0u;
                packet_free(packet);
                g2_sync_schedule_startup_word = 0u;
            } else {
                log1(2u, 0x3abu, e_idle_unsupported, c_idle_unsupported, command_word);
                packet_free(packet);
            }
        } else if (g2_sync_system_disp_status == 1u) {
            if (command == CMD_START) {
                packet->type = SYNC_TYPE_DISPLAY;
                const sync_payload_t *payload = (const sync_payload_t *)packet->payload;
                if (payload->app_id == current_app) {
                    log1(4u, 0x3b8u, e_start_app, c_start_app, current_app);
                    log1(4u, 0x3b9u, e_same_app, c_same_app, payload->app_id);
                    packet_free(packet);
                } else if (audio_uart_display_audio_terminal_mode_45bbf4() == 1u) {
                    log1(3u, 0x3bfu, e_terminal_app, c_terminal_app, payload->app_id);
                    packet_free(packet);
                } else {
                    int32_t status = osMessageQueuePut(g2_uart_send_queue, &packet, 0u, 2000u);
                    if (status != 0) {
                        log1(2u, 0x3c6u, e_put_failed, c_put_failed, (uint32_t)status);
                        packet_free(packet);
                    } else {
                        if (pending == 0u)
                            pending++;
                        (void)osEventFlagsSet(g2_uart_thread_event, 2u);
                        log1(4u, 0x3cfu, e_restart, c_restart, payload->app_id);
                    }
                }
            } else if (command == CMD_REFRESH) {
                packet->type = SYNC_TYPE_DISPLAY;
                if (forward(&packet, 0x3d5u) == 0)
                    log0(4u, 0x3dbu, e_refresh_done, c_refresh_done);
            } else if (command == CMD_EXIT || command == CMD_EXIT_ALT) {
                packet->type = SYNC_TYPE_DISPLAY;
                const sync_payload_t *payload = (const sync_payload_t *)packet->payload;
                if (forward(&packet, 0x3e1u) == 0) {
                    if (pending == 0u) {
                        log1(4u, 0x3e9u, e_exit_cmd, c_exit_cmd, payload->app_id);
                        if (current_app == payload->app_id || payload->app_id == 0u) {
                            g2_sync_system_disp_status = 0u;
                            current_app = 0u;
                        } else {
                            log1(2u, 0x3efu, e_exit_error, c_exit_error, payload->app_id);
                        }
                    }
                    if (pending != 0u)
                        pending--;
                    log0(4u, 0x3f6u, e_exit_done, c_exit_done);
                }
            } else if (command == CMD_INPUT) {
                packet->type = SYNC_TYPE_INPUT;
                audio_uart_display_audio_acquire_45baf0();
                uint32_t input_closed = audio_uart_display_audio_flag_cell;
                audio_uart_display_audio_release_45bb58();
                if (input_closed == 1u) {
                    log0(3u, 0x3ffu, e_input_closed, c_input_closed);
                    packet_free(packet);
                } else if (forward(&packet, 0x406u) == 0) {
                    log0(4u, 0x40cu, e_data_done, c_data_done);
                    g2_sync_system_disp_status = 1u;
                }
            } else if (command == CMD_PAGE_CLOSE) {
                log0(3u, 0x410u, e_page_close, c_page_close);
                packet_free(packet);
                g2_sync_system_disp_status = 0u;
                current_app = 0u;
            } else {
                packet_free(packet);
            }
        } else {
            if (packet->payload != NULL)
                file_heap_free(packet->payload);
            file_heap_free(packet);
            log0(1u, 0x425u, e_status_invalid, c_status_invalid);
        }
    }
}
