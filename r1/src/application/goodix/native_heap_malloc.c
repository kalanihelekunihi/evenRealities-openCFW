#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "goodix_mem.h"
#include "../runtime/native_application_launch.h"
extern void *r1_goodix_native_heap_control(void);
extern void *r1_goodix_native_bin_allocate(void *,uint32_t);
extern bool goodix_primitives_byte_fill(uint8_t,uint8_t *,size_t);
extern void r1_status_record_ring_publish(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_typed(uint32_t,const char *,...);
extern void r1_native_watchdog_feed(uint32_t);
extern uint32_t osThreadFlagsSet(void *,uint32_t);
uint32_t r1_module_thread_flags_set(uint32_t flags)
{
    void *thread=r1_application_lifecycle.thread;
    return thread ? osThreadFlagsSet(thread,flags) : 0;
}
extern int32_t osDelay(uint32_t);
extern uint32_t r1_task_sensor_watchdog;
static uint32_t read_word(uintptr_t address)
{ return *(const volatile uint32_t *)address; }
static void write_word(uintptr_t address,uint32_t value)
{ *(volatile uint32_t *)address=value; }
_Noreturn void r1_goodix_sensor_memory_fatal(uint32_t info,uint32_t available)
{
    r1_status_record_ring_publish(0,info,0,0);
    (void)r1_structured_log_typed(0x0c800000,
        "[sensor]algo mem fatal! info1=%u free=%u",info,available);
    r1_native_watchdog_feed(*(const volatile uint32_t *)&r1_task_sensor_watchdog);
    (void)r1_module_thread_flags_set(0x200);
    for (;;) (void)osDelay(1000);
}
_Noreturn void r1_goodix_native_heap_exhausted(void)
{
    uint32_t available=goodix_mem_get_free_size();
    r1_goodix_sensor_memory_fatal(1,available);
}
void *goodix_mem_malloc(int32_t size)
{
    uintptr_t pool=(uintptr_t)r1_goodix_native_heap_control();
    if (!pool) r1_goodix_native_heap_exhausted();
    uint32_t requested=(uint32_t)size;
    if (requested<8u) requested=8u;
    uint32_t adjusted=((requested+3u)&~3u)+8u;
    if (adjusted>read_word(pool+40u)) r1_goodix_native_heap_exhausted();
    void *allocation=r1_goodix_native_bin_allocate((void *)pool,adjusted);
    if (!allocation) {
        uintptr_t top=read_word(pool+28u);
        uint32_t encoded=adjusted<<2,old=read_word(top+4u);
        if (old<encoded) r1_goodix_native_heap_exhausted();
        write_word(top+4u,encoded|3u);
        uintptr_t next=top+(encoded>>2);
        write_word(pool+28u,(uint32_t)next);
        write_word(next+4u,old-encoded);
        allocation=(void *)(top+8u);
    }
    if (allocation)
        (void)goodix_primitives_byte_fill(0,allocation,(size_t)requested);
    return allocation;
}
