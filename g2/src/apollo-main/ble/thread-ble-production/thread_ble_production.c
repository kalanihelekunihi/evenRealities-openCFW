/* BLE production-test thread, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_production.c
 * (module tag "task.ble_production"). Native 0x5382e4..0x538b46, literal
 * pool 0x538b48..0x538c23.
 *
 * One CMSIS thread ("ble_production", priority 33, 4 KiB stack) owns a
 * 3-entry queue of block pointers and a 3 x 260-byte memory pool. Producers
 * (the NUS/production RX path) call Thread_SendMsgToBleProductionTask, which
 * copies the frame into a zeroed pool block, queues the pointer and sets
 * thread flag 0x400000; flag 0x800000 is the thread-manager stop request.
 *
 * A queued block is either an ASCII "AT..." command (handed to AT_Handler)
 * or a production-test frame:
 *   +0 0x5A  +1 0xA5  +2 0x7F  +3 payload length N  +4 payload[N]  +4+N sum8
 * where sum8 is the low byte of the sum of bytes 0..N+3. Valid frames go to
 * pt_protocol_dispatch; a non-empty response is returned over NUS and a
 * response whose byte 4 is 0x0B, or 0x01 with byte 8 == 0, resets the system
 * after 1000 ticks. */
#include <stdint.h>
#include <stddef.h>

/* CMSIS-RTOS2 osThreadAttr_t. */
typedef struct {
    const char *name;    /* +0x00 */
    uint32_t attr_bits;  /* +0x04 */
    void *cb_mem;        /* +0x08 */
    uint32_t cb_size;    /* +0x0c */
    void *stack_mem;     /* +0x10 */
    uint32_t stack_size; /* +0x14 */
    int32_t priority;    /* +0x18 osPriority_t */
    uint32_t tz_module;  /* +0x1c */
    uint32_t reserved;   /* +0x20 */
} ble_production_thread_attr_t;
_Static_assert(sizeof(ble_production_thread_attr_t) == 36u, "osThreadAttr_t");

/* Thread context at RAM 0x20004044 (next context starts at 0x20004068). */
typedef struct {
    void (*init)(void);      /* +0x00 */
    void (*deinit)(void);    /* +0x04 */
    void *thread;            /* +0x08 osThreadId_t */
    void *queue;             /* +0x0c osMessageQueueId_t, 3 x 4-byte pointers */
    uint32_t reserved_10;    /* +0x10 */
    uint32_t reserved_14;    /* +0x14 */
    void *pool;              /* +0x18 osMemoryPoolId_t, 3 x 260-byte blocks */
    uint32_t reserved_1c;    /* +0x1c */
    uint32_t reserved_20;    /* +0x20 */
} ble_production_context_t;
_Static_assert(sizeof(ble_production_context_t) == 0x24u, "thread context stride");

/* Production-test frame header. */
typedef struct {
    uint8_t flag_1;       /* +0 0x5A */
    uint8_t flag_2;       /* +1 0xA5 */
    uint8_t flag_3;       /* +2 0x7F */
    uint8_t pay_load_len; /* +3 */
} ble_production_msg_head_t;

#define BLE_PRODUCTION_THREAD_INDEX 11u /* thread-manager slot */
#define BLE_PRODUCTION_FLAG_MESSAGE 0x400000u
#define BLE_PRODUCTION_FLAG_EXIT 0x800000u
#define BLE_PRODUCTION_BLOCK_SIZE 0x104u
#define BLE_PRODUCTION_RESPONSE_SIZE 0x100u

extern ble_production_context_t g2_ble_production_context; /* RAM 0x20004044 */
extern uint8_t g2_ble_production_thread_cb[];             /* RAM 0x200723e0, static TCB 112 B */
extern uint8_t g2_ble_production_thread_stack[];          /* RAM 0x2036de40, 4096 B */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format,
                                    const char *copy, ...); /* 0x43ce9e */
extern void audio_dump_hex(const char *label, uint32_t width,
                           const uint8_t *data, uint32_t length); /* 0x43dacc */

/* Thread manager (thread_manager.c). */
extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t index);    /* sysstart sync */
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t index); /* sysstart sync end */
extern void audio_uart_ring_sync_exit_4c9c3c(uint32_t index);               /* stop ack */

/* CMSIS-RTOS2. */
extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr); /* 0x4490e2 */
extern int32_t osThreadTerminate(void *thread);                                /* 0x4491fe */
extern uint32_t osThreadFlagsSet(void *thread, uint32_t flags);                /* 0x449238 */
extern uint32_t osThreadFlagsWait(uint32_t flags, uint32_t options, uint32_t timeout); /* 0x4492c2 */
extern int32_t osDelay(uint32_t ticks);                                        /* 0x449376 */
extern void *osMessageQueueNew(uint32_t count, uint32_t size, const void *attr); /* 0x449a32 */
extern int32_t osMessageQueuePut(void *queue, const void *msg, uint8_t prio, uint32_t timeout); /* 0x449abe */
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout); /* 0x449b3c */
extern int32_t osMessageQueueDelete(void *queue);                              /* 0x449bec */
extern void *osMemoryPoolNew(uint32_t count, uint32_t size, const void *attr); /* 0x449c14 */
extern void *osMemoryPoolAlloc(void *pool, uint32_t timeout);                  /* 0x449d3e */
extern int32_t osMemoryPoolFree(void *pool, void *block);                      /* 0x449dd4 */
extern uint32_t audio_wsf_interrupt_mask_set(void);                            /* ulSetInterruptMask 0x5fa0a4 */

/* Helpers and consumers. */
extern void audio_uart_buffer_zero(void *buffer, uint32_t length, uint32_t fill);        /* memset 0x43c0e4 */
extern void audio_uart_checksum_copy(void *destination, const void *source, uint32_t length); /* memcpy 0x439be4 */
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t count);        /* 0x44b610 */
extern void audio_ble_radio_ready_44b0ae(void);                                        /* system reset via 0x44ab24 */
extern void AT_Handler(char *command);                                                 /* 0x54136c */
extern uint32_t pt_protocol_dispatch(const uint8_t *payload, uint8_t length,
                                     uint8_t *response, uint8_t *response_length);     /* 0x56f4a0 */
extern uint32_t APP_BleNusSendDataMsg(const uint8_t *data, uint16_t length);           /* 0x4be856 */

static const char module[] = "task.ble_production"; /* ROM 0x784220 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_production.c"; /* ROM 0x6f06c8 */
static const char thread_name[] = "ble_production"; /* ROM 0x789990 */

static const char fn_task[] = "thread_ble_production"; /* ROM 0x77cbec */
static const char notify_error[] = "Notify error!"; /* ROM 0x789a90 */
static const char notify_error_s[] = "[task.ble_production]Notify error!"; /* ROM 0x75ba9c */

static const char fn_msg[] = "_thread_msg_handler"; /* ROM 0x784234 */
static const char at_cmd[] = "AT cmd"; /* ROM 0x78ebc4 */
static const char at_cmd_s[] = "[task.ble_production]AT cmd"; /* ROM 0x773610 */
static const char msg_handler[] = "ble_production_task_msg_handler p_msg "; /* ROM 0x74fce4 */
static const char msg_handler_s[] = "[task.ble_production]ble_production_task_msg_handler p_msg "; /* ROM 0x719fe4 */
static const char msg_ptr[] = "p_msg = %p"; /* ROM 0x78c650 */
static const char msg_ptr_s[] = "[task.ble_production]p_msg = %p"; /* ROM 0x7669b0 */
static const char msg_str[] = "p_msg = %s"; /* ROM 0x78c65c */
static const char msg_str_s[] = "[task.ble_production]p_msg = %s"; /* ROM 0x7669d0 */
static const char flag_1[] = "p_msg->head.flag_1 = 0x%02X"; /* ROM 0x77362c */
static const char flag_1_s[] = "[task.ble_production]p_msg->head.flag_1 = 0x%02X"; /* ROM 0x72f0f4 */
static const char flag_2[] = "p_msg->head.flag_2 = 0x%02X"; /* ROM 0x773648 */
static const char flag_2_s[] = "[task.ble_production]p_msg->head.flag_2 = 0x%02X"; /* ROM 0x72f128 */
static const char flag_3[] = "p_msg->head.flag_3 = 0x%02X"; /* ROM 0x773664 */
static const char flag_3_s[] = "[task.ble_production]p_msg->head.flag_3 = 0x%02X"; /* ROM 0x72f15c */
static const char pay_len[] = "p_msg->head.pay_load_len = %d"; /* ROM 0x7669f0 */
static const char pay_len_s[] = "[task.ble_production]p_msg->head.pay_load_len = %d"; /* ROM 0x72f190 */
static const char content[] = "p_msg->msg_buf content:"; /* ROM 0x77cc04 */
static const char content_s[] = "[task.ble_production]p_msg->msg_buf content:"; /* ROM 0x739cd4 */
static const char dump_label[] = "production"; /* ROM 0x78c668 */
static const char send_len[] = "send data len = %d"; /* ROM 0x784248 */
static const char send_len_s[] = "[task.ble_production]send data len = %d"; /* ROM 0x74fd0c */
static const char at_prefix[] = "AT"; /* ROM 0x538808, inline after _thread_notify_event_handler */

static const char fn_notify[] = "_thread_notify_event_handler"; /* ROM 0x766a10 */
static const char notify_value_fmt[] = "notifyValue = 0x%x"; /* ROM 0x78425c */
static const char notify_value_s[] = "[task.ble_production]notifyValue = 0x%x"; /* ROM 0x74fd34 */

static const char fn_exit[] = "_thread_exit"; /* ROM 0x789aa0 */
static const char queue_deleted[] = "ble production message queue deleted"; /* ROM 0x74fd5c */
static const char queue_deleted_s[] = "[task.ble_production]ble production message queue deleted"; /* ROM 0x71a020 */
static const char thread_exit[] = "thread ble production exit"; /* ROM 0x773680 */
static const char thread_exit_s[] = "[task.ble_production]thread ble production exit"; /* ROM 0x739d04 */

static const char fn_head[] = "_thread_ble_production_msg_head_check"; /* ROM 0x74fd84 */
static const char head_fail[] = "ble production msg head check failed"; /* ROM 0x74fdac */
static const char head_fail_s[] = "[task.ble_production]ble production msg head check failed"; /* ROM 0x71a05c */

static const char fn_crc[] = "_thread_ble_production_msg_crc_check"; /* ROM 0x74fdd4 */
static const char crc_fail[] = "ble production msg crc check failed"; /* ROM 0x75bac0 */
static const char crc_fail_s[] = "[task.ble_production]ble production msg crc check failed"; /* ROM 0x71a098 */

static const char fn_send[] = "Thread_SendMsgToBleProductionTask"; /* ROM 0x75bae4 */
static const char send_pdata[] = "ble_production_task_msg_send pdata"; /* ROM 0x75bb08 */
static const char send_pdata_s[] = "[task.ble_production]ble_production_task_msg_send pdata"; /* ROM 0x7248b8 */
static const char pdata_null[] = "msg ble production pdata is null"; /* ROM 0x75bb2c */
static const char pdata_null_s[] = "[task.ble_production]msg ble production pdata is null"; /* ROM 0x7248f0 */
static const char queue_null[] = "g_thread_ble_production queue or h_poolIDnull"; /* ROM 0x739d34 */
static const char queue_null_s[] = "[task.ble_production]g_thread_ble_production queue or h_poolIDnull"; /* ROM 0x707250 */
static const char alloc_fail[] = "ble_production_task_msg_send alloc fail"; /* ROM 0x74fdfc */
static const char alloc_fail_s[] = "[task.ble_production]ble_production_task_msg_send alloc fail"; /* ROM 0x710464 */
static const char send_miss[] = "msg dispatch send msg miss"; /* ROM 0x77369c */
static const char send_miss_s[] = "[task.ble_production]msg dispatch send msg miss"; /* ROM 0x739d64 */

/* Stock LOG expansion. */
#define BP_LOG(level, mask, function, line, format, simple, ...)                \
    do {                                                                        \
        if (audio_log_flags() & 2u)                                             \
            audio_log_extended((level), module, file, (function), (line),       \
                               (format), ##__VA_ARGS__);                        \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))               \
            (void)compress_log_output((mask), (simple), (simple),               \
                                      ##__VA_ARGS__);                           \
    } while (0)

/* Stock configASSERT on a NULL RTOS object: mask interrupts and fault. */
#define BP_ASSERT_NOT_NULL(object)                                              \
    do {                                                                        \
        if ((object) == NULL) {                                                 \
            (void)audio_wsf_interrupt_mask_set();                               \
            *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;                   \
            for (;;) {}                                                         \
        }                                                                       \
    } while (0)

static const ble_production_thread_attr_t ble_production_thread_attr = {
    thread_name, 0u, g2_ble_production_thread_cb, 0x70u,
    g2_ble_production_thread_stack, 0x1000u, 33 /* osPriorityBelowNormal1 */, 1u, 0u,
}; /* ROM 0x75b910 */

void threadBleProductionTask(void *argument);
void threadBleProductionLoopInit(void);
void threadBleProductionStart(void);
void threadBleProductionEnter(void);
void threadBleProductionReady(void);
void threadBleProductionInit(void);
void threadBleProductionDeinit(void);
uint8_t _thread_ble_production_msg_head_check(const uint8_t *msg);
uint8_t _thread_ble_production_msg_crc_check(const uint8_t *msg);
int32_t Thread_SendMsgToBleProductionTask(const void *data, uint16_t length);

/* These four names recur in other stock thread_*.c files; static here. */
static void _thread_resource_init(void);
static void _thread_msg_handler(void);
static void _thread_notify_event_handler(uint32_t notify_value);
static void _thread_exit(void);

/* 0x5382e4: thread entry. A wait result of 0 or an osError code is logged
 * and the wait repeats. */
void threadBleProductionTask(void *argument)
{
    uint32_t flags;

    (void)argument;
    threadBleProductionEnter();
    _thread_resource_init();
    threadBleProductionLoopInit();
    threadBleProductionStart();
    threadBleProductionReady();
    for (;;) {
        flags = osThreadFlagsWait(0x00ffffffu, 0u, 0xffffffffu);
        if (flags != 0u && flags < 0x80000000u) {
            _thread_notify_event_handler(flags);
            continue;
        }
        BP_LOG(1u, 0x04000000u, fn_task, 99u, notify_error, notify_error_s);
    }
}

/* 0x53835c */
void threadBleProductionLoopInit(void)
{
}

/* 0x53835e: 3-entry pointer queue and 3 x 260-byte block pool, both on the
 * RTOS heap. */
static __attribute__((noinline)) void _thread_resource_init(void)
{
    ble_production_context_t *ctx = &g2_ble_production_context;

    ctx->queue = osMessageQueueNew(3u, sizeof(void *), NULL);
    BP_ASSERT_NOT_NULL(ctx->queue);
    ctx->pool = osMemoryPoolNew(3u, BLE_PRODUCTION_BLOCK_SIZE, NULL);
    BP_ASSERT_NOT_NULL(ctx->pool);
}

/* 0x5383a8 */
void threadBleProductionStart(void)
{
}

/* 0x5383aa: thread-manager start barrier for slot 11. */
void threadBleProductionEnter(void)
{
    (void)audio_uart_ring_state_transition_4c9b86(BLE_PRODUCTION_THREAD_INDEX);
}

/* 0x5383b4: thread-manager "start done" for slot 11. */
void threadBleProductionReady(void)
{
    (void)audio_uart_ring_resource_transition_4c9be2(BLE_PRODUCTION_THREAD_INDEX);
}

/* 0x5383be */
void threadBleProductionInit(void)
{
    ble_production_context_t *ctx = &g2_ble_production_context;

    ctx->thread = osThreadNew(threadBleProductionTask, NULL, &ble_production_thread_attr);
    BP_ASSERT_NOT_NULL(ctx->thread);
}

/* 0x5383ea */
void threadBleProductionDeinit(void)
{
    ble_production_context_t *ctx = &g2_ble_production_context;

    if (ctx->thread != NULL) {
        (void)osThreadTerminate(ctx->thread);
        ctx->thread = NULL;
    }
}

/* 0x538402: drain the queue without blocking. The AT path frees its block
 * but leaves the local pointer set; the next osMessageQueueGet overwrites it. */
static __attribute__((noinline)) void _thread_msg_handler(void)
{
    ble_production_context_t *ctx;
    uint8_t response_length;
    uint8_t *p_msg = NULL;
    uint8_t response[BLE_PRODUCTION_RESPONSE_SIZE];

    for (;;) {
        ctx = &g2_ble_production_context;
        if (osMessageQueueGet(ctx->queue, &p_msg, NULL, 0u) != 0)
            return;
        BP_LOG(3u, 0x0c000000u, fn_msg, 188u, msg_handler, msg_handler_s);
        BP_LOG(3u, 0x0c400000u, fn_msg, 189u, msg_ptr, msg_ptr_s, p_msg);
        if (p_msg == NULL)
            return;
        BP_LOG(4u, 0x10400000u, fn_msg, 193u, msg_str, msg_str_s, p_msg);
        if (audio_l2c_strncmp((const char *)p_msg, at_prefix, 2u) == 0) {
            BP_LOG(3u, 0x0c000000u, fn_msg, 195u, at_cmd, at_cmd_s);
            AT_Handler((char *)p_msg);
            (void)osMemoryPoolFree(ctx->pool, p_msg);
            continue;
        }
        BP_LOG(3u, 0x0c400000u, fn_msg, 200u, flag_1, flag_1_s, p_msg[0]);
        BP_LOG(3u, 0x0c400000u, fn_msg, 201u, flag_2, flag_2_s, p_msg[1]);
        BP_LOG(3u, 0x0c400000u, fn_msg, 202u, flag_3, flag_3_s, p_msg[2]);
        BP_LOG(3u, 0x0c400000u, fn_msg, 203u, pay_len, pay_len_s, p_msg[3]);
        BP_LOG(3u, 0x0c000000u, fn_msg, 204u, content, content_s);
        audio_dump_hex(dump_label, 16u, p_msg + 4, (uint16_t)p_msg[3]);
        response_length = 0u;
        audio_uart_buffer_zero(response, sizeof response, 0u);
        if (_thread_ble_production_msg_head_check(p_msg) != 0u &&
            _thread_ble_production_msg_crc_check(p_msg) != 0u) {
            (void)pt_protocol_dispatch(p_msg + 4, p_msg[3], response, &response_length);
            if (response_length != 0u) {
                (void)APP_BleNusSendDataMsg(response, (uint16_t)response_length);
                /* Response command 0x0B, or command 0x01 with status 0. */
                if (response[4] == 0x0bu || (response[4] == 0x01u && response[8] == 0u)) {
                    (void)osDelay(1000u);
                    audio_ble_radio_ready_44b0ae();
                }
            }
            BP_LOG(4u, 0x10400000u, fn_msg, 226u, send_len, send_len_s, response_length);
        }
        (void)osMemoryPoolFree(ctx->pool, p_msg);
        p_msg = NULL;
    }
}

/* 0x5387aa */
static __attribute__((noinline)) void _thread_notify_event_handler(uint32_t notify_value)
{
    BP_LOG(4u, 0x10400000u, fn_notify, 235u, notify_value_fmt, notify_value_s, notify_value);
    if ((notify_value & BLE_PRODUCTION_FLAG_MESSAGE) != 0u)
        _thread_msg_handler();
    if ((notify_value & BLE_PRODUCTION_FLAG_EXIT) != 0u)
        _thread_exit();
}

/* 0x53880c: acknowledge the stop to the thread manager, release the queue
 * (the pool is kept), then park forever. */
static __attribute__((noinline)) void _thread_exit(void)
{
    ble_production_context_t *ctx;

    audio_uart_ring_sync_exit_4c9c3c(BLE_PRODUCTION_THREAD_INDEX);
    ctx = &g2_ble_production_context;
    if (ctx->queue != NULL) {
        (void)osMessageQueueDelete(ctx->queue);
        ctx->queue = NULL;
        BP_LOG(4u, 0x10000000u, fn_exit, 259u, queue_deleted, queue_deleted_s);
    }
    BP_LOG(4u, 0x10000000u, fn_exit, 261u, thread_exit, thread_exit_s);
    for (;;)
        (void)osDelay(0xffffffffu);
}

/* 0x5388b6 */
uint8_t _thread_ble_production_msg_head_check(const uint8_t *msg)
{
    const ble_production_msg_head_t *head = (const ble_production_msg_head_t *)msg;
    uint8_t ok = 0u;

    if (head->flag_1 == 0x5au && head->flag_2 == 0xa5u && head->flag_3 == 0x7fu)
        ok = 1u;
    else
        BP_LOG(1u, 0x04000000u, fn_head, 276u, head_fail, head_fail_s);
    return ok;
}

/* 0x538910: 8-bit sum over header and payload against the trailing byte. */
uint8_t _thread_ble_production_msg_crc_check(const uint8_t *msg)
{
    uint8_t ok = 0u;
    uint32_t sum;
    uint16_t i;

    if (msg == NULL)
        return ok;
    sum = 0u;
    for (i = 0u; i < (uint32_t)msg[3] + 4u; i++)
        sum += msg[i];
    if ((uint8_t)sum == msg[msg[3] + 4u])
        ok = 1u;
    else
        BP_LOG(1u, 0x04000000u, fn_crc, 305u, crc_fail, crc_fail_s);
    return ok;
}

/* 0x538992: copy into a zeroed pool block (first 256 bytes cleared) and
 * queue its pointer. Returns 0 or -1. */
int32_t Thread_SendMsgToBleProductionTask(const void *data, uint16_t length)
{
    ble_production_context_t *ctx;
    void *block;

    BP_LOG(3u, 0x0c000000u, fn_send, 313u, send_pdata, send_pdata_s);
    if (data == NULL) {
        BP_LOG(1u, 0x04000000u, fn_send, 315u, pdata_null, pdata_null_s);
        return -1;
    }
    ctx = &g2_ble_production_context;
    if (ctx->queue == NULL || ctx->pool == NULL) {
        BP_LOG(1u, 0x04000000u, fn_send, 320u, queue_null, queue_null_s);
        return -1;
    }
    block = NULL;
    block = osMemoryPoolAlloc(ctx->pool, 0u);
    if (block == NULL) {
        BP_LOG(1u, 0x04000000u, fn_send, 328u, alloc_fail, alloc_fail_s);
        return -1;
    }
    audio_uart_buffer_zero(block, BLE_PRODUCTION_RESPONSE_SIZE, 0u);
    audio_uart_checksum_copy(block, data, length);
    if (osMessageQueuePut(ctx->queue, &block, 0u, 0u) != 0) {
        BP_LOG(1u, 0x04000000u, fn_send, 337u, send_miss, send_miss_s);
        (void)osMemoryPoolFree(ctx->pool, block);
        return -1;
    }
    (void)osThreadFlagsSet(ctx->thread, BLE_PRODUCTION_FLAG_MESSAGE);
    return 0;
}
