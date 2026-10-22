/* BLE WSF (Cordio) host thread, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_wsf.c
 * (module tag "task.ble.wsf"). Native 0x4d0a4c..0x4d0c35 minus the TX-ready
 * semaphore helpers 0x4d0b36/0x4d0b64/0x4d0c36, which live in
 * drivers/peripherals/ring-ble/display_ring_ble_tx_sync.c
 * (audio_ble_take_tx_ready / audio_ble_tx_ready_wait /
 * audio_ble_tx_complete_notify). Literal pool 0x4d0cdc..0x4d0d23.
 *
 * One CMSIS thread ("ble_wsf", priority 49 = osPriorityRealtime1, 16 KiB
 * stack) runs appBleStart once and then wsfOsDispatcher forever. A binary
 * semaphore (max 1, initial 1) at context +0x14 paces BLE TX: it is taken
 * before each notification and released from the TX-complete event. */
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
} ble_wsf_thread_attr_t;
_Static_assert(sizeof(ble_wsf_thread_attr_t) == 36u, "osThreadAttr_t");

/* Thread context at RAM 0x20004068 (thread-manager table, stride 0x24). */
typedef struct {
    void (*init)(void);      /* +0x00 */
    void (*deinit)(void);    /* +0x04 */
    void *thread;            /* +0x08 osThreadId_t */
    uint32_t reserved_0c;    /* +0x0c */
    uint32_t reserved_10;    /* +0x10 */
    void *tx_semaphore;      /* +0x14 osSemaphoreId_t */
} ble_wsf_context_t;
_Static_assert(sizeof(ble_wsf_context_t) == 0x18u, "context prefix");

#define BLE_WSF_THREAD_INDEX 9u /* thread-manager slot */

extern uint8_t audio_ble_wsf_thread_state[]; /* RAM 0x20004068 */
extern uint8_t g2_ble_wsf_thread_cb[];       /* RAM 0x20076540, static TCB 112 B */
extern uint8_t g2_ble_wsf_thread_stack[];    /* RAM 0x20045498, 16384 B */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format,
                                    const char *copy, ...); /* 0x43ce9e */

/* Thread manager (thread_manager.c). */
extern uint32_t audio_uart_ring_state_transition_4c9b86(uint32_t index);    /* sysstart sync */
extern uint32_t audio_uart_ring_resource_transition_4c9be2(uint32_t index); /* sysstart sync end */

/* CMSIS-RTOS2. */
extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr); /* 0x4490e2 */
extern int32_t osThreadTerminate(void *thread);                                /* 0x4491fe */
extern void *osSemaphoreNew(uint32_t max_count, uint32_t initial_count,
                            const void *attr);                                 /* 0x44989a */
extern uint32_t audio_wsf_interrupt_mask_set(void);                            /* ulSetInterruptMask 0x5fa0a4 */

/* BLE stack and neighbours. */
extern void wsfOsDispatcher(void);                       /* 0x52b9d0 */
extern void appBleStart(void);                           /* 0x4b80f0 */
extern void cb_ble_status_init_4abcb0(void);             /* CALLBACK_MGR_Init(.., "BLE_STATUS") */
extern void cb_ble_status_deinit_4abcbc(void);           /* CALLBACK_MGR_Deinit */
extern uint32_t audio_ble_take_tx_ready(uint32_t timeout_ticks); /* threadBleWsfTakeTxReady 0x4d0b36 */

static const char module[] = "task.ble.wsf"; /* ROM 0x789ab0 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_wsf.c"; /* ROM 0x6fe39c */
static const char fn_resource_init[] = "_thread_resource_init"; /* ROM 0x77cc1c */
static const char sem_ready[] =
    "BLE WSF semaphore initialized: max_count=%d, initial_count=%d"; /* ROM 0x7104a4 */
static const char sem_ready_s[] =
    "[task.ble.wsf]BLE WSF semaphore initialized: max_count=%d, initial_count=%d"; /* ROM 0x6f6ce8 */
static const char thread_name[] = "ble_wsf"; /* ROM 0x78eba4 */

#define WSF_LOG(level, mask, function, line, format, simple, ...)               \
    do {                                                                        \
        if (audio_log_flags() & 2u)                                             \
            audio_log_extended((level), module, file, (function), (line),       \
                               (format), ##__VA_ARGS__);                        \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))               \
            (void)compress_log_output((mask), (simple), (simple),               \
                                      ##__VA_ARGS__);                           \
    } while (0)

/* Stock configASSERT on a NULL RTOS object: mask interrupts and fault. */
#define WSF_ASSERT_NOT_NULL(object)                                             \
    do {                                                                        \
        if ((object) == NULL) {                                                 \
            (void)audio_wsf_interrupt_mask_set();                               \
            *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;                   \
            for (;;) {}                                                         \
        }                                                                       \
    } while (0)

static const ble_wsf_thread_attr_t ble_wsf_thread_attr = {
    thread_name, 0u, g2_ble_wsf_thread_cb, 0x70u,
    g2_ble_wsf_thread_stack, 0x4000u, 49 /* osPriorityRealtime1 */, 1u, 0u,
}; /* ROM 0x75b838 */

void threadBleWsfTask(void *argument);
void threadBleWsfStart(void);
void threadBleWsfLoopInit(void);
void threadBleWsfEnter(void);
void threadBleWsfReady(void);
void threadBleWsfInit(void);
void threadBleWsfDeinit(void);
uint32_t threadBleWsfWaitOnce(uint32_t timeout);

/* "_thread_resource_init" recurs in other stock thread_*.c files; static. */
static void _thread_resource_init(void);

static ble_wsf_context_t *context(void)
{
    return (ble_wsf_context_t *)(void *)audio_ble_wsf_thread_state;
}

/* 0x4d0a4c: thread entry; never returns. */
void threadBleWsfTask(void *argument)
{
    (void)argument;
    threadBleWsfEnter();
    _thread_resource_init();
    threadBleWsfStart();
    threadBleWsfLoopInit();
    threadBleWsfReady();
    for (;;)
        wsfOsDispatcher();
}

/* 0x4d0a68 */
void threadBleWsfStart(void)
{
    appBleStart();
}

/* 0x4d0a70: TX-ready semaphore (max 1, initial 1) and the BLE_STATUS
 * callback manager. */
static __attribute__((noinline)) void _thread_resource_init(void)
{
    ble_wsf_context_t *ctx = context();

    ctx->tx_semaphore = osSemaphoreNew(1u, 1u, NULL);
    WSF_ASSERT_NOT_NULL(ctx->tx_semaphore);
    WSF_LOG(4u, 0x10800000u, fn_resource_init, 108u, sem_ready, sem_ready_s, 1, 1);
    cb_ble_status_init_4abcb0();
}

/* 0x4d0ae0 */
void threadBleWsfLoopInit(void)
{
}

/* 0x4d0ae2: thread-manager start barrier for slot 9. */
void threadBleWsfEnter(void)
{
    (void)audio_uart_ring_state_transition_4c9b86(BLE_WSF_THREAD_INDEX);
}

/* 0x4d0aec: thread-manager "start done" for slot 9. */
void threadBleWsfReady(void)
{
    (void)audio_uart_ring_resource_transition_4c9be2(BLE_WSF_THREAD_INDEX);
}

/* 0x4d0af6 */
void threadBleWsfInit(void)
{
    ble_wsf_context_t *ctx = context();

    ctx->thread = osThreadNew(threadBleWsfTask, NULL, &ble_wsf_thread_attr);
    WSF_ASSERT_NOT_NULL(ctx->thread);
}

/* 0x4d0b1c */
void threadBleWsfDeinit(void)
{
    ble_wsf_context_t *ctx = context();

    cb_ble_status_deinit_4abcbc();
    if (ctx->thread != NULL) {
        (void)osThreadTerminate(ctx->thread);
        ctx->thread = NULL;
    }
}

/* 0x4d0c2c: one bounded take of the TX-ready semaphore; 1 when taken. */
uint32_t threadBleWsfWaitOnce(uint32_t timeout)
{
    return audio_ble_take_tx_ready((uint16_t)timeout);
}
