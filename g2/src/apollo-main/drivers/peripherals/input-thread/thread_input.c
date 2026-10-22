/* Input thread, stock D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_input.c.
 * Native 0x512c84..0x5134b1 (input_msg_send_record 0x51301c and the four
 * senders 0x51308a/0x5130a6/0x5130c0 live in app/input-msg, case-in and
 * wear-child); literal pool 0x5134b4..0x51357b.
 *
 * Thread-manager slot 4. The descriptor (RAM 0x2000408c) and the five-row
 * message routing table (RAM 0x200040b0) are initialised data, read from the
 * SRAM init stream (record 0x75d3f4). The thread waits on CMSIS thread flags:
 * bit 22 drains the 30 x 12-byte message queue, bit 23 runs INP_ThreadExit.
 *
 * Message IDs (record word 0, compared as uint16) and their senders:
 *   0 touch event       sender 0x513056 (touch interrupt path)  -> gesture processor 0x502ef4
 *   1 buzzer play       sender 0x51308a (DRV_BuzzerPlay), param = effect -> DRV_BuzzerPlayAfterQueue
 *   2 buzzer next       sender 0x513070 (buzzer_timer_callback)  -> buzzer_play_next
 *   3 box in case       sender 0x5130a6 (box-detect service, PT cmd F3) -> INP_BoxDetectInCase
 *   4 terminal mode     sender 0x5130c0 (terminal_action_mode_sync), param = mode
 *                       -> INP_SetTerminalMode (mode 0: 1000 ms long press, else 500 ms) */
#include <stdint.h>
#include <stddef.h>
#include "g2_touch_cy8c4046.h"
#include "g2_buzzer.h"

/* Thread-manager descriptor; same 0x24-byte row as the sensor hub's. */
typedef struct {
    void (*init)(void);   /* +0x00 INP_ThreadInit */
    void (*deinit)(void); /* +0x04 thread_input_terminate */
    void *thread;         /* +0x08 osThreadId_t */
    void *queue;          /* +0x0c osMessageQueueId_t */
    uint32_t reserved[5]; /* +0x10 unused, zero */
} g2_thread_desc_t;
_Static_assert(sizeof(g2_thread_desc_t) == 0x24, "thread-manager descriptor stride");

typedef struct {
    uint32_t id;       /* +0x0 low 16 bits select the route */
    uint32_t reserved; /* +0x4 always 0 */
    uint32_t param;    /* +0x8 */
} g2_input_msg_t;
_Static_assert(sizeof(g2_input_msg_t) == 12, "input queue element size");

typedef void (*g2_input_handler_t)(const g2_input_msg_t *msg);
typedef struct {
    uint16_t id;                /* +0 */
    uint16_t pad;               /* +2 */
    g2_input_handler_t handler; /* +4 */
} g2_input_route_t;
_Static_assert(sizeof(g2_input_route_t) == 8, "stock route row");

typedef struct {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority;
    uint32_t tz_module; uint32_t reserved;
} g2_os_thread_attr_t;
_Static_assert(sizeof(g2_os_thread_attr_t) == 36, "osThreadAttr_t");

enum {
    INPUT_MSG_TOUCH_EVENT = 0u,
    INPUT_MSG_BUZZER_PLAY = 1u,
    INPUT_MSG_BUZZER_NEXT = 2u,
    INPUT_MSG_BOX_IN_CASE = 3u,
    INPUT_MSG_TERMINAL_MODE = 4u,
};
#define INPUT_ROUTE_COUNT 5u
#define INPUT_THREAD_SLOT 4u
#define INPUT_QUEUE_DEPTH 30u
#define INPUT_THREAD_CB_SIZE 0x70u
#define INPUT_THREAD_STACK_SIZE 0x1000u
#define INPUT_THREAD_PRIORITY 0x2eu /* osPriorityHigh6 */
#define INPUT_FLAG_QUEUE 0x00400000u
#define INPUT_FLAG_EXIT 0x00800000u
#define INPUT_FLAGS_ANY 0x00ffffffu
#define OS_WAIT_FOREVER 0xffffffffu
#define BUZZER_EFFECT_PIN_RESET 8u
#define LONG_PRESS_MS_DEFAULT 1000u
#define LONG_PRESS_MS_MODE 500u
#define TOUCH_CFG_SETTLE_MS 100u

extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr);
extern int32_t osThreadTerminate(void *thread);
extern uint32_t osThreadFlagsSet(void *thread, uint32_t flags);
extern uint32_t osThreadFlagsWait(uint32_t flags, uint32_t options, uint32_t timeout);
extern int32_t osDelay(uint32_t ticks);
extern void *osMessageQueueNew(uint32_t count, uint32_t size, const void *attr);
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout);
extern int32_t osMessageQueueDelete(void *queue);
extern void audio_input_message_send_record(const void *record); /* input_msg_send_record 0x51301c */
extern uint32_t audio_ble_hci_radio_identifier_480d72(uint8_t mode, void *output); /* 0x480d72 */
extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t slot);    /* thread manager: running */
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t slot); /* thread manager: idle */
extern void audio_uart_ring_sync_exit_4c9c3c(uint32_t slot);               /* thread manager: stop ack */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t value); /* 0x43c0e4 */
extern uint32_t audio_uart_ring_rtc_snapshot_4d3554(void *result); /* RSTGEN STAT bits, byte 2 = EXRSTAT */
extern void DRV_BuzzerPlay(uint8_t effect);           /* 0x502bf0, in g2/src as audio_wear_child_502bf0 */
extern void TouchUpdateFirmwareCheck(uint8_t force);  /* 0x56110c */
extern uint8_t productModeGet(void);                  /* 0x4abe60 */
extern uint32_t UX_GetSelfRingStatus(void);           /* 0x47d8e4 */
extern int32_t audio_uart_ring_mode_update_472362(uint32_t report_ms); /* ring task msg 0x1000 */
extern void DRV_TouchInit_55b66a(void);               /* binds g2_touch_ops */
extern void cy8c4046fni_reset_55b64a(void);           /* GPIO 10 low 10 ms, high, 50 ms */
extern int32_t cy8c4046fni_read_version_55b6dc(uint32_t *version); /* cmd 1, big-endian */
extern void gesture_touch_event_process_502ef4(void); /* g2-service-gesture-processor */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void INP_ThreadInit(void);
void thread_input_terminate(void);
void INP_ThreadHandler(void *argument);
void INP_ThreadExit(void);
void input_queue_drain(void);
void input_flags_dispatch(uint32_t flags);
void INP_BoxDetectInCase(const g2_input_msg_t *msg);
void input_touch_gesture_apply(const g2_input_msg_t *msg);
void input_buzzer_start(const g2_input_msg_t *msg);
void input_buzzer_stop(const g2_input_msg_t *msg);
void INP_SetTerminalMode(const g2_input_msg_t *msg);

static const char module_tag[] = "thread.input"; /* ROM 0x789ad0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_input.c"; /* ROM 0x7072d8 */
static const char thread_name[] = "input"; /* ROM 0x78ebbc */
static const char fn_thread_init[] = "INP_ThreadInit";             /* ROM 0x789ac0 */
static const char fn_resource_init[] = "INP_ResourceInit";         /* ROM 0x784284 */
static const char fn_hardware_init[] = "INP_HardwareInit";         /* ROM 0x784298 */
static const char fn_thread_handler[] = "INP_ThreadHandler";       /* ROM 0x7842ac */
static const char fn_message_processer[] = "INP_MessageProcesser"; /* ROM 0x77cc4c */
static const char fn_box_detect[] = "INP_BoxDetectInCase";         /* ROM 0x7842c0 */
static const char fn_terminal_mode[] = "INP_SetTerminalMode";      /* ROM 0x7842d4 */
static const char fn_thread_exit[] = "INP_ThreadExit";             /* ROM 0x789af0 */
static const char thread_fail[] = "osThreadNew fail";                                   /* ROM 0x784270 */
static const char thread_fail_short[] = "[thread.input]osThreadNew fail";               /* ROM 0x766a50 */
static const char thread_ok[] = "osThreadNew:0x%x, success";                            /* ROM 0x7736b8 */
static const char thread_ok_short[] = "[thread.input]osThreadNew:0x%x, success";        /* ROM 0x74fe4c */
static const char queue_fail[] = "osMessageQueueNew fail";                              /* ROM 0x77cc34 */
static const char queue_fail_short[] = "[thread.input]osMessageQueueNew fail";          /* ROM 0x74fe74 */
static const char queue_ok[] = "osMessageQueueNew:0x%x, success";                       /* ROM 0x766a70 */
static const char queue_ok_short[] = "[thread.input]osMessageQueueNew:0x%x, success";   /* ROM 0x739dc4 */
static const char dfu_cfg[] = "touch gesture cfg after startup dfu: long_press_threshold_ms=%u"; /* ROM 0x710524 */
static const char dfu_cfg_short[] =
    "[thread.input]touch gesture cfg after startup dfu: long_press_threshold_ms=%u"; /* ROM 0x6f0718 */
static const char dfu_cfg_fail[] = "touch gesture cfg read failed after startup dfu"; /* ROM 0x739df4 */
static const char dfu_cfg_fail_short[] =
    "[thread.input]touch gesture cfg read failed after startup dfu"; /* ROM 0x710564 */
static const char notify_error[] = "Notify error!";                       /* ROM 0x789ae0 */
static const char notify_error_short[] = "[thread.input]Notify error!";   /* ROM 0x7736d4 */
static const char bad_message[] = "Receive error message, id = [%d]";     /* ROM 0x75bb74 */
static const char bad_message_short[] = "[thread.input]Receive error message, id = [%d]"; /* ROM 0x739e24 */
static const char box_in_case[] = "Box detect in case, reset touch and save proximity baseline"; /* ROM 0x71a0d4 */
static const char box_in_case_short[] =
    "[thread.input]Box detect in case, reset touch and save proximity baseline"; /* ROM 0x6f6d80 */
static const char ring_report[] = "set ring touch algo report time: %u ms"; /* ROM 0x74fe9c */
static const char ring_report_short[] = "[thread.input]set ring touch algo report time: %u ms"; /* ROM 0x724960 */
static const char cfg_read_fail[] = "read touch gesture cfg failed: %d, continue apply target"; /* ROM 0x71a110 */
static const char cfg_read_fail_short[] =
    "[thread.input]read touch gesture cfg failed: %d, continue apply target"; /* ROM 0x6fe3e4 */
static const char cfg_write_fail[] = "write touch gesture cfg failed: %d, threshold=%u"; /* ROM 0x72f1f8 */
static const char cfg_write_fail_short[] =
    "[thread.input]write touch gesture cfg failed: %d, threshold=%u"; /* ROM 0x7105a4 */
static const char cfg_unchanged[] = "touch long press threshold unchanged by mode=%lu, threshold=%u ms"; /* ROM 0x70731c */
static const char cfg_unchanged_short[] =
    "[thread.input]touch long press threshold unchanged by mode=%lu, threshold=%u ms"; /* ROM 0x6f0768 */
static const char cfg_readback_fail[] = "readback touch gesture cfg failed: %d"; /* ROM 0x74fec4 */
static const char cfg_readback_fail_short[] = "[thread.input]readback touch gesture cfg failed: %d"; /* ROM 0x72f22c */
static const char cfg_verify_fail[] = "touch gesture cfg verify failed, expected=%u ms, actual=%u ms"; /* ROM 0x7105e4 */
static const char cfg_verify_fail_short[] =
    "[thread.input]touch gesture cfg verify failed, expected=%u ms, actual=%u ms"; /* ROM 0x6f6dcc */
static const char cfg_set[] = "touch long press threshold set by mode=%lu, threshold=%u ms"; /* ROM 0x71a14c */
static const char cfg_set_short[] =
    "[thread.input]touch long press threshold set by mode=%lu, threshold=%u ms"; /* ROM 0x6f6e18 */
static const char queue_deleted[] = "input message queue deleted";                     /* ROM 0x7736f0 */
static const char queue_deleted_short[] = "[thread.input]input message queue deleted"; /* ROM 0x745460 */
static const char thread_exit[] = "thread input exit";                                 /* ROM 0x7842e8 */
static const char thread_exit_short[] = "[thread.input]thread input exit";             /* ROM 0x766a90 */

uint32_t g2_input_thread_cb[INPUT_THREAD_CB_SIZE / 4u];       /* RAM 0x20072370 */
uint32_t g2_input_thread_stack[INPUT_THREAD_STACK_SIZE / 4u]; /* RAM 0x2036ce40 */

g2_thread_desc_t g2_input_thread_desc = { /* RAM 0x2000408c */
    INP_ThreadInit, thread_input_terminate, NULL, NULL, {0u, 0u, 0u, 0u, 0u}};

g2_input_route_t g2_input_routes[INPUT_ROUTE_COUNT] = { /* RAM 0x200040b0 */
    {INPUT_MSG_TOUCH_EVENT, 0u, input_touch_gesture_apply},
    {INPUT_MSG_BUZZER_PLAY, 0u, input_buzzer_start},
    {INPUT_MSG_BUZZER_NEXT, 0u, input_buzzer_stop},
    {INPUT_MSG_BOX_IN_CASE, 0u, INP_BoxDetectInCase},
    {INPUT_MSG_TERMINAL_MODE, 0u, INP_SetTerminalMode},
};

static const g2_os_thread_attr_t input_thread_attr = { /* ROM 0x75b8ec */
    thread_name, 0u, g2_input_thread_cb, INPUT_THREAD_CB_SIZE,
    g2_input_thread_stack, INPUT_THREAD_STACK_SIZE, INPUT_THREAD_PRIORITY, 1u, 0u};

#define LOG_EXT(level, fn, line, ...) \
    do { if (audio_log_flags() & 2u) audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); } while (0)
#define LOG_ON() ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))

/* Stock 0x512c84: first word of the 64-byte record from 0x480d72(1, ...). */
int32_t input_tick_read(uint32_t *out)
{
    uint32_t record[16];
    if (out == NULL)
        return -1;
    (void)audio_ble_hci_radio_identifier_480d72(1u, record);
    *out = record[0];
    return 0;
}

void thread_input_state_enter(void)
{
    (void)audio_uart_ring_state_transition_4c9b86(INPUT_THREAD_SLOT);
}

void thread_input_state_exit(void)
{
    (void)audio_uart_ring_resource_transition_4c9be2(INPUT_THREAD_SLOT);
}

void INP_ThreadInit(void)
{
    g2_input_thread_desc.thread = osThreadNew(INP_ThreadHandler, NULL, &input_thread_attr);
    if (g2_input_thread_desc.thread == NULL) {
        LOG_EXT(1u, fn_thread_init, 0x71u, thread_fail);
        if (LOG_ON())
            (void)compress_log_output(0x04000000u, thread_fail_short, thread_fail_short);
    } else {
        LOG_EXT(4u, fn_thread_init, 0x73u, thread_ok, g2_input_thread_desc.thread);
        if (LOG_ON())
            (void)compress_log_output(0x10400000u, thread_ok_short, thread_ok_short,
                                      g2_input_thread_desc.thread);
    }
}

void INP_ResourceInit(void)
{
    g2_input_thread_desc.queue = osMessageQueueNew(INPUT_QUEUE_DEPTH, sizeof(g2_input_msg_t), NULL);
    if (g2_input_thread_desc.queue == NULL) {
        LOG_EXT(1u, fn_resource_init, 0x7bu, queue_fail);
        if (LOG_ON())
            (void)compress_log_output(0x04000000u, queue_fail_short, queue_fail_short);
    } else {
        LOG_EXT(4u, fn_resource_init, 0x7du, queue_ok, g2_input_thread_desc.queue);
        if (LOG_ON())
            (void)compress_log_output(0x10400000u, queue_ok_short, queue_ok_short,
                                      g2_input_thread_desc.queue);
    }
}

/* Buzzer, touch transport and touch DFU check, then report the long-press
 * threshold left by the DFU check. Factory mode (productModeGet() == 1) also
 * reads the touch firmware version. */
void INP_HardwareInit(void)
{
    uint16_t threshold;
    audio_uart_buffer_zero(&threshold, sizeof threshold, 0u);
    DRV_BuzzerInit();
    DRV_TouchInit_55b66a();
    TouchUpdateFirmwareCheck(0u);
    if (DRV_TouchReadGestureCfg_55b92a(&threshold) == 0) {
        LOG_EXT(3u, fn_hardware_init, 0x89u, dfu_cfg, (uint32_t)threshold);
        if (LOG_ON())
            (void)compress_log_output(0x0c400000u, dfu_cfg_short, dfu_cfg_short, (uint32_t)threshold);
    } else {
        LOG_EXT(2u, fn_hardware_init, 0x8bu, dfu_cfg_fail);
        if (LOG_ON())
            (void)compress_log_output(0x08000000u, dfu_cfg_fail_short, dfu_cfg_fail_short);
    }
    if (productModeGet() == 1u) {
        uint32_t version = 0u;
        (void)cy8c4046fni_read_version_55b6dc(&version);
    }
}

void thread_input_terminate(void)
{
    if (g2_input_thread_desc.thread != NULL) {
        (void)osThreadTerminate(g2_input_thread_desc.thread);
        g2_input_thread_desc.thread = NULL;
    }
}

void INP_ThreadHandler(void *argument)
{
    g2_input_msg_t unused = {0u, 0u, 0u};
    uint8_t reset_status[16];
    (void)argument;
    (void)unused;

    audio_uart_buffer_zero(reset_status, sizeof reset_status, 0u);
    thread_input_state_enter();
    INP_HardwareInit();
    INP_ResourceInit();
    (void)audio_uart_ring_rtc_snapshot_4d3554(reset_status);
    if (reset_status[2] != 0u) /* external reset pin */
        DRV_BuzzerPlay(BUZZER_EFFECT_PIN_RESET);
    thread_input_state_exit();

    for (;;) {
        uint32_t flags = osThreadFlagsWait(INPUT_FLAGS_ANY, 0u, OS_WAIT_FOREVER);
        if (flags != 0u && flags < 0x80000000u) {
            input_flags_dispatch(flags);
            continue;
        }
        LOG_EXT(1u, fn_thread_handler, 0xb5u, notify_error);
        if (LOG_ON())
            (void)compress_log_output(0x04000000u, notify_error_short, notify_error_short);
    }
}

void INP_MessageProcesser(const g2_input_msg_t *msg)
{
    uint32_t id = msg->id;
    uint32_t i;
    for (i = 0u; i < INPUT_ROUTE_COUNT; i++) {
        if ((uint16_t)id == g2_input_routes[i].id && g2_input_routes[i].handler != NULL) {
            g2_input_routes[i].handler(msg);
            return;
        }
    }
    if (i == INPUT_ROUTE_COUNT) {
        LOG_EXT(1u, fn_message_processer, 0xc6u, bad_message, (uint32_t)(uint16_t)id);
        if (LOG_ON())
            (void)compress_log_output(0x04400000u, bad_message_short, bad_message_short,
                                      (uint32_t)(uint16_t)id);
    }
}

void input_msg_send_touch(void)
{
    g2_input_msg_t msg = {0u, 0u, 0u};
    msg.id = INPUT_MSG_TOUCH_EVENT;
    audio_input_message_send_record(&msg);
}

void input_msg_send_id1(void)
{
    g2_input_msg_t msg = {0u, 0u, 0u};
    msg.id = INPUT_MSG_BUZZER_NEXT;
    audio_input_message_send_record(&msg);
}

void INP_BoxDetectInCase(const g2_input_msg_t *msg)
{
    uint32_t version;
    (void)msg;
    LOG_EXT(3u, fn_box_detect, 0x101u, box_in_case);
    if (LOG_ON())
        (void)compress_log_output(0x0c000000u, box_in_case_short, box_in_case_short);
    cy8c4046fni_reset_55b64a();
    version = 0u;
    (void)cy8c4046fni_read_version_55b6dc(&version);
    (void)DRV_TouchSaveProximityBaseline_55b730();
}

void input_touch_gesture_apply(const g2_input_msg_t *msg)
{
    (void)msg;
    gesture_touch_event_process_502ef4();
}

void input_buzzer_start(const g2_input_msg_t *msg)
{
    DRV_BuzzerPlayAfterQueue((int32_t)msg->param);
}

void input_buzzer_stop(const g2_input_msg_t *msg)
{
    (void)msg;
    buzzer_play_next();
}

/* Apply the long-press threshold for a terminal mode: skip when the touch
 * controller already holds it, otherwise write, wait 100 ms and read back. */
void INP_SetTerminalMode(const g2_input_msg_t *msg)
{
    uint16_t current;
    uint16_t target;
    int32_t status;

    audio_uart_buffer_zero(&current, sizeof current, 0u);
    if (msg == NULL)
        return;
    target = msg->param != 0u ? LONG_PRESS_MS_MODE : LONG_PRESS_MS_DEFAULT;

    if (UX_GetSelfRingStatus() != 0u) {
        (void)audio_uart_ring_mode_update_472362(target);
        LOG_EXT(3u, fn_terminal_mode, 0x127u, ring_report, (uint32_t)target);
        if (LOG_ON())
            (void)compress_log_output(0x0c400000u, ring_report_short, ring_report_short, (uint32_t)target);
    }

    status = DRV_TouchReadGestureCfg_55b92a(&current);
    if (status == 0) {
        if (current == target) {
            LOG_EXT(3u, fn_terminal_mode, 0x12eu, cfg_unchanged, msg->param, (uint32_t)current);
            if (LOG_ON())
                (void)compress_log_output(0x0c800000u, cfg_unchanged_short, cfg_unchanged_short,
                                          msg->param, (uint32_t)current);
            return;
        }
    } else {
        LOG_EXT(2u, fn_terminal_mode, 300u, cfg_read_fail, status);
        if (LOG_ON())
            (void)compress_log_output(0x08400000u, cfg_read_fail_short, cfg_read_fail_short, status);
    }

    current = target;
    status = DRV_TouchWriteGestureCfg_55b840(&current);
    if (status != 0) {
        LOG_EXT(1u, fn_terminal_mode, 0x136u, cfg_write_fail, status, (uint32_t)target);
        if (LOG_ON())
            (void)compress_log_output(0x04800000u, cfg_write_fail_short, cfg_write_fail_short,
                                      status, (uint32_t)target);
        return;
    }
    (void)osDelay(TOUCH_CFG_SETTLE_MS);
    status = DRV_TouchReadGestureCfg_55b92a(&current);
    if (status != 0) {
        LOG_EXT(2u, fn_terminal_mode, 0x13eu, cfg_readback_fail, status);
        if (LOG_ON())
            (void)compress_log_output(0x08400000u, cfg_readback_fail_short, cfg_readback_fail_short, status);
    } else if (current != target) {
        LOG_EXT(1u, fn_terminal_mode, 0x142u, cfg_verify_fail, (uint32_t)target, (uint32_t)current);
        if (LOG_ON())
            (void)compress_log_output(0x04800000u, cfg_verify_fail_short, cfg_verify_fail_short,
                                      (uint32_t)target, (uint32_t)current);
    } else {
        LOG_EXT(3u, fn_terminal_mode, 0x146u, cfg_set, msg->param, (uint32_t)current);
        if (LOG_ON())
            (void)compress_log_output(0x0c800000u, cfg_set_short, cfg_set_short,
                                      msg->param, (uint32_t)current);
    }
}

void input_queue_drain(void)
{
    g2_input_msg_t msg = {0u, 0u, 0u};
    while (osMessageQueueGet(g2_input_thread_desc.queue, &msg, NULL, 0u) == 0)
        INP_MessageProcesser(&msg);
}

void input_flags_dispatch(uint32_t flags)
{
    if (flags & INPUT_FLAG_QUEUE)
        input_queue_drain();
    if (flags & INPUT_FLAG_EXIT)
        INP_ThreadExit();
}

void INP_ThreadExit(void)
{
    audio_uart_ring_sync_exit_4c9c3c(INPUT_THREAD_SLOT);
    if (g2_input_thread_desc.queue != NULL) {
        (void)osMessageQueueDelete(g2_input_thread_desc.queue);
        g2_input_thread_desc.queue = NULL;
        LOG_EXT(4u, fn_thread_exit, 0x166u, queue_deleted);
        if (LOG_ON())
            (void)compress_log_output(0x10000000u, queue_deleted_short, queue_deleted_short);
    }
    LOG_EXT(4u, fn_thread_exit, 0x168u, thread_exit);
    if (LOG_ON())
        (void)compress_log_output(0x10000000u, thread_exit_short, thread_exit_short);
    for (;;)
        (void)osDelay(OS_WAIT_FOREVER);
}
