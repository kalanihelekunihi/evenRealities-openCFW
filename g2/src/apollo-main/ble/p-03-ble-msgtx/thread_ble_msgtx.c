/* BLE message-transmit thread, stock D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_msgtx.c.
 * Native 0x475290..0x475523, 0x475a38..0x475aa5 and 0x475d78..0x475ed3
 * (literal pools 0x475d60..0x475d77, 0x475e64..0x475fbf).
 * Owned elsewhere in the same stock file: Thread_BleMsgtxQueueClear 0x475524
 * (ble/ble-queue/ble_queue_clear.c), Thread_MsgTxByBle 0x47564e (ble/ble-msg/display_ble_msg_tx.c,
 * audio_ble_msg_tx), Thread_MsgPbNotifyByBleDirect 0x475aa6, Thread_MsgPbTxByBle 0x475b14.
 *
 * Producers allocate a heap node and queue its pointer (150-entry queue) then raise thread
 * flag bit 22. Node layout: +0 pipe bit (1 protobuf/TPL, 2 ESS streaming, 4 EFS, 8 transport-3),
 * +4 length, and for the framed pipes +8 notify flag, +9 type, +10 command, +11 payload
 * (length counts those three header bytes). Bit 23 terminates the thread. */
#include <stdint.h>
#include <stddef.h>

#define MSGTX_THREAD_INDEX 8u
#define MSGTX_QUEUE_DEPTH 150u
#define MSGTX_FLAG_QUEUE 0x00400000u
#define MSGTX_FLAG_EXIT 0x00800000u
#define MSGTX_FLAGS_ALL 0x00ffffffu
#define OS_WAIT_FOREVER 0xffffffffu
#define ESS_WAIT_TICKS 50u

enum { MSGTX_NODE_PB = 1u, MSGTX_NODE_ESS = 2u, MSGTX_NODE_EFS = 4u, MSGTX_NODE_TRANSPORT3 = 8u };
enum { PIPE_PB = 0u, PIPE_ESS = 1u, PIPE_EFS = 2u, PIPE_TRANSPORT3 = 3u };

typedef struct {
    uint32_t kind;    /* +0x0 */
    uint32_t length;  /* +0x4 */
    uint8_t notify;   /* +0x8 (ESS payload starts here) */
    uint8_t type;     /* +0x9 */
    uint8_t command;  /* +0xa */
    uint8_t payload[]; /* +0xb */
} msgtx_node_t;

struct ble_msgtx_manager {
    uint8_t reserved[8];
    void *thread; /* +0x8 */
    void *queue;  /* +0xc */
};
_Static_assert(sizeof(struct ble_msgtx_manager) == 16u, "BLE manager ABI");

extern struct ble_msgtx_manager audio_ble_msgtx_manager; /* RAM 0x20004020 */
/* osThreadAttr_t "ble_msgtx": cb 0x200721b0/0x70, stack 0x20047a98/0x4000, priority 0x30, tz_module 1. */
extern const uint8_t g2_ble_msgtx_thread_attr[]; /* ROM 0x75b85c */

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
extern void audio_file_heap_free(void *buffer);                                       /* 0x474d16 */
extern uint32_t TPL_SendPacket(uint8_t channel, uint8_t notify, uint8_t type, uint8_t command,
                               const uint8_t *payload, uint16_t length);              /* 0x4b9640 */
extern uint32_t threadBleWsfWaitOnce(uint32_t timeout);                               /* 0x4d0c2c */
extern uint32_t APP_BleEssSendDataMsg(const uint8_t *data, uint16_t length);          /* 0x4be2f6 */
extern uint32_t efs_transport_send_4d12de(uint8_t notify, uint8_t type, uint8_t command,
                                          const uint8_t *payload, uint16_t length);
extern uint32_t ota_transport_send_48de40(uint8_t notify, uint8_t type, uint8_t command,
                                          const uint8_t *payload, uint16_t length);
extern uint32_t audio_ota_transfer_active(void);                                      /* 0x4487ac */
extern uint32_t audio_ble_msg_tx(uint8_t piping, uint8_t notify, uint8_t type, uint8_t command,
                                 const void *payload, uint16_t length);              /* 0x47564e */
extern uint32_t audio_log_flags(void);                                                /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);       /* 0x43ce9e */

void threadBleMsgTxEnter(void);
void threadBleMsgTxQueueInit(void);
void threadBleMsgTxApplicationInit(void);
void threadBleMsgTxThreadInitHook(void);
void threadBleMsgTxReady(void);
void threadBleMsgTxDispatchFlags(uint32_t flags);
void threadBleMsgTxQueueDrain(void);
void threadBleMsgTxExit(void);

static const char module_tag[] = "ble.msgtx"; /* ROM 0x78c644 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgtx.c"; /* ROM 0x6fe2c4 */
static const char task_fn[] = "thread_ble_msgtx"; /* ROM 0x7841d0 */
static const char notify_error[] = "Notify error!"; /* ROM 0x789a70 */
static const char notify_error_short[] = "[ble.msgtx]Notify error!"; /* ROM 0x77354c */
static const char handler_fn[] = "_thread_msg_handler"; /* ROM 0x7841e4 */
static const char ess_skipped[] = "ESS send skipped: semaphore not available, dropping message"; /* ROM 0x719f6c */
static const char ess_skipped_short[] =
    "[ble.msgtx]ESS send skipped: semaphore not available, dropping message"; /* ROM 0x6fe30c */
static const char exit_fn[] = "_thread_exit"; /* ROM 0x789a80 */
static const char exit_msg[] = "thread ble msgtx exit"; /* ROM 0x77cb74 */
static const char exit_short[] = "[ble.msgtx]thread ble msgtx exit"; /* ROM 0x75ba0c */
static const char pb_direct_fn[] = "Thread_MsgPbTxDirectByBle"; /* ROM 0x773584 */
static const char pb_direct_ota[] = "OTA is going, pb tx direct failed"; /* ROM 0x75ba54 */
static const char pb_direct_ota_short[] = "[ble.msgtx]OTA is going, pb tx direct failed"; /* ROM 0x739ca4 */
static const char streaming_fn[] = "Thread_MsgStreamingNotifyByBle"; /* ROM 0x766970 */
static const char streaming_ota[] = "OTA is going, streaming notify failed"; /* ROM 0x74fc94 */
static const char streaming_ota_short[] = "[ble.msgtx]OTA is going, streaming notify failed"; /* ROM 0x72f0c0 */
static const char efs_tx_fn[] = "Thread_MsgEfsTxByBle"; /* ROM 0x77cbd4 */
static const char efs_tx_ota[] = "OTA is going, efs tx failed"; /* ROM 0x7735d8 */
static const char efs_tx_ota_short[] = "[ble.msgtx]OTA is going, efs tx failed"; /* ROM 0x74fcbc */
static const char efs_notify_fn[] = "Thread_MsgEfsNotifyByBle"; /* ROM 0x7735f4 */
static const char efs_notify_ota[] = "OTA is going, efs notify failed"; /* ROM 0x766990 */
static const char efs_notify_ota_short[] = "[ble.msgtx]OTA is going, efs notify failed"; /* ROM 0x745434 */

static void trap_forever(void)
{
    (void)ulSetInterruptMask();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) {
    }
}

void threadBleMsgTxTask(void *argument)
{
    (void)argument;
    threadBleMsgTxEnter();
    threadBleMsgTxQueueInit();
    threadBleMsgTxApplicationInit();
    threadBleMsgTxThreadInitHook();
    threadBleMsgTxReady();
    for (;;) {
        uint32_t flags = osThreadFlagsWait(MSGTX_FLAGS_ALL, 0u, OS_WAIT_FOREVER);
        if (flags != 0u && flags < 0x80000000u) {
            threadBleMsgTxDispatchFlags(flags);
            continue;
        }
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, task_fn, 0x67u, notify_error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, notify_error_short, notify_error_short);
    }
}

void threadBleMsgTxApplicationInit(void)
{
}

void threadBleMsgTxQueueInit(void)
{
    audio_ble_msgtx_manager.queue = osMessageQueueNew(MSGTX_QUEUE_DEPTH, sizeof(void *), NULL);
    if (audio_ble_msgtx_manager.queue == NULL)
        trap_forever();
}

void threadBleMsgTxThreadInitHook(void)
{
}

void threadBleMsgTxEnter(void)
{
    (void)audio_uart_ring_state_transition_4c9b86(MSGTX_THREAD_INDEX);
}

void threadBleMsgTxReady(void)
{
    (void)audio_uart_ring_resource_transition_4c9be2(MSGTX_THREAD_INDEX);
}

void threadBleMsgTxInit(void)
{
    audio_ble_msgtx_manager.thread = osThreadNew(threadBleMsgTxTask, NULL, g2_ble_msgtx_thread_attr);
    if (audio_ble_msgtx_manager.thread == NULL)
        trap_forever();
}

void threadBleMsgTxDeinit(void)
{
    if (audio_ble_msgtx_manager.thread != NULL) {
        (void)osThreadTerminate(audio_ble_msgtx_manager.thread);
        audio_ble_msgtx_manager.thread = NULL;
    }
}

/* Stock _thread_msg_handler: send every queued node on its pipe, then free it. */
void threadBleMsgTxQueueDrain(void)
{
    msgtx_node_t *node = NULL;

    while (osMessageQueueGet(audio_ble_msgtx_manager.queue, &node, NULL, 0u) == 0 && node != NULL) {
        switch (node->kind) {
        case MSGTX_NODE_PB:
            (void)TPL_SendPacket(0u, node->notify != 0u, node->type, node->command, node->payload,
                                 (uint16_t)(node->length - 3u));
            break;
        case MSGTX_NODE_ESS:
            if (threadBleWsfWaitOnce(ESS_WAIT_TICKS) != 0u) {
                (void)APP_BleEssSendDataMsg(&node->notify, (uint16_t)node->length);
            } else {
                if (audio_log_flags() & 2u)
                    audio_log_extended(2u, module_tag, source_file, handler_fn, 0xceu, ess_skipped);
                if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                    (void)compress_log_output(0x08000000u, ess_skipped_short, ess_skipped_short);
            }
            break;
        case MSGTX_NODE_EFS:
            (void)efs_transport_send_4d12de(node->notify != 0u, node->type, node->command, node->payload,
                                            (uint16_t)(node->length - 3u));
            break;
        case MSGTX_NODE_TRANSPORT3:
            (void)ota_transport_send_48de40(node->notify != 0u, node->type, node->command, node->payload,
                                            (uint16_t)(node->length - 3u));
            break;
        default:
            break;
        }
        audio_file_heap_free(node);
        node = NULL;
    }
}

void threadBleMsgTxDispatchFlags(uint32_t flags)
{
    if (flags & MSGTX_FLAG_QUEUE)
        threadBleMsgTxQueueDrain();
    if (flags & MSGTX_FLAG_EXIT)
        threadBleMsgTxExit();
}

void threadBleMsgTxExit(void)
{
    audio_uart_ring_sync_exit_4c9c3c(MSGTX_THREAD_INDEX);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, exit_fn, 0xfdu, exit_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, exit_short, exit_short);
    for (;;)
        (void)osDelay(OS_WAIT_FOREVER);
}

/* Each public sender refuses while an OTA transfer owns the link (EFS notify reports 8). */
uint32_t Thread_MsgPbTxByBleDirect(uint8_t type, uint8_t command, const void *payload, uint16_t length)
{
    if (audio_ota_transfer_active() == 0u)
        return audio_ble_msg_tx(PIPE_PB, 0u, type, command, payload, length);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, pb_direct_fn, 0x198u, pb_direct_ota);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, pb_direct_ota_short, pb_direct_ota_short);
    return 0u;
}

uint32_t Thread_MsgStreamingNotifyByBle(const void *payload, uint16_t length)
{
    if (audio_ota_transfer_active() == 0u)
        return audio_ble_msg_tx(PIPE_ESS, 1u, 0u, 0u, payload, length);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, streaming_fn, 0x1e9u, streaming_ota);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, streaming_ota_short, streaming_ota_short);
    return 0u;
}

uint32_t Thread_MsgTransport3TxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length)
{
    return audio_ble_msg_tx(PIPE_TRANSPORT3, 0u, type, command, payload, length);
}

uint32_t Thread_MsgEfsTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length)
{
    if (audio_ota_transfer_active() == 0u)
        return audio_ble_msg_tx(PIPE_EFS, 0u, type, command, payload, length);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, efs_tx_fn, 0x1fdu, efs_tx_ota);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, efs_tx_ota_short, efs_tx_ota_short);
    return 0u;
}

uint32_t Thread_MsgEfsNotifyByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length)
{
    if (audio_ota_transfer_active() == 0u)
        return audio_ble_msg_tx(PIPE_EFS, 1u, type, command, payload, length);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, efs_notify_fn, 0x207u, efs_notify_ota);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, efs_notify_ota_short, efs_notify_ota_short);
    return 8u;
}
