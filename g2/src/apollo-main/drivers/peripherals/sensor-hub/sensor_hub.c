/* Sensor hub thread, stock D:\01_workspace\s200_ap510b_iar_git\platform\sensor_hub\sensor_hub.c.
 * Native 0x4a6644..0x4a6bce and 0x4a6d26..0x4a6e3c, 0x4a6ee8..0x4a7344
 * (HUB_ParameterConfig 0x4a6e3c lives in hub-parameter/, HUB_IMUCalibParaInit
 * 0x4a6bce in sensor_hub_calib.c). Literal pools 0x4a6ecc..0x4a6ee7 and
 * 0x4a713c..0x4a743f.
 *
 * Data owned here: thread-manager descriptor 0x20003664 (slot 5), message
 * routing table 0x20003688, thread control block 0x20072060 and stack
 * 0x20102c54, IMU interrupt tick 0x2007490c, IMU-ready flag 0x20074910 and the
 * queue-receive error counter 0x20074914. The descriptor and routing table are
 * initialised data (SRAM init stream record 0x75d3f4). The per-call 8-byte zero
 * images at ROM 0x78e474..0x78e4b3 are IAR aggregate-initialiser copies of the
 * `= {0}` message locals. */
#include <stdint.h>
#include <stddef.h>
#include "g2_als.h"
#include "sensor_hub.h"

/* Thread-manager descriptor; every managed thread has one of these 0x24-byte rows. */
typedef struct {
    void (*init)(void);   /* +0x00 HUB_ThreadInit */
    void (*deinit)(void); /* +0x04 hub_thread_terminate */
    void *thread;         /* +0x08 osThreadId_t */
    void *queue;          /* +0x0c osMessageQueueId_t */
    uint32_t reserved[5]; /* +0x10 unused by sensor_hub.c, zero */
} g2_thread_desc_t;
_Static_assert(sizeof(g2_thread_desc_t) == 0x24, "thread-manager descriptor stride");

typedef void (*g2_hub_handler_t)(const g2_hub_msg_t *msg);
typedef struct {
    uint16_t id;              /* +0 */
    uint16_t pad;             /* +2 */
    g2_hub_handler_t handler; /* +4 */
} g2_hub_route_t;
_Static_assert(sizeof(g2_hub_route_t) == 8, "stock route row");
#define HUB_ROUTE_COUNT 8u

/* CMSIS-RTOS2 attribute records (IAR layout, 4-byte enums). */
typedef struct {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority;
    uint32_t tz_module; uint32_t reserved;
} g2_os_thread_attr_t;
_Static_assert(sizeof(g2_os_thread_attr_t) == 36, "osThreadAttr_t");
typedef struct {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
} g2_os_timer_attr_t;
_Static_assert(sizeof(g2_os_timer_attr_t) == 16, "osTimerAttr_t");

#define HUB_QUEUE_DEPTH 50u
#define HUB_THREAD_CB_SIZE 0x70u
#define HUB_THREAD_STACK_SIZE 0x2000u
#define HUB_THREAD_PRIORITY 0x29u /* osPriorityHigh1 */
#define HUB_THREAD_MANAGER_SLOT 5u
#define OS_TIMER_PERIODIC 1u
#define OS_WAIT_FOREVER 0xffffffffu

extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr);
extern int32_t osThreadTerminate(void *thread);
extern void *osMessageQueueNew(uint32_t count, uint32_t size, const void *attr);
extern int32_t osMessageQueuePut(void *queue, const void *msg, uint8_t prio, uint32_t timeout);
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout);
extern void *osTimerNew(void (*func)(void *), uint32_t type, void *argument, const void *attr);
extern int32_t osTimerStart(void *timer, uint32_t ticks);
extern int32_t osTimerStop(void *timer);
extern uint32_t osKernelGetTickCount(void);
extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t slot);    /* thread manager: running */
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t slot); /* thread manager: idle */
extern void task_vote_acquire_current(void);
extern void task_vote_release_current(void);
extern uint8_t productModeGet(void);
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t semantic_OtaTransferActive(void);
extern void SVC_Settings_HeadUpConfig(void);
/* IMU glue, module g2-imu-icm45608 (drivers/peripherals/imu-icm45608). */
extern uint32_t DRV_IMUReadData(uint32_t tick);
extern void DRV_IMUStartRawDataCollection(void);
extern void DRV_IMUStopRawDataCollection(void);
extern int32_t semantic_imu_init(uint8_t mode);
extern void semantic_sensor_reset_line(void); /* IMU power off */
extern uint32_t semantic_get_state_20074674(void); /* head-up open */
extern uint32_t semantic_get_state_20074678(void); /* compass open */
extern uint32_t semantic_get_state_2007467c(void); /* dis open */
extern uint32_t semantic_get_state_20074680(void); /* type-5 user open */
extern void semantic_set_state_20074674(uint32_t open);
extern void semantic_set_state_20074678(uint32_t open);
extern void semantic_set_state_2007467c(uint32_t open);
extern void semantic_set_state_20074680(uint32_t open);

extern volatile uint16_t audio_uart_hub_role_cell; /* RAM 0x20004526, init 3 */
extern void *audio_hub_timer_handle;               /* RAM 0x20074908 */
extern uint8_t audio_hub_timer_control_block[44];  /* RAM 0x20073650 */

static const char hub_module[] = "sensor_hub"; /* ROM 0x78bde0, also the thread name */
static const char hub_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\sensor_hub\\sensor_hub.c"; /* ROM 0x6fc974 */
static const char fn_thread_init[] = "HUB_ThreadInit"; /* ROM 0x788640 */
static const char thread_fail[] = "[HUB_ThreadInit]osThreadNew fail"; /* ROM 0x758f94 */
static const char thread_fail_short[] = "[sensor_hub][HUB_ThreadInit]osThreadNew fail"; /* ROM 0x737ab4 */
static const char thread_ok[] = "[HUB_ThreadInit]osThreadNew:0x%x, success"; /* ROM 0x742860 */
static const char thread_ok_short[] = "[sensor_hub][HUB_ThreadInit]osThreadNew:0x%x, success"; /* ROM 0x722270 */
static const char fn_resource_init[] = "HUB_ResourceInit"; /* ROM 0x782de4 */
static const char queue_fail[] = "[HUB_ResourceInit]osMessageQueueNew fail"; /* ROM 0x74288c */
static const char queue_fail_short[] = "[sensor_hub][HUB_ResourceInit]osMessageQueueNew fail"; /* ROM 0x7222a8 */
static const char queue_ok[] = "[HUB_ResourceInit]osMessageQueueNew:0x%x, success"; /* ROM 0x72cc64 */
static const char queue_ok_short[] = "[sensor_hub][HUB_ResourceInit]osMessageQueueNew:0x%x, success"; /* ROM 0x70e6e4 */
static const char timer_fail[] = "[HUB_ResourceInit]osTimerNew failed"; /* ROM 0x758fb8 */
static const char timer_fail_short[] = "[sensor_hub][HUB_ResourceInit]osTimerNew failed"; /* ROM 0x737ae4 */
static const char timer_ok[] = "[HUB_ResourceInit]osTimerNew success"; /* ROM 0x74d714 */
static const char timer_ok_short[] = "[sensor_hub][HUB_ResourceInit]osTimerNew success"; /* ROM 0x72cc98 */
static const char timer_name[] = "sensor_hub_timer"; /* ROM 0x782dd0 */
static const char fn_processer[] = "HUB_MessageProcesser"; /* ROM 0x77b1dc */
static const char bad_id[] = "[HUB_MessageProcesser]Receive error message, id = [%d]"; /* ROM 0x7222e0 */
static const char bad_id_short[] = "[sensor_hub][HUB_MessageProcesser]Receive error message, id = [%d]"; /* ROM 0x705270 */
static const char fn_collection[] = "HUB_IMUCollectionHandler"; /* ROM 0x770adc */
static const char collection[] = "IMU sensor collection"; /* ROM 0x77b1f4 */
static const char collection_short[] = "[sensor_hub]IMU sensor collection"; /* ROM 0x758fdc */
static const char fn_send[] = "HUB_SendMessage"; /* ROM 0x788650 */
static const char put_fail[] = "[HUB_MessageProcesser]osMessageQueuePut error:%d"; /* ROM 0x72cccc */
static const char put_fail_short[] = "[sensor_hub][HUB_MessageProcesser]osMessageQueuePut error:%d"; /* ROM 0x70e724 */
static const char fn_set_mode[] = "HUB_IMUSetModeHandler"; /* ROM 0x77b20c */
static const char set_mode[] = "[HUB_IMUSetModeHandler]set mode: %d"; /* ROM 0x759000 */
static const char set_mode_short[] = "[sensor_hub][HUB_IMUSetModeHandler]set mode: %d"; /* ROM 0x737b14 */
static const char set_mode_error[] = "[HUB_IMUSetMode]set mode error"; /* ROM 0x764830 */
static const char set_mode_error_short[] = "[sensor_hub][HUB_IMUSetMode]set mode error"; /* ROM 0x7428b8 */
static const char fn_open[] = "HUB_Open"; /* ROM 0x78bdec */
static const char open_left[] = "IMU open role type is left, cannot open"; /* ROM 0x74d73c */
static const char open_left_short[] = "[sensor_hub]IMU open role type is left, cannot open"; /* ROM 0x72cd00 */
static const char fn_close[] = "HUB_Close"; /* ROM 0x78bdf8 */
static const char close_left[] = "IMU open role type is left, cannot close"; /* ROM 0x7428e4 */
static const char close_left_short[] = "[sensor_hub]IMU open role type is left, cannot close"; /* ROM 0x722318 */
static const char fn_func_open[] = "HUB_IMUFuncOpenHandler"; /* ROM 0x77b23c */
static const char fn_func_close[] = "HUB_IMUFuncCloseHandler"; /* ROM 0x77b254 */
static const char type_error[] = "FuncOpen func_type error"; /* ROM 0x770af8 */
static const char type_error_short[] = "[sensor_hub]FuncOpen func_type error"; /* ROM 0x74d764 */
static const char open_busy[] = "FuncOpen func_type=%d, but dis or compass is open"; /* ROM 0x72cd34 */
static const char open_busy_short[] = "[sensor_hub]FuncOpen func_type=%d, but dis or compass is open"; /* ROM 0x70e764 */
static const char open_mode0[] = "FuncOpen func_type=%d, set work mode to 0"; /* ROM 0x74293c */
static const char open_mode0_short[] = "[sensor_hub]FuncOpen func_type=%d, set work mode to 0"; /* ROM 0x722388 */
static const char open_dis_busy[] = "FuncOpen func_type=%d, but dis is open"; /* ROM 0x74d78c */
static const char open_dis_busy_short[] = "[sensor_hub]FuncOpen func_type=%d, but dis is open"; /* ROM 0x72cd68 */
static const char open_mode2[] = "FuncOpen func_type=%d, set work mode to 2"; /* ROM 0x742968 */
static const char open_mode2_short[] = "[sensor_hub]FuncOpen func_type=%d, set work mode to 2"; /* ROM 0x7223c0 */
static const char open_mode1[] = "FuncOpen func_type=%d, set work mode to 1"; /* ROM 0x742994 */
static const char open_mode1_short[] = "[sensor_hub]FuncOpen func_type=%d, set work mode to 1"; /* ROM 0x7223f8 */
static const char close_mode1[] = "FuncClose func_type=%d, set work mode to 1"; /* ROM 0x7429c0 */
static const char close_mode1_short[] = "[sensor_hub]FuncClose func_type=%d, set work mode to 1"; /* ROM 0x722430 */
static const char close_mode2[] = "FuncClose func_type=%d, set work mode to 2"; /* ROM 0x7429ec */
static const char close_mode2_short[] = "[sensor_hub]FuncClose func_type=%d, set work mode to 2"; /* ROM 0x722468 */
static const char close_mode0[] = "FuncClose func_type=%d, set work mode to 0"; /* ROM 0x742a18 */
static const char close_mode0_short[] = "[sensor_hub]FuncClose func_type=%d, set work mode to 0"; /* ROM 0x7224a0 */
static const char close_off[] = "FuncClose func_type=%d, power off"; /* ROM 0x759024 */
static const char close_off_short[] = "[sensor_hub]FuncClose func_type=%d, power off"; /* ROM 0x737b44 */

/* The stock log macro: extended record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. */
#define HUB_LOG0(level, code, fn, line, text, text_short)                         \
    do {                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                       \
            audio_log_extended((level), hub_module, hub_path, (fn), (line), (text)); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)     \
            (void)compress_log_output((code), (text_short), (text_short));        \
    } while (0)
#define HUB_LOG1(level, code, fn, line, text, text_short, arg)                    \
    do {                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                       \
            audio_log_extended((level), hub_module, hub_path, (fn), (line), (text), (arg)); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)     \
            (void)compress_log_output((code), (text_short), (text_short), (arg)); \
    } while (0)

uint32_t g2_hub_thread_cb[HUB_THREAD_CB_SIZE / 4u];       /* RAM 0x20072060 */
uint32_t g2_hub_thread_stack[HUB_THREAD_STACK_SIZE / 4u]; /* RAM 0x20102c54 */
volatile uint32_t g2_hub_imu_irq_tick;      /* RAM 0x2007490c, tick of the last IMU interrupt */
volatile uint32_t g2_hub_imu_ready;         /* RAM 0x20074910, 1 once a work mode is set */
volatile uint32_t g2_hub_queue_get_errors;  /* RAM 0x20074914 */

g2_thread_desc_t g2_hub_thread_desc = {     /* RAM 0x20003664 */
    HUB_ThreadInit, hub_thread_terminate, NULL, NULL, {0u, 0u, 0u, 0u, 0u}};

/* RAM 0x20003688. Stock row order; ids 5/6 follow 7. */
g2_hub_route_t g2_hub_routes[HUB_ROUTE_COUNT] = {
    {G2_HUB_MSG_IMU_SET_MODE, 0u, HUB_IMUSetModeHandler},
    {G2_HUB_MSG_IMU_READ, 0u, hub_imu_register_write},
    {G2_HUB_MSG_IMU_CALIB, 0u, hub_calib_init_wrapper},
    {G2_HUB_MSG_IMU_COLLECT, 0u, HUB_IMUCollectionHandler},
    {G2_HUB_MSG_NOP, 0u, hub_empty_hook},
    {G2_HUB_MSG_FUNC_OPEN, 0u, HUB_IMUFuncOpenHandler},
    {G2_HUB_MSG_FUNC_CLOSE, 0u, HUB_IMUFuncCloseHandler},
    {G2_HUB_MSG_ALS_TIMER, 0u, (g2_hub_handler_t)als_function_34}, /* ignores the message */
};

static const g2_os_thread_attr_t hub_thread_attr = { /* ROM 0x759048 */
    hub_module, 0u, g2_hub_thread_cb, HUB_THREAD_CB_SIZE,
    g2_hub_thread_stack, HUB_THREAD_STACK_SIZE, HUB_THREAD_PRIORITY, 1u, 0u};
static const g2_os_timer_attr_t hub_timer_attr = { /* ROM 0x788660 */
    timer_name, 0u, audio_hub_timer_control_block, sizeof audio_hub_timer_control_block};

void HUB_ThreadInit(void) {
    g2_hub_thread_desc.thread = osThreadNew(hub_thread_entry, NULL, &hub_thread_attr);
    if (g2_hub_thread_desc.thread == NULL)
        HUB_LOG0(1u, 0x04000000u, fn_thread_init, 89u, thread_fail, thread_fail_short);
    else
        HUB_LOG1(4u, 0x10400000u, fn_thread_init, 91u, thread_ok, thread_ok_short,
                 g2_hub_thread_desc.thread);
}

void HUB_ResourceInit(void) {
    g2_hub_thread_desc.queue = osMessageQueueNew(HUB_QUEUE_DEPTH, sizeof(g2_hub_msg_t), NULL);
    if (g2_hub_thread_desc.queue == NULL)
        HUB_LOG0(1u, 0x04000000u, fn_resource_init, 99u, queue_fail, queue_fail_short);
    else
        HUB_LOG1(4u, 0x10400000u, fn_resource_init, 101u, queue_ok, queue_ok_short,
                 g2_hub_thread_desc.queue);
    if (audio_hub_timer_handle == NULL) {
        /* Periodic ALS timer; started/stopped by the ALS driver via hub_timer_start/stop. */
        audio_hub_timer_handle = osTimerNew(hub_msg_send_id8, OS_TIMER_PERIODIC, NULL,
                                            &hub_timer_attr);
        if (audio_hub_timer_handle == NULL)
            HUB_LOG0(1u, 0x04000000u, fn_resource_init, 107u, timer_fail, timer_fail_short);
        else
            HUB_LOG0(4u, 0x10000000u, fn_resource_init, 109u, timer_ok, timer_ok_short);
    }
}

void hub_thread_terminate(void) {
    if (g2_hub_thread_desc.thread != NULL) {
        (void)osThreadTerminate(g2_hub_thread_desc.thread);
        g2_hub_thread_desc.thread = NULL;
    }
}

void hub_state_enter(void) {
    (void)audio_uart_ring_state_transition_4c9b86(HUB_THREAD_MANAGER_SLOT);
}

void hub_state_exit(void) {
    (void)audio_uart_ring_resource_transition_4c9be2(HUB_THREAD_MANAGER_SLOT);
}

/* Product (factory) mode: IMU work mode 4 and ALS init. Otherwise the right
 * side (role 3) applies the head-up settings and the left side powers the IMU off. */
void hub_thread_entry(void *argument) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e474 */
    (void)argument;
    hub_state_enter();
    HUB_ResourceInit();
    HUB_IMUCalibParaInit();
    hub_role_init();
    if (productModeGet() == 1u) {
        (void)hub_msg_send_id1(4u);
        (void)als_function_25();
    } else if (hub_role_get() == G2_HUB_ROLE_RIGHT) {
        SVC_Settings_HeadUpConfig();
    } else {
        semantic_sensor_reset_line();
    }
    hub_state_exit();
    for (;;) {
        if (osMessageQueueGet(g2_hub_thread_desc.queue, &msg, NULL, OS_WAIT_FOREVER) != 0) {
            g2_hub_queue_get_errors++;
            continue;
        }
        task_vote_acquire_current();
        HUB_MessageProcesser(&msg);
        task_vote_release_current();
    }
}

void HUB_MessageProcesser(const g2_hub_msg_t *msg) {
    const uint16_t id = msg->id;
    uint32_t i;
    for (i = 0u; i < HUB_ROUTE_COUNT; i++) {
        if (id == g2_hub_routes[i].id && g2_hub_routes[i].handler != NULL) {
            g2_hub_routes[i].handler(msg);
            return;
        }
    }
    HUB_LOG1(1u, 0x04400000u, fn_processer, 183u, bad_id, bad_id_short, (uint32_t)id);
}

/* osTimer callback of "sensor_hub_timer": forwards the ALS timer tick to the thread. */
void hub_msg_send_id8(void *argument) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e47c */
    (void)argument;
    msg.id = G2_HUB_MSG_ALS_TIMER;
    HUB_SendMessage(&msg);
}

void hub_timer_start(uint32_t ticks) {
    (void)osTimerStart(audio_hub_timer_handle, ticks);
}

void hub_timer_stop(void) {
    (void)osTimerStop(audio_hub_timer_handle);
}

/* Message 2: read the IMU FIFO, stamped with the interrupt tick. */
void hub_imu_register_write(const g2_hub_msg_t *msg) {
    (void)msg;
    (void)DRV_IMUReadData(g2_hub_imu_irq_tick);
}

void hub_calib_init_wrapper(const g2_hub_msg_t *msg) {
    (void)msg;
    HUB_IMUCalibParaInit();
}

void HUB_IMUCollectionHandler(const g2_hub_msg_t *msg) {
    HUB_LOG0(4u, 0x10000000u, fn_collection, 225u, collection, collection_short);
    if (msg->value == 1u)
        DRV_IMUStartRawDataCollection();
    else if (msg->value == 0u)
        DRV_IMUStopRawDataCollection();
}

/* Non-blocking put; a full queue is logged and the message dropped. */
void HUB_SendMessage(const g2_hub_msg_t *msg) {
    int32_t status;
    if (msg == NULL || g2_hub_thread_desc.queue == NULL)
        return;
    status = osMessageQueuePut(g2_hub_thread_desc.queue, msg, 0u, 0u);
    if (status != 0)
        HUB_LOG1(1u, 0x04400000u, fn_send, 242u, put_fail, put_fail_short, status);
}

int32_t hub_msg_send_id1(uint8_t mode) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e484 */
    msg.id = G2_HUB_MSG_IMU_SET_MODE;
    msg.value = mode;
    HUB_SendMessage(&msg);
    return 0;
}

int32_t hub_msg_send_id4(uint8_t start) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e48c */
    msg.id = G2_HUB_MSG_IMU_COLLECT;
    msg.value = start;
    HUB_SendMessage(&msg);
    return 0;
}

int32_t hub_msg_send_id3(void) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e494 */
    msg.id = G2_HUB_MSG_IMU_CALIB;
    HUB_SendMessage(&msg);
    return 0;
}

/* Despite the inventory name this is the IMU interrupt callback: board pin
 * table row {0x26, 0x20002, this} at ROM 0x686f74 (table 0x686db8). Ignored
 * until a work mode is set and while an OTA transfer runs. */
void hub_als_timer_callback(void) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e49c */
    if (g2_hub_imu_ready == 0u || semantic_OtaTransferActive() != 0u)
        return;
    g2_hub_imu_irq_tick = osKernelGetTickCount();
    msg.id = G2_HUB_MSG_IMU_READ;
    HUB_SendMessage(&msg);
}

void HUB_IMUSetModeHandler(const g2_hub_msg_t *msg) {
    if (msg->value < 5u) {
        g2_hub_imu_ready = 0u;
        HUB_LOG1(1u, 0x04400000u, fn_set_mode, 290u, set_mode, set_mode_short, msg->value);
        (void)semantic_imu_init((uint8_t)msg->value);
        g2_hub_imu_ready = 1u;
    } else {
        HUB_LOG0(1u, 0x04000000u, fn_set_mode, 294u, set_mode_error, set_mode_error_short);
    }
}

void hub_empty_hook(const g2_hub_msg_t *msg) {
    (void)msg;
}

/* Device role 1 -> hub role 3, device role 2 -> hub role 2 (left), else unchanged. */
void hub_role_init(void) {
    const uint8_t role = audio_uart_device_role_get();
    if (role == 1u)
        audio_uart_hub_role_cell = G2_HUB_ROLE_RIGHT;
    else if (role == 2u)
        audio_uart_hub_role_cell = G2_HUB_ROLE_LEFT;
}

uint16_t hub_role_get(void) {
    return audio_uart_hub_role_cell;
}

int32_t HUB_Open(uint8_t func_type) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e4a4 */
    if (hub_role_get() == G2_HUB_ROLE_LEFT) {
        HUB_LOG0(1u, 0x04000000u, fn_open, 391u, open_left, open_left_short);
        return -1;
    }
    msg.id = G2_HUB_MSG_FUNC_OPEN;
    msg.value = func_type;
    HUB_SendMessage(&msg);
    return 0;
}

int32_t HUB_Close(uint8_t func_type) {
    g2_hub_msg_t msg = {0}; /* ROM image 0x78e4ac */
    if (hub_role_get() == G2_HUB_ROLE_LEFT) {
        HUB_LOG0(1u, 0x04000000u, fn_close, 404u, close_left, close_left_short);
        return -1;
    }
    msg.id = G2_HUB_MSG_FUNC_CLOSE;
    msg.value = func_type;
    HUB_SendMessage(&msg);
    return 0;
}

void HUB_IMUFuncOpenHandler(const g2_hub_msg_t *msg) {
    const uint8_t func = (uint8_t)msg->value;
    if (func >= G2_HUB_FUNC_COUNT) {
        HUB_LOG0(1u, 0x04000000u, fn_func_open, 440u, type_error, type_error_short);
        return;
    }
    switch (func) {
    case G2_HUB_FUNC_HEADUP:
    case G2_HUB_FUNC_TYPE5:
        if (func == G2_HUB_FUNC_HEADUP)
            semantic_set_state_20074674(1u);
        else if (func == G2_HUB_FUNC_TYPE5)
            semantic_set_state_20074680(1u);
        if (semantic_get_state_2007467c() == 1u || semantic_get_state_20074678() == 1u) {
            HUB_LOG1(2u, 0x08400000u, fn_func_open, 452u, open_busy, open_busy_short,
                     (uint32_t)func);
        } else {
            HUB_LOG1(2u, 0x08400000u, fn_func_open, 454u, open_mode0, open_mode0_short,
                     (uint32_t)func);
            (void)hub_msg_send_id1(0u);
        }
        break;
    case G2_HUB_FUNC_COMPASS:
        semantic_set_state_20074678(1u);
        if (semantic_get_state_2007467c() == 1u) {
            HUB_LOG1(2u, 0x08400000u, fn_func_open, 461u, open_dis_busy, open_dis_busy_short,
                     (uint32_t)func);
        } else {
            HUB_LOG1(2u, 0x08400000u, fn_func_open, 463u, open_mode2, open_mode2_short,
                     (uint32_t)func);
            (void)hub_msg_send_id1(2u);
        }
        break;
    case G2_HUB_FUNC_DIS:
        semantic_set_state_2007467c(1u);
        HUB_LOG1(2u, 0x08400000u, fn_func_open, 469u, open_mode1, open_mode1_short,
                 (uint32_t)func);
        (void)hub_msg_send_id1(1u);
        break;
    case G2_HUB_FUNC_ALS:
        (void)als_function_28(); /* DRV_ALSOpen */
        break;
    default: /* G2_HUB_FUNC_NONE */
        break;
    }
}

/* Clears the user's flag, then reprograms the IMU for the highest-priority
 * remaining user, or powers it off. ALS (type 4) only closes the ALS driver. */
void HUB_IMUFuncCloseHandler(const g2_hub_msg_t *msg) {
    const uint8_t func = (uint8_t)msg->value;
    if (func >= G2_HUB_FUNC_COUNT) {
        HUB_LOG0(1u, 0x04000000u, fn_func_close, 484u, type_error, type_error_short);
        return;
    }
    switch (func) {
    case G2_HUB_FUNC_HEADUP:
        semantic_set_state_20074674(0u);
        break;
    case G2_HUB_FUNC_COMPASS:
        semantic_set_state_20074678(0u);
        break;
    case G2_HUB_FUNC_DIS:
        semantic_set_state_2007467c(0u);
        break;
    case G2_HUB_FUNC_ALS:
        (void)als_function_29(); /* DRV_ALSClose */
        return;
    case G2_HUB_FUNC_TYPE5:
        semantic_set_state_20074680(0u);
        break;
    default: /* G2_HUB_FUNC_NONE: re-evaluate only */
        break;
    }
    if (semantic_get_state_2007467c() == 1u) {
        HUB_LOG1(2u, 0x08400000u, fn_func_close, 507u, close_mode1, close_mode1_short,
                 (uint32_t)func);
        (void)hub_msg_send_id1(1u);
    } else if (semantic_get_state_20074678() == 1u) {
        HUB_LOG1(2u, 0x08400000u, fn_func_close, 510u, close_mode2, close_mode2_short,
                 (uint32_t)func);
        (void)hub_msg_send_id1(2u);
    } else if (semantic_get_state_20074674() == 1u || semantic_get_state_20074680() == 1u) {
        HUB_LOG1(2u, 0x08400000u, fn_func_close, 513u, close_mode0, close_mode0_short,
                 (uint32_t)func);
        (void)hub_msg_send_id1(0u);
    } else {
        HUB_LOG1(2u, 0x08400000u, fn_func_close, 516u, close_off, close_off_short,
                 (uint32_t)func);
        semantic_sensor_reset_line();
    }
}
