/* Device manager thread, stock D:\01_workspace\s200_ap510b_iar_git\platform\device_mgr\device_mgr.c.
 * Native 0x4c6240..0x4c6bf3; literal pool 0x4c6bf4..0x4c6d03.
 *
 * Already defined elsewhere (not repeated here): DEV_ResourceInit 0x4c632c
 * (app/device-resource), DEV_SendMessage 0x4c659a (ble/ble-device) and the
 * 1 s timer callback 0x4c661c that posts message 2. The thread record at RAM
 * 0x2000060c {DEV_ThreadInit, DEV_ThreadDeinit, thread, queue} is defined in
 * app/device-manager.
 *
 * Message ids (dispatch table ROM 0x7490c4): 1 box UART data
 * (DEV_BoxRevcMsgProcess 0x53a0b6), 2 one-second charge-cycle poll
 * (0x4c6638), 3 box-detect event (DEV_BoxDetectMsgProcess 0x4ac278),
 * 4 ring battery report (0x4c66f0), 5 reserved (NULL handler). */
#include <stddef.h>
#include <stdint.h>

/* Device-manager queue item (8 bytes, osMessageQueueNew(50, 8)). */
typedef struct {
    uint16_t id;     /* +0 */
    uint16_t length; /* +2 */
    union {
        const uint8_t *data; /* +4 box UART payload */
        uint8_t bytes[4];    /* +4 inline payload (ring battery: level, charging) */
    } u;
} g2_dev_msg_t;
_Static_assert(sizeof(g2_dev_msg_t) == 8u, "device-manager message is 8 bytes");

typedef void (*g2_dev_msg_handler_t)(const g2_dev_msg_t *msg);

typedef struct {
    uint16_t id;                  /* +0 */
    g2_dev_msg_handler_t handler; /* +4 */
} g2_dev_msg_route_t;
_Static_assert(sizeof(g2_dev_msg_route_t) == 8u, "dispatch row is 8 bytes");

/* Thread-manager record shared by every managed thread. */
typedef struct {
    void (*init)(void);   /* +0x0 */
    void (*deinit)(void); /* +0x4 */
    void *thread;         /* +0x8 osThreadId_t */
    void *queue;          /* +0xc osMessageQueueId_t */
} g2_dev_thread_record_t;

/* Charger telemetry record (see g2_bq27427.h); +0x14 is the "full" flag
 * maintained by DEV_CheckBatFull below. */
typedef struct {
    uint32_t charge_status; /* +0x00 */
    int32_t soc;            /* +0x04 % */
    int32_t voltage_mv;     /* +0x08 */
    int32_t current_ma;     /* +0x0c signed, negative = discharging */
    int32_t temperature;    /* +0x10 */
    uint8_t battery_full;   /* +0x14 */
} g2_dev_charger_telemetry_t;

/* am_hal_rtc_time_t word layout as filled by service_time_current_calendar_get. */
typedef struct {
    uint32_t read_error, weekday, century, year, month, day, hour, minute, second, hundredths;
} g2_dev_calendar_t;
_Static_assert(sizeof(g2_dev_calendar_t) == 40u, "calendar is 40 bytes");

typedef struct {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority; uint32_t tz_module; uint32_t reserved;
} g2_dev_thread_attr_t;
_Static_assert(sizeof(g2_dev_thread_attr_t) == 36u, "osThreadAttr_t");

#define DEV_MSG_ROUTES       5u
#define DEV_THREAD_CB_SIZE   0x70u
#define DEV_THREAD_STACK     0x2000u
#define DEV_THREAD_PRIORITY  37u      /* osPriorityAboveNormal5 */
#define NPMX_SUCCESS         0x2bad0000u
#define BOARD_CHARGER_NPM1300 1u
#define BOARD_CHARGER_BQ25180 2u
#define DEV_STATUS_PIN       7u

extern g2_dev_thread_record_t audio_device_manager_state;        /* RAM 0x2000060c */
extern g2_dev_charger_telemetry_t g2_charger_telemetry;          /* RAM 0x20073b18 */
extern uint8_t display_driver_ratio_cells_20003994[0xac];        /* RAM 0x20003994 nvSysDt */
extern struct npmx_instance g2_npmx_instance;                    /* RAM 0x20070f78 */
extern volatile uint8_t g2_pdm_production_bypass;                /* RAM 0x20075019, aging/production test active */
extern volatile uint8_t g2_dev_box_ota_mode;                     /* RAM 0x20075009 g_is_box_ota_mode */
extern volatile uint8_t g2_dev_status_pin_inhibit;               /* RAM 0x2007500a */
extern volatile uint32_t g2_dev_box_ota_start_s;                 /* RAM 0x200748ec, seconds */
extern volatile uint8_t g2_dev_shipmode_pending;                 /* RAM 0x20075003 */
extern volatile uint8_t g2_dev_aging_alert_on;                   /* RAM 0x20004545 */

uint32_t g2_device_mgr_thread_cb[DEV_THREAD_CB_SIZE / 4u];       /* RAM 0x20071f10 */
uint32_t g2_device_mgr_thread_stack[DEV_THREAD_STACK / 4u];      /* RAM 0x200e79b4 */
volatile uint32_t g2_dev_queue_get_errors;                       /* RAM 0x200744c4 */
volatile uint16_t g2_dev_shipmode_ticks;                         /* RAM 0x20074f1e */
volatile uint16_t g2_dev_poll_ticks;                             /* RAM 0x20074f20 */
volatile uint16_t g2_dev_batinfo_log_ticks;                      /* RAM 0x20074f22 */
volatile uint16_t g2_dev_aging_alert_ticks;                      /* RAM 0x20074f24 */
volatile uint16_t g2_dev_aging_record_ticks;                     /* RAM 0x20074f26 */
volatile uint16_t g2_dev_aging_soc10_ticks;                      /* RAM 0x20074f28 */
volatile uint16_t g2_dev_bat_full_ticks;                         /* RAM 0x20074f2a */
volatile uint8_t g2_dev_aging_soc10_recorded;                    /* RAM 0x20074fb0 */
volatile uint8_t g2_dev_status_pin_level;                        /* RAM 0x20074fb1 */

extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr);
extern int32_t osThreadTerminate(void *thread);
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout);
extern int32_t osDelay(uint32_t ticks);
extern uint32_t xTaskGetTickCount(void);
extern void watchdog_init(void);
extern void box_uart_init_53a09c(void);
extern void CHG_DeinitBatterySync(void);
extern void CHG_OnBatteryLevelChanged(void);
extern void svc_ring_battery_deinit_4ff8dc(void);
extern void SVC_RingBattery_Update(uint8_t level, uint8_t is_charging);
extern void BoxDetect_Deinit_4ac0f8(void);
extern void DEV_BoxRevcMsgProcess_53a0b6(const g2_dev_msg_t *msg);
extern void DEV_BoxDetectMsgProcess_4ac278(const g2_dev_msg_t *msg);
extern void audio_device_manager_resource_init_4c632c(void); /* DEV_ResourceInit 0x4c632c */
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t index); /* board config byte */
extern void check_fuel_gauge_init_51283c(void);
extern uint32_t npmx_interrupt_handler_510fe2(struct npmx_instance *p_pm);
extern void npmx_fuel_gauge_poll_5128a0(void);
extern int32_t npmx_enter_ship_mode_512a70(void);
extern int32_t DRV_Bq25180RefreshStatus(void);
extern int32_t bq27427_init_wrapper(void);
extern uint8_t productModeGet(void);
extern uint8_t box_detect_local_case_status_4ac75a(void);
extern uint32_t semantic_OtaTransferActive(void);
extern uint32_t g2_codec_pin_write(uint32_t pin, uint32_t value); /* 0x53a5be GPIO write */
extern uint32_t audio_log_wake_allowed(void);
extern uint32_t display_background_app_running_44349c(void);
extern uint32_t display_foreground_app_running_4434b4(void);
extern void audio_uart_master_display_stop(uint32_t, const void *, uint16_t, uint32_t); /* 0x464c36 */
extern void audio_ble_hci_radio_prepare_52f38c(void);
extern void aud_send_message_type0(uint32_t value);
extern void aud_send_message_type1(uint32_t value);
extern uint8_t audio_uart_device_role_get(void);
extern int32_t audio_uart_slave_display_refresh(uint32_t, const void *, uint32_t); /* 0x4442d0 */
extern void DRV_BuzzerPlay(uint8_t effect);
extern void service_time_current_calendar_get(g2_dev_calendar_t *calendar);
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern int32_t SVC_NvdbWriteSysData(uint8_t data_index, const void *value);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void device_mgr_fn_004c64c8(void *argument);
void device_mgr_fn_004c6510(const g2_dev_msg_t *msg);
void device_mgr_fn_004c6638(const g2_dev_msg_t *msg);
void device_mgr_fn_004c66f0(const g2_dev_msg_t *msg);
void device_mgr_fn_004c67a4(uint8_t level);
void device_mgr_fn_004c67dc(void);
void device_mgr_fn_004c6810(void);
void device_mgr_fn_004c691c(void);
void device_mgr_fn_004c674c(void);
void device_mgr_fn_004c6990(void);
void device_mgr_fn_004c69f4(void);
void device_mgr_fn_004c6a56(uint8_t on);
void device_mgr_fn_004c6a9e(void);
void device_mgr_fn_004c6ad8(void);

static const char module_tag[] = "device_mgr"; /* ROM 0x78a7f0, also the thread name */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\device_mgr\\device_mgr.c"; /* ROM 0x6f9c74 */
static const char fn_thread_init[] = "DEV_ThreadInit"; /* ROM 0x785a40 */
static const char thread_init_msg[] = "DEV_ThreadInit\n"; /* ROM 0x785a50 */
static const char thread_init_short[] = "[device_mgr]DEV_ThreadInit\n"; /* ROM 0x76ac78 */
static const char thread_fail[] = "[DEV_ThreadInit]osThreadNew fail"; /* ROM 0x753504 */
static const char thread_fail_short[] = "[device_mgr][DEV_ThreadInit]osThreadNew fail"; /* ROM 0x732f24 */
static const char thread_ok[] = "[DEV_ThreadInit]osThreadNew:0x%x, success"; /* ROM 0x73dbe4 */
static const char thread_ok_short[] = "[device_mgr][DEV_ThreadInit]osThreadNew:0x%x, success"; /* ROM 0x71db90 */
static const char fn_processer[] = "DEV_MessageProcesser"; /* ROM 0x7768d4 */
static const char bad_msg[] = "[DEV_MessageProcesser]Receive error message, id = [%d]"; /* ROM 0x71dc00 */
static const char bad_msg_short[] = "[device_mgr][DEV_MessageProcesser]Receive error message, id = [%d]"; /* ROM 0x701f70 */
static const char fn_ring_bat[] = "DEV_RingBatteryReportProcess"; /* ROM 0x75f2b0 */
static const char ring_bat_bad[] = "[DEV_RingBatteryReportProcess] invalid msg"; /* ROM 0x73dc3c */
static const char ring_bat_bad_short[] = "[device_mgr][DEV_RingBatteryReportProcess] invalid msg"; /* ROM 0x71dc38 */
static const char fn_bat_info[] = "DEV_CheckBatInfo"; /* ROM 0x77eca8 */
static const char npmx_fail[] = "npmx_interrupt_handler failed: %d\n"; /* ROM 0x75354c */
static const char npmx_fail_short[] = "[device_mgr]npmx_interrupt_handler failed: %d\n"; /* ROM 0x732fb4 */
static const char bat_info[] = "calculate_soc: %d, V: %d, I: %d, T: %d"; /* ROM 0x749074 */
static const char bat_info_short[] = "[device_mgr]calculate_soc: %d, V: %d, I: %d, T: %d"; /* ROM 0x7288c0 */
static const char fn_box_ota[] = "DEV_CheckBoxOtaTimeout"; /* ROM 0x7768ec */
static const char box_ota_timeout[] =
    "DEV_ChgCyclePoll: box OTA timeout (>3 minutes), force clear g_is_box_ota_mode"; /* ROM 0x6ecac8 */
static const char box_ota_timeout_short[] =
    "[device_mgr]DEV_ChgCyclePoll: box OTA timeout (>3 minutes), force clear g_is_box_ota_mode"; /* ROM 0x6dff58 */
static const char fn_aging[] = "DEV_AgingRecordSocTo10Time"; /* ROM 0x76ac94 */
static const char aging_flag[] = "aging_soc_to_10_record_flag: %d"; /* ROM 0x75f2d0 */
static const char aging_flag_short[] = "[device_mgr]aging_soc_to_10_record_flag: %d"; /* ROM 0x73dc68 */
static const char aging_time[] = "aging_soc_to_10_time: %d-%d-%d %d:%d:%d"; /* ROM 0x74909c */
static const char aging_time_short[] = "[device_mgr]aging_soc_to_10_time: %d-%d-%d %d:%d:%d"; /* ROM 0x7288f4 */

static const g2_dev_thread_attr_t device_mgr_thread_attr = { /* ROM 0x753570 */
    module_tag, 0u, g2_device_mgr_thread_cb, DEV_THREAD_CB_SIZE,
    g2_device_mgr_thread_stack, DEV_THREAD_STACK, DEV_THREAD_PRIORITY, 1u, 0u};

static const g2_dev_msg_route_t device_mgr_routes[DEV_MSG_ROUTES] = { /* ROM 0x7490c4 */
    {1u, DEV_BoxRevcMsgProcess_53a0b6},
    {2u, device_mgr_fn_004c6638},
    {3u, DEV_BoxDetectMsgProcess_4ac278},
    {4u, device_mgr_fn_004c66f0},
    {5u, NULL},
};

#define LOG_EXT(level, fn, line, ...) \
    do { if (audio_log_flags() & 2u) audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); } while (0)
#define LOG_ON() ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))

/* DEV_ThreadInit: record init hook, creates the device_mgr thread. */
void device_mgr_fn_004c6240(void)
{
    LOG_EXT(4u, fn_thread_init, 0x8bu, thread_init_msg);
    if (LOG_ON())
        (void)compress_log_output(0x10000000u, thread_init_short, thread_init_short);
    audio_device_manager_state.thread = osThreadNew(device_mgr_fn_004c64c8, NULL, &device_mgr_thread_attr);
    if (audio_device_manager_state.thread == NULL) {
        LOG_EXT(1u, fn_thread_init, 0x8fu, thread_fail);
        if (LOG_ON())
            (void)compress_log_output(0x04000000u, thread_fail_short, thread_fail_short);
    } else {
        LOG_EXT(4u, fn_thread_init, 0x93u, thread_ok, audio_device_manager_state.thread);
        if (LOG_ON())
            (void)compress_log_output(0x10400000u, thread_ok_short, thread_ok_short,
                                      audio_device_manager_state.thread);
    }
}

/* Late init run from the thread before the message loop. */
void device_mgr_fn_004c6498(void)
{
    watchdog_init();
    box_uart_init_53a09c();
}

/* DEV_ThreadDeinit: record deinit hook. */
void device_mgr_fn_004c64a4(void)
{
    CHG_DeinitBatterySync();
    svc_ring_battery_deinit_4ff8dc();
    BoxDetect_Deinit_4ac0f8();
    if (audio_device_manager_state.thread != NULL) {
        (void)osThreadTerminate(audio_device_manager_state.thread);
        audio_device_manager_state.thread = NULL;
    }
}

/* Thread entry: resource init, then drain the queue forever. */
void device_mgr_fn_004c64c8(void *argument)
{
    g2_dev_msg_t msg = {0};
    (void)argument;
    audio_device_manager_resource_init_4c632c();
    device_mgr_fn_004c6498();
    for (;;) {
        if (osMessageQueueGet(audio_device_manager_state.queue, &msg, NULL, UINT32_MAX) != 0)
            g2_dev_queue_get_errors++;
        else
            device_mgr_fn_004c6510(&msg);
        (void)osDelay(1u);
    }
}

/* DEV_MessageProcesser: first matching row with a handler wins. */
void device_mgr_fn_004c6510(const g2_dev_msg_t *msg)
{
    uint16_t id = msg->id;
    uint32_t i;
    for (i = 0u; i < DEV_MSG_ROUTES; i++) {
        if (id == device_mgr_routes[i].id && device_mgr_routes[i].handler != NULL) {
            device_mgr_routes[i].handler(msg);
            return;
        }
    }
    if (i == DEV_MSG_ROUTES) {
        LOG_EXT(1u, fn_processer, 0xf8u, bad_msg, id);
        if (LOG_ON())
            (void)compress_log_output(0x04400000u, bad_msg_short, bad_msg_short, id);
    }
}

/* DEV_ChgCyclePoll (message 2, posted by the 1 s timer). Counters advance in
 * DEV_PollTickCount; aging-test actions run every 2 s / 20 s, ship mode
 * fires 6 s after it was requested. */
void device_mgr_fn_004c6638(const g2_dev_msg_t *msg)
{
    const uint8_t *board = audio_ble_hci_radio_mode_state_50938e(0u);
    (void)msg;
    g2_dev_poll_ticks++;
    if (*board == BOARD_CHARGER_NPM1300)
        check_fuel_gauge_init_51283c();
    if (g2_dev_poll_ticks != 0u) {
        g2_dev_poll_ticks = 0u;
        device_mgr_fn_004c67dc();
        device_mgr_fn_004c6810();
        device_mgr_fn_004c691c();
        device_mgr_fn_004c674c();
        device_mgr_fn_004c6990();
        audio_ble_hci_radio_prepare_52f38c();
        device_mgr_fn_004c69f4();
    }
    if (g2_dev_aging_alert_ticks >= 2u && g2_pdm_production_bypass != 0u) {
        g2_dev_aging_alert_ticks = 0u;
        if (g2_dev_aging_alert_on == 0u)
            g2_dev_aging_alert_on = 1u;
        else
            g2_dev_aging_alert_on = 0u;
        device_mgr_fn_004c6a56(g2_dev_aging_alert_on);
    }
    if (g2_dev_aging_record_ticks >= 20u && g2_pdm_production_bypass != 0u) {
        g2_dev_aging_record_ticks = 0u;
        device_mgr_fn_004c6a9e();
        device_mgr_fn_004c6ad8();
    }
    if (g2_dev_shipmode_ticks >= 6u) {
        g2_dev_shipmode_pending = 0u;
        g2_dev_shipmode_ticks = 0u;
        if (*board == BOARD_CHARGER_NPM1300)
            (void)npmx_enter_ship_mode_512a70();
    }
}

/* DEV_RingBatteryReportProcess (message 4): payload {level, charging}. */
void device_mgr_fn_004c66f0(const g2_dev_msg_t *msg)
{
    if (msg == NULL || msg->length < 2u) {
        LOG_EXT(2u, fn_ring_bat, 0x151u, ring_bat_bad);
        if (LOG_ON())
            (void)compress_log_output(0x08000000u, ring_bat_bad_short, ring_bat_bad_short);
        return;
    }
    SVC_RingBattery_Update(msg->u.bytes[0], msg->u.bytes[1]);
}

/* Drive status pin 7 once the battery is above 3.3 V: high unless a box OTA,
 * case-local state, OTA transfer or inhibit flag is active (boards whose
 * config byte 1 is below 4 always drive it high). */
void device_mgr_fn_004c674c(void)
{
    if (g2_charger_telemetry.voltage_mv < 3301)
        return;
    if (*audio_ble_hci_radio_mode_state_50938e(1u) < 4u) {
        device_mgr_fn_004c67a4(1u);
    } else if (productModeGet() == 1u || g2_dev_box_ota_mode != 0u ||
               box_detect_local_case_status_4ac75a() == 1u || semantic_OtaTransferActive() != 0u ||
               g2_dev_status_pin_inhibit != 0u) {
        device_mgr_fn_004c67a4(0u);
    } else {
        device_mgr_fn_004c67a4(1u);
    }
}

/* Cached write of status pin 7. */
void device_mgr_fn_004c67a4(uint8_t level)
{
    if (level != 0u) {
        if (g2_dev_status_pin_level == 0u) {
            (void)g2_codec_pin_write(DEV_STATUS_PIN, 1u);
            g2_dev_status_pin_level = 1u;
        }
    } else if (g2_dev_status_pin_level != 0u) {
        (void)g2_codec_pin_write(DEV_STATUS_PIN, 0u);
        g2_dev_status_pin_level = 0u;
    }
}

/* Per-second counters for the aging test and pending ship mode. */
void device_mgr_fn_004c67dc(void)
{
    if (g2_pdm_production_bypass != 0u) {
        g2_dev_aging_alert_ticks++;
        g2_dev_aging_record_ticks++;
    }
    if (g2_dev_shipmode_pending != 0u)
        g2_dev_shipmode_ticks++;
}

/* DEV_CheckBatInfo: service the charger/gauge, notify level changes and log
 * the telemetry every 10 s. */
void device_mgr_fn_004c6810(void)
{
    const uint8_t *board = audio_ble_hci_radio_mode_state_50938e(0u);
    if (*board == BOARD_CHARGER_NPM1300) {
        uint32_t err = npmx_interrupt_handler_510fe2(&g2_npmx_instance);
        if (err != NPMX_SUCCESS) {
            LOG_EXT(1u, fn_bat_info, 0x195u, npmx_fail, err);
            if (LOG_ON())
                (void)compress_log_output(0x04400000u, npmx_fail_short, npmx_fail_short, err);
        }
        npmx_fuel_gauge_poll_5128a0();
    } else if (*board == BOARD_CHARGER_BQ25180) {
        (void)DRV_Bq25180RefreshStatus();
        (void)bq27427_init_wrapper();
    }
    if (productModeGet() != 1u)
        CHG_OnBatteryLevelChanged();
    g2_dev_batinfo_log_ticks++;
    if (g2_dev_batinfo_log_ticks >= 10u) {
        g2_dev_batinfo_log_ticks = 0u;
        LOG_EXT(3u, fn_bat_info, 0x1abu, bat_info, g2_charger_telemetry.soc,
                g2_charger_telemetry.voltage_mv, g2_charger_telemetry.current_ma,
                g2_charger_telemetry.temperature);
        if (LOG_ON())
            (void)compress_log_output(0x0d000000u, bat_info_short, bat_info_short,
                                      g2_charger_telemetry.soc, g2_charger_telemetry.voltage_mv,
                                      g2_charger_telemetry.current_ma, g2_charger_telemetry.temperature);
    }
}

/* DEV_CheckBoxOtaTimeout: clear box OTA mode after more than 180 s. */
void device_mgr_fn_004c691c(void)
{
    if (g2_dev_box_ota_mode == 0u || g2_dev_box_ota_start_s == 0u)
        return;
    if (xTaskGetTickCount() / 1000u - g2_dev_box_ota_start_s < 181u)
        return;
    LOG_EXT(1u, fn_box_ota, 0x1b8u, box_ota_timeout);
    if (LOG_ON())
        (void)compress_log_output(0x04000000u, box_ota_timeout_short, box_ota_timeout_short);
    g2_dev_box_ota_mode = 0u;
    g2_dev_box_ota_start_s = 0u;
}

/* Empty battery while not charging: stop the master display apps, then enter
 * nPM1300 ship mode. */
void device_mgr_fn_004c6990(void)
{
    const uint8_t *board = audio_ble_hci_radio_mode_state_50938e(0u);
    if (g2_charger_telemetry.soc >= 1 || g2_charger_telemetry.current_ma < 0)
        return;
    if (audio_log_wake_allowed() == 1u) {
        if (display_background_app_running_44349c() == 1u) {
            audio_uart_master_display_stop(0u, NULL, 0u, 0u);
            (void)osDelay(500u);
        }
        if (display_foreground_app_running_4434b4() == 1u) {
            audio_uart_master_display_stop(0u, NULL, 0u, 0u);
            (void)osDelay(500u);
        }
    }
    if (*board == BOARD_CHARGER_NPM1300)
        (void)npmx_enter_ship_mode_512a70();
}

/* Battery-full debounce: five consecutive seconds above the threshold
 * (product mode 1: SoC >= 80 % or >= 4300 mV; otherwise SoC >= 100 %). */
void device_mgr_fn_004c69f4(void)
{
    if (productModeGet() == 1u) {
        if (g2_charger_telemetry.soc < 80 && g2_charger_telemetry.voltage_mv < 4300)
            g2_dev_bat_full_ticks = 0u;
        else
            g2_dev_bat_full_ticks++;
    } else if (g2_charger_telemetry.soc < 100) {
        g2_dev_bat_full_ticks = 0u;
    } else {
        g2_dev_bat_full_ticks++;
    }
    if (g2_dev_bat_full_ticks >= 5u) {
        g2_dev_bat_full_ticks = 5u;
        g2_charger_telemetry.battery_full = 1u;
    } else {
        g2_charger_telemetry.battery_full = 0u;
    }
}

/* Aging-test alert toggle; reads the state byte, not the argument. */
void device_mgr_fn_004c6a56(uint8_t on)
{
    (void)on;
    if (g2_dev_aging_alert_on != 0u) {
        aud_send_message_type1(1u);
        if (audio_uart_device_role_get() == 2u)
            aud_send_message_type0(0u);
    } else {
        aud_send_message_type1(0u);
        if (audio_uart_device_role_get() == 2u)
            aud_send_message_type0(1u);
        (void)audio_uart_slave_display_refresh(0x104u, NULL, 0u);
        DRV_BuzzerPlay(0u);
    }
}

/* Record the current time as nvSysDt item 7 (+0x58); the first record also
 * seeds the SoC-to-10 timestamp (+0x80). */
void device_mgr_fn_004c6a9e(void)
{
    g2_dev_calendar_t now;
    service_time_current_calendar_get(&now);
    (void)audio_uart_display_area_copy_439c04(display_driver_ratio_cells_20003994 + 0x58u, &now, sizeof(now));
    if (g2_dev_aging_soc10_recorded == 0u)
        (void)audio_uart_display_area_copy_439c04(display_driver_ratio_cells_20003994 + 0x80u, &now, sizeof(now));
    (void)SVC_NvdbWriteSysData(7u, display_driver_ratio_cells_20003994 + 0x58u);
}

/* DEV_AgingRecordSocTo10Time: after three discharging samples (I < -19 mA)
 * latch the timestamp once and persist the telemetry as nvSysDt item 10. */
void device_mgr_fn_004c6ad8(void)
{
    if (g2_charger_telemetry.current_ma < -19 && g2_dev_aging_soc10_recorded == 0u) {
        g2_dev_aging_soc10_ticks++;
        if (g2_dev_aging_soc10_ticks >= 3u) {
            const g2_dev_calendar_t *rec;
            g2_dev_calendar_t now;
            g2_dev_aging_soc10_ticks = 0u;
            g2_dev_aging_soc10_recorded = 1u;
            LOG_EXT(2u, fn_aging, 0x235u, aging_flag, g2_dev_aging_soc10_recorded);
            if (LOG_ON())
                (void)compress_log_output(0x08400000u, aging_flag_short, aging_flag_short,
                                          g2_dev_aging_soc10_recorded);
            service_time_current_calendar_get(&now);
            (void)audio_uart_display_area_copy_439c04(display_driver_ratio_cells_20003994 + 0x80u, &now, sizeof(now));
            rec = (const g2_dev_calendar_t *)(const void *)(display_driver_ratio_cells_20003994 + 0x80u);
            LOG_EXT(2u, fn_aging, 0x239u, aging_time, rec->year, rec->month, rec->day, rec->hour,
                    rec->minute, rec->second);
            if (LOG_ON())
                (void)compress_log_output(0x09800000u, aging_time_short, aging_time_short, rec->year,
                                          rec->month, rec->day, rec->hour, rec->minute, rec->second);
            (void)SVC_NvdbWriteSysData(10u, &g2_charger_telemetry.soc);
        }
    } else if (g2_dev_aging_soc10_recorded == 0u) {
        g2_dev_aging_soc10_ticks = 0u;
    }
}
