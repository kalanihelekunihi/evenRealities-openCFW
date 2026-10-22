/* Notification thread, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_notification.c
 * (module tag "task.notif"). Native 0x48e154..0x48e42d, literal pool
 * 0x48e430..0x48e483.
 *
 * One CMSIS thread ("msg_notif", priority 34, 8 KiB stack) owns a 50-entry
 * queue of heap message pointers. Thread flags: 0x400000 drain the queue,
 * 0x000002 reload the whitelist (EFS service after a whitelist write),
 * 0x800000 thread-manager stop request. A queued message is
 *   +0 u32 type (4 = protobuf notification frame, 0x101 = ANCC notification)
 *   +4 u32 length (low 16 bits used)   +8 payload
 * and is released with file_heap_free after dispatch. */
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
} notif_thread_attr_t;
_Static_assert(sizeof(notif_thread_attr_t) == 36u, "osThreadAttr_t");

/* Thread-manager descriptor at RAM 0x200040fc (slot 1, stride 0x24). */
typedef struct {
    void (*init)(void);   /* +0x00 */
    void (*deinit)(void); /* +0x04 */
    void *thread;         /* +0x08 osThreadId_t */
    void *queue;          /* +0x0c osMessageQueueId_t, 50 x 4-byte pointers */
    uint32_t reserved[5]; /* +0x10 */
} notif_context_t;
_Static_assert(sizeof(notif_context_t) == 0x24u, "thread context stride");

typedef struct {
    uint32_t type;      /* +0 */
    uint32_t length;    /* +4 */
    uint8_t payload[];  /* +8 */
} notif_msg_t;

#define NOTIF_THREAD_INDEX 1u
#define NOTIF_FLAG_WHITELIST 0x000002u
#define NOTIF_FLAG_MESSAGE 0x400000u
#define NOTIF_FLAG_EXIT 0x800000u
#define NOTIF_MSG_PB_NOTIFICATION 4u
#define NOTIF_MSG_ANCC 0x101u

extern notif_context_t g2_notif_thread_context;  /* RAM 0x200040fc */
extern uint8_t g2_notif_thread_cb[];             /* RAM 0x20072450, static TCB 0x70 B */
extern uint8_t g2_notif_thread_stack[];          /* RAM 0x20362e18, 0x2000 B */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format,
                                    const char *copy, ...); /* 0x43ce9e */

extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t index);    /* sysstart sync */
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t index); /* sysstart sync end */
extern void audio_uart_ring_sync_exit_4c9c3c(uint32_t index);               /* stop ack */

extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr); /* 0x4490e2 */
extern int32_t osThreadTerminate(void *thread);                                /* 0x4491fe */
extern uint32_t osThreadFlagsSet(void *thread, uint32_t flags);                /* 0x449238 */
extern uint32_t osThreadFlagsWait(uint32_t flags, uint32_t options, uint32_t timeout); /* 0x4492c2 */
extern int32_t osDelay(uint32_t ticks);                                        /* 0x449376 */
extern void *osMessageQueueNew(uint32_t count, uint32_t size, const void *attr); /* 0x449a32 */
extern int32_t osMessageQueueGet(void *queue, void *msg, uint8_t *prio, uint32_t timeout); /* 0x449b3c */
extern int32_t osMessageQueueDelete(void *queue);                              /* 0x449bec */
extern uint32_t ulSetInterruptMask(void);                                      /* 0x5fa0a4 */

extern void SVC_WhitelistManagerInit(void);                                    /* 0x4d6a5c */
extern void service_ancc_init(void);                                           /* 0x4972c2 */
extern void service_ancc_deinit_49739e(void);
extern void service_ancc_notification_process(const uint8_t *data, uint16_t length); /* 0x497960 */
extern uint32_t APP_PbRxNotificationFrameDataProcess(const uint8_t *data, uint16_t length); /* 0x4d6ba8 */
extern void file_heap_free(void *buffer);                                      /* 0x474d16 */

static const char module[] = "task.notif"; /* ROM 0x78c680 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_notification.c"; /* ROM 0x6f6e64 */
static const char thread_name[] = "msg_notif"; /* ROM 0x78c608 */

static const char fn_task[] = "thread_notif"; /* ROM 0x789b30 */
static const char notify_error[] = "Notify error!"; /* ROM 0x789b40 */
static const char notify_error_s[] = "[task.notif]Notify error!"; /* ROM 0x77377c */
static const char fn_notify[] = "_thread_notify_event_handler"; /* ROM 0x766b50 */
static const char notify_value_fmt[] = "notifyValue = 0x%x"; /* ROM 0x78434c */
static const char notify_value_s[] = "[task.notif]notifyValue = 0x%x"; /* ROM 0x766b70 */
static const char whitelist[] =
    "[WHITELIST] Received whitelist update event, reloading whitelist..."; /* ROM 0x707360 */
static const char whitelist_s[] =
    "[task.notif][WHITELIST] Received whitelist update event, reloading whitelist..."; /* ROM 0x6f07b8 */
static const char fn_exit[] = "_thread_exit"; /* ROM 0x789b50 */
static const char queue_deleted[] = "notif message queue deleted"; /* ROM 0x773798 */
static const char queue_deleted_s[] = "[task.notif]notif message queue deleted"; /* ROM 0x74ff3c */
static const char thread_exit[] = "thread notif exit"; /* ROM 0x784360 */
static const char thread_exit_s[] = "[task.notif]thread notif exit"; /* ROM 0x766b90 */
static const char fn_send[] = "Thread_SendEvtToNotifTask"; /* ROM 0x7737b4 */
static const char send_evt[] = "Thread_SendEvtToNotifTask = 0x%x"; /* ROM 0x75bc94 */
static const char send_evt_s[] = "[task.notif]Thread_SendEvtToNotifTask = 0x%x"; /* ROM 0x739ee4 */

#define NOTIF_LOG(level, mask, function, line, format, simple, ...)             \
    do {                                                                        \
        if (audio_log_flags() & 2u)                                             \
            audio_log_extended((level), module, file, (function), (line),       \
                               (format), ##__VA_ARGS__);                        \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))               \
            (void)compress_log_output((mask), (simple), (simple),               \
                                      ##__VA_ARGS__);                           \
    } while (0)

/* Stock configASSERT on a NULL RTOS object: mask interrupts and fault. */
#define NOTIF_ASSERT_NOT_NULL(object)                                           \
    do {                                                                        \
        if ((object) == NULL) {                                                 \
            (void)ulSetInterruptMask();                                         \
            *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;                   \
            for (;;) {}                                                         \
        }                                                                       \
    } while (0)

void thread_notification_entry(void *argument);
void thread_notification_init_hook(void);
void thread_notification_queue_init(void);
void thread_notification_whitelist_init(void);
void thread_notification_state_enter(void);
void thread_notification_state_exit(void);
void thread_notification_create(void);
void thread_notification_destroy(void);
void thread_notification_drain_queue(void);
void Thread_SendEvtToNotifTask(uint32_t event);

/* These names recur in other stock thread_*.c files; static here. */
static void _thread_notify_event_handler(uint32_t notify_value);
static void _thread_exit(void);

static const notif_thread_attr_t notif_thread_attr = {
    thread_name, 0u, g2_notif_thread_cb, 0x70u,
    g2_notif_thread_stack, 0x2000u, 34 /* osPriorityBelowNormal2 */, 1u, 0u,
}; /* ROM 0x75b934 */

/* 0x48e154: thread entry. A wait result of 0 or an osError code is logged
 * and the wait repeats. */
void thread_notification_entry(void *argument)
{
    uint32_t flags;

    (void)argument;
    thread_notification_state_enter();
    thread_notification_queue_init();
    thread_notification_init_hook();
    thread_notification_whitelist_init();
    thread_notification_state_exit();
    for (;;) {
        flags = osThreadFlagsWait(0x00ffffffu, 0u, 0xffffffffu);
        if (flags != 0u && flags < 0x80000000u) {
            _thread_notify_event_handler(flags);
            continue;
        }
        NOTIF_LOG(1u, 0x04000000u, fn_task, 0x5du, notify_error, notify_error_s);
    }
}

/* 0x48e1cc */
void thread_notification_init_hook(void)
{
}

/* 0x48e1ce: 50 x pointer queue on the RTOS heap. */
void thread_notification_queue_init(void)
{
    notif_context_t *ctx = &g2_notif_thread_context;

    ctx->queue = osMessageQueueNew(50u, sizeof(void *), NULL);
    NOTIF_ASSERT_NOT_NULL(ctx->queue);
}

/* 0x48e1f6 */
void thread_notification_whitelist_init(void)
{
    SVC_WhitelistManagerInit();
}

/* 0x48e1fe: thread-manager start barrier for slot 1. */
void thread_notification_state_enter(void)
{
    (void)audio_uart_ring_state_transition_4c9b86(NOTIF_THREAD_INDEX);
}

/* 0x48e208: thread-manager "start done" for slot 1. */
void thread_notification_state_exit(void)
{
    (void)audio_uart_ring_resource_transition_4c9be2(NOTIF_THREAD_INDEX);
}

/* 0x48e212 */
void thread_notification_create(void)
{
    notif_context_t *ctx = &g2_notif_thread_context;

    ctx->thread = osThreadNew(thread_notification_entry, NULL, &notif_thread_attr);
    NOTIF_ASSERT_NOT_NULL(ctx->thread);
    service_ancc_init();
}

/* 0x48e242 */
void thread_notification_destroy(void)
{
    notif_context_t *ctx = &g2_notif_thread_context;

    if (ctx->thread != NULL) {
        (void)osThreadTerminate(ctx->thread);
        ctx->thread = NULL;
    }
    service_ancc_deinit_49739e();
}

/* 0x48e25e: dispatch and free every queued message without blocking. */
void thread_notification_drain_queue(void)
{
    notif_msg_t *msg = NULL;

    while (osMessageQueueGet(g2_notif_thread_context.queue, &msg, NULL, 0u) == 0 &&
           msg != NULL) {
        if (msg->type == NOTIF_MSG_PB_NOTIFICATION)
            (void)APP_PbRxNotificationFrameDataProcess(msg->payload, (uint16_t)msg->length);
        else if (msg->type == NOTIF_MSG_ANCC)
            service_ancc_notification_process(msg->payload, (uint16_t)msg->length);
        file_heap_free(msg);
        msg = NULL;
    }
}

/* 0x48e2b8 */
static __attribute__((noinline)) void _thread_notify_event_handler(uint32_t notify_value)
{
    NOTIF_LOG(4u, 0x10400000u, fn_notify, 0xd2u, notify_value_fmt, notify_value_s, notify_value);
    if ((notify_value & NOTIF_FLAG_MESSAGE) != 0u)
        thread_notification_drain_queue();
    if ((notify_value & NOTIF_FLAG_WHITELIST) != 0u) {
        NOTIF_LOG(4u, 0x10000000u, fn_notify, 0xdau, whitelist, whitelist_s);
        SVC_WhitelistManagerInit();
    }
    if ((notify_value & NOTIF_FLAG_EXIT) != 0u)
        _thread_exit();
}

/* 0x48e34e: acknowledge the stop, drop the queue and park forever. */
static __attribute__((noinline)) void _thread_exit(void)
{
    notif_context_t *ctx = &g2_notif_thread_context;

    audio_uart_ring_sync_exit_4c9c3c(NOTIF_THREAD_INDEX);
    if (ctx->queue != NULL) {
        (void)osMessageQueueDelete(ctx->queue);
        ctx->queue = NULL;
        NOTIF_LOG(4u, 0x10000000u, fn_exit, 0xedu, queue_deleted, queue_deleted_s);
    }
    NOTIF_LOG(4u, 0x10000000u, fn_exit, 0xefu, thread_exit, thread_exit_s);
    for (;;)
        (void)osDelay(0xffffffffu);
}

/* 0x48e3e2 */
void Thread_SendEvtToNotifTask(uint32_t event)
{
    NOTIF_LOG(4u, 0x10400000u, fn_send, 0xf8u, send_evt, send_evt_s, event);
    (void)osThreadFlagsSet(g2_notif_thread_context.thread, event);
}
