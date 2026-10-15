#include <stdint.h>

/* Only this authenticated thread-manager field is owned here. The rest of
 * the manager and actual CMSIS event object remain separate source gates. */
void *volatile r1_native_sync_event_flags
 __attribute__((section(".r1.sync.flags"),aligned(4)));
extern uint32_t osEventFlagsSet(void *,uint32_t);
extern uint32_t osThreadFlagsWait(uint32_t,uint32_t,uint32_t);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void r1_native_watchdog_arm(uint32_t);

static uint32_t group_bit(uint32_t group)
{
    /* ARM register-shift counts use the low byte; >=32 produces zero. */
    uint32_t shift=group&255u;
    return shift<32 ? UINT32_C(1)<<shift : 0;
}
void r1_native_suspend_signal(uint32_t group)
{ osEventFlagsSet(r1_native_sync_event_flags,group_bit(group)); }
void r1_native_sync_wait(uint32_t group)
{
    while ((osThreadFlagsWait(0x800000,1,UINT32_MAX)&0x800000u)==0) {}
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c400000,"[thread_manager]thread %d sync start:","[thread_manager]thread %d sync start:",group);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x1c0003,"thread %d sync start:",group);
}
void r1_native_sync_signal(uint32_t group)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c400000,"[thread_manager]thread %d sync end","[thread_manager]thread %d sync end",group);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x1c0003,"thread %d sync end",group);
    osEventFlagsSet(r1_native_sync_event_flags,group_bit(group));
}
void r1_native_worker_park(uint32_t group,uint32_t watchdog)
{
    r1_native_watchdog_arm(watchdog);
    r1_native_suspend_signal(group);
    for (;;) osDelay(UINT32_MAX);
}
