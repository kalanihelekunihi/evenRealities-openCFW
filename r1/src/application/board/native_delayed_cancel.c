#include "native_delayed_state.h"
extern uint32_t r1_delayed_callbacks[64],r1_delayed_arguments[64];
extern int32_t osMutexAcquire(void *,uint32_t),osMutexRelease(void *),osTimerStop(void *);
extern uint32_t osKernelGetTickCount(void),r1_structured_log_mode_get(void);
extern void r1_native_delayed_reschedule(uint32_t);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
static void log_failure(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,sdk);
}
int32_t r1_native_delayed_cancel(void (*callback)(uint32_t),uint32_t argument)
{
    if (!r1_delayed_context[1]) {
        log_failure("[RING]fw_evt_loop_thread_id == NULL\r\n","fw_evt_loop_thread_id == NULL\r\n");return 0;
    }
    (void)osMutexAcquire((void *)(uintptr_t)r1_delayed_context[2],1000);
    int32_t found=0;
    for (uint32_t i=0;i<64;i++) {
        /* Stock also matches zero callback slots; do not add an occupancy test. */
        if (r1_delayed_callbacks[i]==(uint32_t)(uintptr_t)callback && (!argument || r1_delayed_arguments[i]==argument)) {
            r1_delayed_callbacks[i]=0;found=1;
        }
    }
    if (osMutexRelease((void *)(uintptr_t)r1_delayed_context[2]))
        log_failure("[RING][fw_evt_loop_timer_callback]fw_evt_loop_remove_delayed unlock fail",
                    "[fw_evt_loop_timer_callback]fw_evt_loop_remove_delayed unlock fail");
    if (found) {
        uint32_t ticks=osKernelGetTickCount();
        uint32_t elapsed=((ticks*UINT32_C(1000))>>10)-r1_delayed_context[4];
        (void)osTimerStop((void *)(uintptr_t)r1_delayed_context[3]);
        r1_native_delayed_reschedule(elapsed|UINT32_C(0xff000000));
    }
    return found;
}
