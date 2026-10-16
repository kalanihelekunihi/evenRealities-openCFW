#include "native_delayed_state.h"
/* Supplemental instruction-backed recovery of0x65740; not a locked corpus row. */
extern void *osMessageQueueNew(uint32_t,uint32_t,const void *);
extern void *osTimerNew(void (*)(void *),uint32_t,void *,const void *);
extern void *osMutexNew(const void *),*osThreadNew(void (*)(void *),void *,const void *);
extern int32_t osThreadTerminate(void *);
extern void r1_native_delayed_reschedule(uint32_t),r1_native_delayed_worker(void *);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
static void log_failure(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,sdk);
}
void r1_native_delayed_initialize(void)
{
    if (!r1_delayed_context[0]) {
        void *queue=osMessageQueueNew(15,8,&r1_delayed_queue_attributes);
        r1_delayed_context[0]=(uint32_t)(uintptr_t)queue;
        if (!queue) log_failure("[RING][fw_evt_loop_init]osMessageQueueNew, fail","[fw_evt_loop_init]osMessageQueueNew, fail");
    }
    if (!r1_delayed_context[3]) {
        /* Native ARM32 callback token shares R0 with the uint32_t entry. */
        void *timer=osTimerNew((void (*)(void *))(uintptr_t)r1_native_delayed_reschedule,0,0,&r1_delayed_timer_attributes);
        r1_delayed_context[3]=(uint32_t)(uintptr_t)timer;
        if (!timer) log_failure("[RING][fw_evt_loop_init]osTimerNew, failed","[fw_evt_loop_init]osTimerNew, failed");
    }
    if (!r1_delayed_context[2]) {
        void *mutex=osMutexNew(&r1_delayed_mutex_attributes);
        r1_delayed_context[2]=(uint32_t)(uintptr_t)mutex;
        if (!mutex) log_failure("[RING]Warning: failed to Create fw_evt_loop_mutex_id","Warning: failed to Create fw_evt_loop_mutex_id");
    }
    if (r1_delayed_context[1]) {
        (void)osThreadTerminate((void *)(uintptr_t)r1_delayed_context[1]);r1_delayed_context[1]=0;
    }
    void *thread=osThreadNew(r1_native_delayed_worker,0,&r1_delayed_thread_attributes);
    r1_delayed_context[1]=(uint32_t)(uintptr_t)thread;
    if (!thread) log_failure("[RING][fw_evt_loop_init]osThreadNew, fail","[fw_evt_loop_init]osThreadNew, fail");
}
