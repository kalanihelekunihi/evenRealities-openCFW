/* BLE message-receive thread, stock D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_msgrx.c.
 * Native 0x48edb0..0x48f017 (literal pool 0x48f324..0x48f35b).
 * Owned elsewhere in the same stock file: Thread_BleMsgrxQueueClear 0x48f018
 * (ble/ble-queue/ble_queue_clear.c) and Thread_MsgRxFromBle 0x48f12c
 * (drivers/display/display-thread/display_thread_msg_rx_ble.c).
 *
 * Producers (Thread_MsgRxFromBle) queue a heap node pointer (150-entry queue) and raise
 * thread flag bit 22; bit 23 terminates the thread. Node layout: +0 message id, +4 length,
 * +8 payload. The manager object is RAM 0x20003ffc: +0 init hook (threadBleMsgRxInit),
 * +4 deinit hook (threadBleMsgRxDeinit), +8 thread, +12 queue. */
#include <stdint.h>
#include <stddef.h>

#define MSGRX_THREAD_INDEX 7u
#define MSGRX_QUEUE_DEPTH 150u
#define MSGRX_FLAG_QUEUE 0x00400000u
#define MSGRX_FLAG_EXIT 0x00800000u
#define MSGRX_FLAGS_ALL 0x00ffffffu
#define OS_WAIT_FOREVER 0xffffffffu

/* Message ids routed by _thread_pb_msg_handler. */
#define MSGRX_ID_DEV_CONFIG 0x080u        /* protobuf device-config frame */
#define MSGRX_ID_OTA_FIRST 0x0c0u         /* 0xc0..0xc3: OTA frame commands */
#define MSGRX_ID_EFS_FIRST 0x0c4u         /* 0xc4..0xc7: EFS frame commands */
#define MSGRX_ID_MASTER_PAIR_ERASE 0x200u /* EVENT_BLE_MSG_MASTER_PAIR_ERASE */
#define MSGRX_ID_EFS_CANCEL_EXPORT 0x400u

typedef struct {
    uint32_t id;       /* +0x0 */
    uint32_t length;   /* +0x4 */
    uint8_t payload[]; /* +0x8 */
} msgrx_node_t;

struct ble_msgrx_manager {
    void (*init)(void);   /* +0x0 */
    void (*deinit)(void); /* +0x4 */
    void *thread;         /* +0x8 */
    void *queue;          /* +0xc */
};
_Static_assert(sizeof(struct ble_msgrx_manager) == 16u, "BLE manager ABI");

extern uint8_t audio_ble_rx_thread_state[]; /* RAM 0x20003ffc, struct ble_msgrx_manager */
#define MSGRX_MANAGER ((struct ble_msgrx_manager *)(void *)audio_ble_rx_thread_state)
/* osThreadAttr_t "ble_msgrx": cb 0x20072220/0x70, stack 0x2004ba98/0x4000, priority 0x30, tz_module 1. */
extern const uint8_t g2_ble_msgrx_thread_attr[]; /* ROM 0x75b880 */

extern uint32_t osThreadFlagsWait(uint32_t flags, uint32_t options, uint32_t timeout); /* 0x4492c2 */
extern void *osMessageQueueNew(uint32_t count, uint32_t size, const void *attr);     /* 0x449a32 */
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout); /* 0x449b3c */
extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr);    /* 0x4490e2 */
extern int32_t osThreadTerminate(void *thread);                                       /* 0x4491fe */
extern int32_t osDelay(uint32_t ticks);                                               /* 0x449376 */
extern uint32_t ulSetInterruptMask(void);                                             /* 0x5fa0a4 */
extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t index);   /* thread manager start sync */
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t index); /* thread manager start sync end */
extern void audio_uart_ring_sync_exit_4c9c3c(uint32_t index);              /* thread manager stop ack */
extern void file_heap_free(void *buffer);                                             /* 0x474d16 */
extern void APP_PbRxDevCfgFrameDataProcess(const uint8_t *data, uint16_t length);     /* 0x4d83d8 */
extern uint32_t semantic_OtaFrameDispatch(uint8_t command, const uint8_t *data, uint16_t len); /* 0x448670 */
extern int32_t semantic_EfsFrameDispatch(uint8_t command, const uint8_t *payload, uint16_t length); /* 0x458b60 */
extern void EFS_CancelExport(void);                                                   /* 0x458c5e */
extern void AppBleMasterPeerMgrUnpairDev(uint32_t reason, const uint8_t *address);    /* 0x4d9010 */
extern void audio_dump_hex(const char *, uint32_t, const uint8_t *, uint32_t);        /* 0x43dacc */
extern uint32_t audio_log_flags(void);                                                /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);       /* 0x43ce9e */

void threadBleMsgRxEnter(void);
void threadBleMsgRxQueueInit(void);
void threadBleMsgRxApplicationInit(void);
void threadBleMsgRxThreadInitHook(void);
void threadBleMsgRxReady(void);
void threadBleMsgRxDispatchFlags(uint32_t flags);
void _thread_pb_msg_handler(void);
/* _thread_exit is a shared stock name (0x48e34e, 0x48efc2, 0x4c53a6, 0x53880c): file-local here. */
static void _thread_exit(void);

static const char module_tag[] = "ble.msgrx"; /* ROM 0x78c638 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgrx.c"; /* ROM 0x6fe234 */
static const char task_fn[] = "thread_ble_msgrx"; /* ROM 0x7841a8 */
static const char notify_error[] = "Notify error!"; /* ROM 0x789a50 */
static const char notify_error_short[] = "[ble.msgrx]Notify error!"; /* ROM 0x7734f8 */
static const char handler_fn[] = "_thread_pb_msg_handler"; /* ROM 0x77cb44 */
static const char pair_erase[] = "EVENT_BLE_MSG_MASTER_PAIR_ERASE"; /* ROM 0x766850 */
static const char pair_erase_short[] = "[ble.msgrx]EVENT_BLE_MSG_MASTER_PAIR_ERASE"; /* ROM 0x745224 */
static const char mac_label[] = "mac"; /* ROM 0x48f128 (literal pool, adr) */
static const char exit_fn[] = "_thread_exit"; /* ROM 0x789a60 */
static const char exit_msg[] = "thread ble msgrx exit"; /* ROM 0x77cb5c */
static const char exit_short[] = "[ble.msgrx]thread ble msgrx exit"; /* ROM 0x75b9c4 */

static void trap_forever(void)
{
    (void)ulSetInterruptMask();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) {
    }
}

void threadBleMsgRxTask(void *argument)
{
    (void)argument;
    threadBleMsgRxEnter();
    threadBleMsgRxQueueInit();
    threadBleMsgRxApplicationInit();
    threadBleMsgRxThreadInitHook();
    threadBleMsgRxReady();
    for (;;) {
        uint32_t flags = osThreadFlagsWait(MSGRX_FLAGS_ALL, 0u, OS_WAIT_FOREVER);
        if (flags != 0u && flags < 0x80000000u) {
            threadBleMsgRxDispatchFlags(flags);
            continue;
        }
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, task_fn, 0x72u, notify_error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, notify_error_short, notify_error_short);
    }
}

void threadBleMsgRxApplicationInit(void)
{
}

void threadBleMsgRxQueueInit(void)
{
    MSGRX_MANAGER->queue = osMessageQueueNew(MSGRX_QUEUE_DEPTH, sizeof(void *), NULL);
    if (MSGRX_MANAGER->queue == NULL)
        trap_forever();
}

void threadBleMsgRxThreadInitHook(void)
{
}

void threadBleMsgRxEnter(void)
{
    (void)audio_uart_ring_state_transition_4c9b86(MSGRX_THREAD_INDEX);
}

void threadBleMsgRxReady(void)
{
    (void)audio_uart_ring_resource_transition_4c9be2(MSGRX_THREAD_INDEX);
}

void threadBleMsgRxInit(void)
{
    MSGRX_MANAGER->thread = osThreadNew(threadBleMsgRxTask, NULL, g2_ble_msgrx_thread_attr);
    if (MSGRX_MANAGER->thread == NULL)
        trap_forever();
}

void threadBleMsgRxDeinit(void)
{
    if (MSGRX_MANAGER->thread != NULL) {
        (void)osThreadTerminate(MSGRX_MANAGER->thread);
        MSGRX_MANAGER->thread = NULL;
    }
}

/* Drain the queue without blocking; NULL entries are skipped, every node is freed. */
void _thread_pb_msg_handler(void)
{
    msgrx_node_t *node = NULL;

    while (osMessageQueueGet(MSGRX_MANAGER->queue, &node, NULL, 0u) == 0) {
        if (node == NULL)
            continue;
        switch (node->id) {
        case MSGRX_ID_DEV_CONFIG:
            APP_PbRxDevCfgFrameDataProcess(node->payload, (uint16_t)node->length);
            break;
        case MSGRX_ID_OTA_FIRST + 0u:
        case MSGRX_ID_OTA_FIRST + 1u:
        case MSGRX_ID_OTA_FIRST + 2u:
        case MSGRX_ID_OTA_FIRST + 3u:
            (void)semantic_OtaFrameDispatch((uint8_t)node->id, node->payload, (uint16_t)node->length);
            break;
        case MSGRX_ID_EFS_FIRST + 0u:
        case MSGRX_ID_EFS_FIRST + 1u:
        case MSGRX_ID_EFS_FIRST + 2u:
        case MSGRX_ID_EFS_FIRST + 3u:
            (void)semantic_EfsFrameDispatch((uint8_t)node->id, node->payload, (uint16_t)node->length);
            break;
        case MSGRX_ID_MASTER_PAIR_ERASE:
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module_tag, source_file, handler_fn, 0xe9u, pair_erase);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compress_log_output(0x10000000u, pair_erase_short, pair_erase_short);
            audio_dump_hex(mac_label, 16u, node->payload, (uint16_t)node->length);
            AppBleMasterPeerMgrUnpairDev(3u, node->payload);
            break;
        case MSGRX_ID_EFS_CANCEL_EXPORT:
            EFS_CancelExport();
            break;
        default:
            break;
        }
        file_heap_free(node);
        node = NULL;
    }
}

void threadBleMsgRxDispatchFlags(uint32_t flags)
{
    if (flags & MSGRX_FLAG_QUEUE)
        _thread_pb_msg_handler();
    if (flags & MSGRX_FLAG_EXIT)
        _thread_exit();
}

static void _thread_exit(void)
{
    audio_uart_ring_sync_exit_4c9c3c(MSGRX_THREAD_INDEX);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, exit_fn, 0x10au, exit_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, exit_short, exit_short);
    for (;;)
        (void)osDelay(OS_WAIT_FOREVER);
}
