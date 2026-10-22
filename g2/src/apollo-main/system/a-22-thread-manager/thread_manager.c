/* Thread manager, stock D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_manager.c.
 * Native 0x4c94c8..0x4c9b85; literal pool 0x4c9c58..0x4c9d43.
 *
 * Already defined elsewhere (not repeated here): the stop fan-out 0x4c96b6
 * (audio_stop_fanout, audio/stop-handshake), thread_manager_sysstart_sync
 * 0x4c9b86, thread_manager_sysstart_sync_end 0x4c9be2 and the stop ack
 * 0x4c9c3c (drivers/peripherals/ring-task). The manager record at RAM
 * 0x200040d8 {kernel start, deinit, thread, ..., +0x1c event flags} is
 * defined in hal/uart/uart-thread.
 *
 * Thread-manager slots (bit n of the event-flags group is the sync/exit ack
 * of slot n): 1 notification 0x200040fc, 3 audio 0x20003f98, 4 input
 * 0x2000408c, 5 sensor hub 0x20003664, 6 ring 0x20004120, 7 BLE msg rx
 * 0x20003ffc, 8 BLE msg tx 0x20004020, 9 BLE WSF 0x20004068, 11 BLE
 * production 0x20004044, 12 display driver 0x20000658. The device manager
 * 0x2000060c is started but never synced. */
#include <stddef.h>
#include <stdint.h>

typedef struct {
    void (*init)(void);   /* +0x0 */
    void (*deinit)(void); /* +0x4 */
    void *thread;         /* +0x8 osThreadId_t */
    void *queue;          /* +0xc */
} g2_tm_thread_record_t;

typedef struct {
    void (*init)(void);   /* +0x00 thread_manager_kernel_start_4c9b48 */
    void (*deinit)(void); /* +0x04 thread_manager_deinit_4c9b70 */
    void *thread;         /* +0x08 "manager" thread */
    uint32_t reserved[4]; /* +0x0c */
    void *event_flags;    /* +0x1c sync/exit acknowledgements */
    uint32_t tail;        /* +0x20 */
} g2_tm_state_t;
_Static_assert(sizeof(g2_tm_state_t) == 36u, "thread manager record spans 0x200040d8..0x200040fb");

typedef struct {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority; uint32_t tz_module; uint32_t reserved;
} g2_tm_thread_attr_t;
_Static_assert(sizeof(g2_tm_thread_attr_t) == 36u, "osThreadAttr_t");

#define TM_THREAD_CB_SIZE   0x70u
#define TM_THREAD_STACK     0x4000u
#define TM_THREAD_PRIORITY  24u          /* osPriorityNormal */
#define TM_FLAG_EXIT        0x800000u    /* thread flag asking a managed thread to sync/exit */
#define TM_FLAGS_WAIT_ALL   1u           /* osFlagsWaitAll */
#define TM_EVENT_MASK       0x00ffffffu
#define TM_SYNC_TIMEOUT     20000u
#define TM_EXIT_TIMEOUT     5000u
#define TM_IDLE_PERIOD      60000u

/* Notification bits handled by the manager thread. */
#define SYS_MODE_POWEROFF   0x01u
#define SYS_MODE_REBOOT     0x02u
#define SYS_MODE_SHIPMODE   0x04u
#define SYS_MODE_LOWPOWER   0x08u
#define SYS_MODE_TEMP       0x10u
#define SYS_MODE_OTA        0x20u    /* also keeps the three BLE message threads alive */

extern g2_tm_state_t audio_uart_thread_manager_state;            /* RAM 0x200040d8 */
extern g2_tm_thread_record_t g2_notif_thread_context;            /* RAM 0x200040fc slot 1 */
extern g2_tm_thread_record_t g2_audio_dispatch_state;            /* RAM 0x20003f98 slot 3 */
extern g2_tm_thread_record_t g2_input_thread_desc;               /* RAM 0x2000408c slot 4 */
extern g2_tm_thread_record_t g2_hub_thread_desc;                 /* RAM 0x20003664 slot 5 */
extern g2_tm_thread_record_t audio_uart_ring_thread_manager;     /* RAM 0x20004120 slot 6 */
extern g2_tm_thread_record_t audio_ble_rx_thread_state;          /* RAM 0x20003ffc slot 7 */
extern g2_tm_thread_record_t audio_ble_msgtx_manager;            /* RAM 0x20004020 slot 8 */
extern g2_tm_thread_record_t audio_ble_wsf_thread_state;         /* RAM 0x20004068 slot 9 */
extern g2_tm_thread_record_t g2_ble_production_context;          /* RAM 0x20004044 slot 11 */
extern g2_tm_thread_record_t audio_display_driver_manager;       /* RAM 0x20000658 slot 12 */
extern g2_tm_thread_record_t audio_device_manager_state;         /* RAM 0x2000060c */
extern volatile uint8_t audio_ble_trace_level_cell;              /* RAM 0x2007502f, set once all threads synced */
extern volatile uint8_t g2_tm_ota_exit_started;                  /* RAM 0x20075030 */

uint32_t g2_thread_manager_cb[TM_THREAD_CB_SIZE / 4u];           /* RAM 0x200720d0 */
uint32_t g2_thread_manager_stack[TM_THREAD_STACK / 4u];          /* RAM 0x203322c4 */

extern int32_t osKernelInitialize(void);
extern int32_t osKernelStart(void);
extern uint32_t osKernelGetTickCount(void);
extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr);
extern void *osThreadGetId(void);
extern int32_t osThreadSetPriority(void *thread, int32_t priority);
extern int32_t osThreadTerminate(void *thread);
extern uint32_t osThreadFlagsSet(void *thread, uint32_t flags);
extern uint32_t osThreadFlagsWait(uint32_t flags, uint32_t options, uint32_t timeout);
extern void *osEventFlagsNew(const void *attr);
extern uint32_t osEventFlagsWait(void *ef, uint32_t flags, uint32_t options, uint32_t timeout);
extern uint32_t ulSetInterruptMask(void);
extern void compress_log_mutex_init(void);
extern void compress_log_set_output_flags_43d0c8(uint8_t flags);
extern uint64_t TPL_Init(uint8_t service, ...);
extern int32_t audio_ble_send_status_message(uint32_t, const uint8_t *, uint32_t, uint32_t); /* SendDataToBoth 0x464d1c */
extern int32_t Thread_MsgRxFromBle(uint32_t id, const void *bytes, uint32_t length); /* 0x48f12c */
extern void APP_BleEusSendDataMsg(void);        /* 0x4bdff4 */
extern void APP_BleEusDirectSendDataMsg(void);  /* 0x4be14e */
extern uint32_t DRV_Mx25u25643g_init_46fe38(void);
extern void SVC_FlashDBInit(void);
extern int littlefs_init_47627e(void);
extern void elog_async_ext_flieStore_Init(void); /* 0x448e48 */
extern void audio_event_loop_initialize(void);   /* fw_event_loop_initialize 0x4764e0 */
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument, uint32_t delay_ms);
extern void service_time_sync_callback(void);
extern void AT_CoreInit(void);
extern void tracepoint_defer_init_47e232(void);
extern void uart_shell_init_54171c(void);
extern int32_t uart_instance_init(void);
extern uint8_t productModeGet(void);
extern uint32_t audio_stop_fanout(uint32_t reason); /* 0x4c96b6 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void thread_manager_threads_init_4c953e(void);
void thread_manager_task_4c98c2(void *argument);
void thread_manager_thread_init_4c9b1a(void *argument);
void thread_task_exit_4c9778(uint32_t flags);
void thread_notify_event_handler_4c995e(uint32_t flags);

static const char module_tag[] = "task.manager"; /* ROM 0x789b10 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_manager.c"; /* ROM 0x6fe42c */
static const char thread_name[] = "manager"; /* ROM 0x78eb9c */
static const char fn_sync[] = "_thread_sync"; /* ROM 0x789b00 */
static const char sync_failed[] = "thread sync failed:0x%x, task:%d"; /* ROM 0x75bb98 */
static const char sync_failed_short[] = "[task.manager]thread sync failed:0x%x, task:%d"; /* ROM 0x739e84 */
static const char fn_exit[] = "_thread_task_exit"; /* ROM 0x7842fc */
static const char exit_start[] = "thread exit start:"; /* ROM 0x784310 */
static const char exit_start_short[] = "[task.manager]thread exit start:"; /* ROM 0x75bbbc */
static const char exit_sync[] = "thread sync exit:0x%x, 0x%x\r\n"; /* ROM 0x766ab0 */
static const char exit_sync_short[] = "[task.manager]thread sync exit:0x%x, 0x%x\r\n"; /* ROM 0x74548c */
static const char exit_failed[] = "thread sync exit failed:0x%x != 0x%x\r\n"; /* ROM 0x74feec */
static const char exit_failed_short[] = "[task.manager]thread sync exit failed:0x%x != 0x%x\r\n"; /* ROM 0x724998 */
static const char exit_end[] = "thread exit end."; /* ROM 0x784324 */
static const char exit_end_short[] = "[task.manager]thread exit end."; /* ROM 0x766ad0 */
static const char fn_manager[] = "_thread_manager"; /* ROM 0x789b20 */
static const char sw_version[] = "software version: V%s"; /* ROM 0x77cc64 */
static const char sw_version_short[] = "[task.manager]software version: V%s"; /* ROM 0x75bbe0 */
static const char version_string[] = "2.2.6.10"; /* ROM 0x78c674 */
static const char fn_notify[] = "_thread_notify_event_handler"; /* ROM 0x766af0 */
static const char mode_ota[] = "[sys] enter mode: ota"; /* ROM 0x77cc7c */
static const char mode_ota_short[] = "[task.manager][sys] enter mode: ota"; /* ROM 0x75bc04 */
static const char mode_poweroff[] = "[sys] enter mode: poweroff"; /* ROM 0x77370c */
static const char mode_poweroff_short[] = "[task.manager][sys] enter mode: poweroff"; /* ROM 0x7454b8 */
static const char mode_reboot[] = "[sys] enter mode: reboot"; /* ROM 0x773728 */
static const char mode_reboot_short[] = "[task.manager][sys] enter mode: reboot"; /* ROM 0x74ff14 */
static const char mode_shipmode[] = "[sys] enter mode: shipmode"; /* ROM 0x773744 */
static const char mode_shipmode_short[] = "[task.manager][sys] enter mode: shipmode"; /* ROM 0x7454e4 */
static const char mode_lowpower[] = "[sys] enter mode: lowpower"; /* ROM 0x773760 */
static const char mode_lowpower_short[] = "[task.manager][sys] enter mode: lowpower"; /* ROM 0x745510 */
static const char mode_temp[] = "[sys] enter mode: temp abnormal"; /* ROM 0x766b10 */
static const char mode_temp_short[] = "[task.manager][sys] enter mode: temp abnormal"; /* ROM 0x739eb4 */

static const g2_tm_thread_attr_t thread_manager_attr = { /* ROM 0x75b814 */
    thread_name, 0u, g2_thread_manager_cb, TM_THREAD_CB_SIZE,
    g2_thread_manager_stack, TM_THREAD_STACK, TM_THREAD_PRIORITY, 1u, 0u};

#define LOG_EXT(level, fn, line, ...) \
    do { if (audio_log_flags() & 2u) audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); } while (0)
#define LOG_ON() ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))

/* Unrecoverable start-up failure: mask interrupts and fault on a write to
 * 0xffffffff. */
static void thread_manager_fatal(void)
{
    (void)ulSetInterruptMask();
    *(volatile uint32_t *)0xffffffffu = 0u;
    for (;;) {
    }
}

/* Resource init: log mutex, ack event-flags group and the transport layer. */
void thread_manager_resource_init_4c94c8(void)
{
    compress_log_mutex_init();
    audio_uart_thread_manager_state.event_flags = osEventFlagsNew(NULL);
    if (audio_uart_thread_manager_state.event_flags == NULL)
        thread_manager_fatal();
    (void)TPL_Init(0u, audio_ble_send_status_message, Thread_MsgRxFromBle, APP_BleEusSendDataMsg,
                   APP_BleEusDirectSendDataMsg);
}

/* Storage bring-up: external flash, FlashDB, littlefs, crash-log file store. */
void thread_manager_storage_init_4c9508(void)
{
    (void)DRV_Mx25u25643g_init_46fe38();
    SVC_FlashDBInit();
    (void)littlefs_init_47627e();
    elog_async_ext_flieStore_Init();
}

/* Service bring-up: event loop, managed threads, delayed time sync, AT core. */
void thread_manager_service_init_4c951c(void)
{
    audio_event_loop_initialize();
    thread_manager_threads_init_4c953e();
    fw_event_loop_push_delayed(service_time_sync_callback, 0u, 10000u);
    AT_CoreInit();
    tracepoint_defer_init_47e232();
}

/* Create every managed thread at low priority, then restore normal. */
void thread_manager_threads_init_4c953e(void)
{
    (void)osThreadSetPriority(osThreadGetId(), 8);
    uart_shell_init_54171c();
    (void)uart_instance_init();
    if (productModeGet() == 1u)
        compress_log_set_output_flags_43d0c8(3u);
    g2_audio_dispatch_state.init();
    g2_input_thread_desc.init();
    g2_hub_thread_desc.init();
    audio_device_manager_state.init();
    audio_uart_ring_thread_manager.init();
    g2_ble_production_context.init();
    audio_ble_rx_thread_state.init();
    audio_ble_msgtx_manager.init();
    audio_ble_wsf_thread_state.init();
    g2_notif_thread_context.init();
    (void)osThreadSetPriority(osThreadGetId(), TM_THREAD_PRIORITY);
}

/* _thread_sync: release one thread and wait up to 20 s for its ack bit. */
void thread_sync_4c95bc(void *thread, uint8_t index)
{
    uint32_t mask = index < 32u ? 1u << index : 0u;
    uint32_t flags;
    (void)osThreadFlagsSet(thread, TM_FLAG_EXIT);
    flags = osEventFlagsWait(audio_uart_thread_manager_state.event_flags, mask, TM_FLAGS_WAIT_ALL, TM_SYNC_TIMEOUT);
    if ((mask & flags) != mask) {
        LOG_EXT(1u, fn_sync, 0xb1u, sync_failed, flags, index);
        if (LOG_ON())
            (void)compress_log_output(0x04800000u, sync_failed_short, sync_failed_short, flags, index);
    }
}

/* Start-up handshake with each managed thread in a fixed order. */
void thread_manager_sync_all_4c963a(void)
{
    thread_sync_4c95bc(g2_notif_thread_context.thread, 1u);
    thread_sync_4c95bc(audio_uart_ring_thread_manager.thread, 6u);
    thread_sync_4c95bc(g2_ble_production_context.thread, 11u);
    thread_sync_4c95bc(audio_ble_rx_thread_state.thread, 7u);
    thread_sync_4c95bc(audio_ble_msgtx_manager.thread, 8u);
    thread_sync_4c95bc(g2_audio_dispatch_state.thread, 3u);
    thread_sync_4c95bc(g2_input_thread_desc.thread, 4u);
    thread_sync_4c95bc(audio_ble_wsf_thread_state.thread, 9u);
    thread_sync_4c95bc(g2_hub_thread_desc.thread, 5u);
    thread_sync_4c95bc(audio_display_driver_manager.thread, 12u);
}

/* _thread_task_exit: ask the managed threads to exit and wait 5 s for all
 * of their ack bits. */
void thread_task_exit_4c9778(uint32_t flags)
{
    uint32_t want;
    uint32_t got;
    LOG_EXT(3u, fn_exit, 0xffu, exit_start);
    if (LOG_ON())
        (void)compress_log_output(0x0c000000u, exit_start_short, exit_start_short);
    want = audio_stop_fanout(flags);
    got = osEventFlagsWait(audio_uart_thread_manager_state.event_flags, want, TM_FLAGS_WAIT_ALL, TM_EXIT_TIMEOUT);
    LOG_EXT(3u, fn_exit, 0x103u, exit_sync, got, want);
    if (LOG_ON())
        (void)compress_log_output(0x0c800000u, exit_sync_short, exit_sync_short, got, want);
    if (got != want) {
        LOG_EXT(1u, fn_exit, 0x106u, exit_failed, got, want);
        if (LOG_ON())
            (void)compress_log_output(0x04800000u, exit_failed_short, exit_failed_short, got, want);
    }
    LOG_EXT(3u, fn_exit, 0x109u, exit_end);
    if (LOG_ON())
        (void)compress_log_output(0x0c000000u, exit_end_short, exit_end_short);
}

/* _thread_manager: bring the system up, then serve mode notifications. */
void thread_manager_task_4c98c2(void *argument)
{
    uint32_t last = 0u;
    (void)argument;
    thread_manager_resource_init_4c94c8();
    thread_manager_storage_init_4c9508();
    thread_manager_service_init_4c951c();
    thread_manager_sync_all_4c963a();
    audio_ble_trace_level_cell = 1u;
    LOG_EXT(3u, fn_manager, 0x123u, sw_version, version_string);
    if (LOG_ON())
        (void)compress_log_output(0x0c400000u, sw_version_short, sw_version_short, version_string);
    for (;;) {
        uint32_t flags = osThreadFlagsWait(TM_EVENT_MASK, 0u, TM_IDLE_PERIOD);
        uint32_t now = osKernelGetTickCount();
        if (flags != 0u && flags < 0x80000000u) {
            thread_notify_event_handler_4c995e(flags);
            continue;
        }
        if (now - last >= TM_IDLE_PERIOD)
            last = now;
    }
}

/* _thread_notify_event_handler: OTA exits the threads once; every other
 * system mode runs the exit sequence each time it is signalled. */
void thread_notify_event_handler_4c995e(uint32_t flags)
{
    if (flags & SYS_MODE_OTA) {
        LOG_EXT(3u, fn_notify, 0x13cu, mode_ota);
        if (LOG_ON())
            (void)compress_log_output(0x0c000000u, mode_ota_short, mode_ota_short);
        if (g2_tm_ota_exit_started == 0u) {
            g2_tm_ota_exit_started = 1u;
            thread_task_exit_4c9778(flags);
        }
    }
    if (flags & SYS_MODE_POWEROFF) {
        LOG_EXT(4u, fn_notify, 0x146u, mode_poweroff);
        if (LOG_ON())
            (void)compress_log_output(0x10000000u, mode_poweroff_short, mode_poweroff_short);
        thread_task_exit_4c9778(flags);
    }
    if (flags & SYS_MODE_REBOOT) {
        LOG_EXT(4u, fn_notify, 0x14eu, mode_reboot);
        if (LOG_ON())
            (void)compress_log_output(0x10000000u, mode_reboot_short, mode_reboot_short);
        thread_task_exit_4c9778(flags);
    }
    if (flags & SYS_MODE_SHIPMODE) {
        LOG_EXT(4u, fn_notify, 0x156u, mode_shipmode);
        if (LOG_ON())
            (void)compress_log_output(0x10000000u, mode_shipmode_short, mode_shipmode_short);
        thread_task_exit_4c9778(flags);
    }
    if (flags & SYS_MODE_LOWPOWER) {
        LOG_EXT(4u, fn_notify, 0x15du, mode_lowpower);
        if (LOG_ON())
            (void)compress_log_output(0x10000000u, mode_lowpower_short, mode_lowpower_short);
        thread_task_exit_4c9778(flags);
    }
    if (flags & SYS_MODE_TEMP) {
        LOG_EXT(4u, fn_notify, 0x164u, mode_temp);
        if (LOG_ON())
            (void)compress_log_output(0x10000000u, mode_temp_short, mode_temp_short);
        thread_task_exit_4c9778(flags);
    }
}

/* Boot thread: create the "manager" thread, then delete itself. */
void thread_manager_thread_init_4c9b1a(void *argument)
{
    (void)argument;
    audio_uart_thread_manager_state.thread = osThreadNew(thread_manager_task_4c98c2, NULL, &thread_manager_attr);
    if (audio_uart_thread_manager_state.thread == NULL)
        thread_manager_fatal();
    (void)osThreadTerminate(osThreadGetId());
}

/* Record init hook: initialise the kernel, create the boot thread, start. */
void thread_manager_kernel_start_4c9b48(void)
{
    (void)osKernelInitialize();
    if (osThreadNew(thread_manager_thread_init_4c9b1a, NULL, NULL) == NULL)
        thread_manager_fatal();
    (void)osKernelStart();
}

/* Record deinit hook. */
void thread_manager_deinit_4c9b70(void)
{
    if (audio_uart_thread_manager_state.thread != NULL) {
        (void)osThreadTerminate(audio_uart_thread_manager_state.thread);
        audio_uart_thread_manager_state.thread = NULL;
    }
}
