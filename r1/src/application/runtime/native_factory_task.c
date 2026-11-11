/* Stock R1 factory creator 0x45c54, stop 0x45c3c, worker 0x9230c. */
#include <stdint.h>
#include <stddef.h>
extern void *volatile r1_factory_rx_thread,*volatile r1_factory_rx_queue;
extern void r1_native_sync_wait(uint32_t),r1_native_sync_signal(uint32_t),r1_native_suspend_signal(uint32_t);
extern void *osMessageQueueNew(uint32_t,uint32_t,const void *);
extern uint32_t osThreadFlagsWait(uint32_t,uint32_t,uint32_t);
extern int32_t osDelay(uint32_t),osThreadTerminate(void *);
/* Configuration-driven delayed factory start; see its separate review. */
extern void r1_factory_boot_mode_schedule(void);
extern uint32_t r1_native_stream_initialize(void),r1_native_stream_register(void);
extern void *r1_native_accelerometer_singleton(void),*r1_native_temperature_singleton(void);
extern uint32_t r1_native_sensor_timer_poll(void);
extern void r1_factory_input_record_plan_dispatch(void);
extern int32_t osMessageQueueGet(void *,void *,uint8_t *,uint32_t);
extern void nrf_log_frontend_hexdump(uint32_t,const void *,uint16_t);
extern uint32_t r1_factory_legacy_command_route_frame(uint32_t,const void *,uint32_t);
extern void r1_eat_command_tokenize(void *);
extern void vPortFree(void *);
extern uint32_t r1_native_watchdog_hw_feed(void);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
struct r1_factory_thread_attr {
    const char *name;uint32_t attr_bits;void *cb_mem;uint32_t cb_size;
    void *stack_mem;uint32_t stack_size;int32_t priority;uint32_t tz_module,reserved;
};
_Static_assert(sizeof(struct r1_factory_thread_attr)==36,"native CMSIS attributes");
extern void *osThreadNew(void (*)(void *),void *,const struct r1_factory_thread_attr *);
const char r1_factory_thread_name[] __attribute__((section(".r1.factory.name")))="factory_test";
const struct r1_factory_thread_attr r1_factory_thread_attributes
 __attribute__((section(".r1.factory.attributes"),aligned(4)))={r1_factory_thread_name,0,0,0,0,8192,39,1,0};
_Noreturn void r1_factory_input_task_plan_startup(void *argument)
{
    (void)argument;
    r1_native_sync_wait(6);
    void *queue=osMessageQueueNew(8,4,0);
    r1_factory_rx_queue=queue;
    if (!queue) r1_bae8_rx_allocation_fault();
    r1_factory_boot_mode_schedule();
    (void)r1_native_stream_initialize();
    (void)r1_native_accelerometer_singleton();
    (void)r1_native_stream_register();
    (void)r1_native_temperature_singleton();
    r1_native_sync_signal(6);
    for (;;) {
        uint32_t timeout=r1_native_sensor_timer_poll();
        uint32_t flags=osThreadFlagsWait(0x00ffffff,0,timeout);
        if (flags-1u<UINT32_C(0x7fffffff)) {
            if (flags&0x400000u) r1_factory_input_record_plan_dispatch();
            if (flags&0x800000u) {
                r1_native_suspend_signal(6);
                for (;;) (void)osDelay(UINT32_MAX);
            }
        }
        (void)r1_native_watchdog_hw_feed();
    }
}
void r1_factory_input_thread_creation_plan_build(void)
{
    void *thread=osThreadNew(r1_factory_input_task_plan_startup,0,&r1_factory_thread_attributes);
    r1_factory_rx_thread=thread;
    if (!thread) r1_bae8_rx_allocation_fault();
}
void r1_factory_input_thread_stop(void)
{
    void *thread=r1_factory_rx_thread;
    if (thread) { (void)osThreadTerminate(thread);r1_factory_rx_thread=0; }
}
/* Stock factory queue drain at 0x45f3c. The queue holds owned pointers to
 * twelve-byte headers followed by payload bytes. Provider calls may replace
 * the live queue slot, so keep it volatile as in the stock stack frame. */
struct r1_factory_record {uint32_t handle,channel,length;uint8_t payload[];};
_Static_assert(sizeof(struct r1_factory_record)==12,"factory record header");
void r1_factory_input_record_plan_dispatch(void)
{
    struct r1_factory_record *volatile record=0;
    while (osMessageQueueGet(r1_factory_rx_queue,(void *)&record,0,0)==0) {
        if (!record) continue;
        uint32_t length=record->length;
        if (length>3 && record->payload[0]=='A' &&
            record->payload[1]=='T' && record->payload[2]=='^') {
            record->payload[length]=0;
            r1_eat_command_tokenize(record->payload);
        } else {
            nrf_log_frontend_hexdump(0x001c0004,record->payload,(uint16_t)length);
            (void)r1_factory_legacy_command_route_frame((uint16_t)record->handle,
                                                   record->payload,(uint16_t)record->length);
        }
        vPortFree(record);
        record=0;
    }
}
#include "../board/native_task_contexts.h"
_Static_assert(sizeof(struct r1_factory_lifecycle)==8,"native lifecycle prefix");
struct r1_factory_lifecycle r1_factory_rx_lifecycle
 __attribute__((section(".r1.factory.lifecycle"),aligned(4)))={r1_factory_input_thread_creation_plan_build,r1_factory_input_thread_stop};
