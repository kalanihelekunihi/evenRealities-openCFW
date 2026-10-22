/* EasyLogger async back end (G2 downstream glue), stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\EasyLogger-master\easylogger\src\elog_async_api.c
 * Native 0x448cac..0x448cb8 (UART sink setter), 0x448cc4..0x448ccc (default
 * level setter) and 0x448f44..0x448f78 (handler thread start); shared pool
 * 0x448f40..0x44900b. Neighbours: 0x448cb8 (BLE sink setter,
 * system/log/logger-ble/display_logger_ble_cancel.c), 0x448c74
 * (system/log/extended-log), 0x448ccc.. (system/a-03-elog-async). The
 * handler thread body 0x448e8e has no C yet. */
#include <stdint.h>
#include <stddef.h>

/* Output sinks, RAM 0x20073b90: {enabled, output} for UART (+0x00/+0x04)
 * and BLE (+0x08/+0x0c, set by 0x448cb8). */
typedef struct {
    uint8_t enabled;                                /* +0x00 */
    void (*output)(const char *text, uint16_t len); /* +0x04 */
} g2_elog_sink_t;

/* CMSIS-RTOS2 osThreadAttr_t. */
typedef struct {
    const char *name;   /* +0x00 */
    uint32_t attr_bits; /* +0x04 */
    void *cb_mem;       /* +0x08 */
    uint32_t cb_size;   /* +0x0c */
    void *stack_mem;    /* +0x10 */
    uint32_t stack_size;/* +0x14 */
    int32_t priority;   /* +0x18 */
    uint32_t tz_module; /* +0x1c */
    uint32_t reserved;  /* +0x20 */
} g2_os_thread_attr_t;
_Static_assert(sizeof(g2_os_thread_attr_t) == 0x24u, "osThreadAttr_t");

extern g2_elog_sink_t g2_elog_sink;            /* RAM 0x20073b90 */
extern volatile uint8_t g2_elog_default_level; /* RAM 0x20004546 */
extern uint32_t g2_audio_log_event_handle;     /* RAM 0x20074570 osEventFlagsId_t */

extern void *osEventFlagsNew(const void *attr);                                 /* 0x449590 */
extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr); /* 0x4490e2 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern int32_t g2_log_transport_queue_failure(const char *fmt, ...);           /* 0x4733ee */
extern void elog_async_handler_thread_448e8e(void *argument);

static const char thread_name[] = "elog_async_handler_thread"; /* ROM 0x76b650 */
static const char event_flags_failed[] =
    "Failed to create elog_async_handler_thread EventFlags\n"; /* ROM 0x71ea00 */

/* ROM 0x7542f0: stack 0x800, priority 0x17 (osPriorityBelowNormal7). */
const g2_os_thread_attr_t g2_elog_async_thread_attr_7542f0 = {
    .name = thread_name,
    .stack_size = 0x800u,
    .priority = 0x17,
};

uint32_t elog_async_output_sink_set_448cac(uint32_t enabled, void *output)
{
    g2_elog_sink.enabled = (uint8_t)enabled;
    g2_elog_sink.output = (void (*)(const char *, uint16_t))output;
    return 0u;
}

void elog_async_default_level_set_448cc4(uint8_t level)
{
    g2_elog_default_level = level;
}

/* Create the consumer's event flags, then the handler thread. */
void elog_async_thread_init_448f44(void)
{
    g2_os_thread_attr_t attr;

    g2_audio_log_event_handle = (uint32_t)(uintptr_t)osEventFlagsNew(NULL);
    if (g2_audio_log_event_handle == 0u) {
        (void)g2_log_transport_queue_failure(event_flags_failed);
        return;
    }
    (void)audio_uart_display_area_copy_439c04(&attr, &g2_elog_async_thread_attr_7542f0, sizeof attr);
    (void)osThreadNew(elog_async_handler_thread_448e8e, NULL, &attr);
}
