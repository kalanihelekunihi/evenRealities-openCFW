#include <stdint.h>
/* Product timer callback at0x65f84; source initialization remains gated.
 * Preserve both table passes and clear each expired callback before pushing it. */
extern volatile uint32_t r1_delayed_context[6];
extern uint32_t r1_delayed_callbacks[64],r1_delayed_arguments[64],r1_delayed_deadlines[64];
extern void vPortEnterCritical(void),vPortExitCritical(void);
extern int32_t osMutexAcquire(void *,uint32_t),osMutexRelease(void *),osTimerStart(void *,uint32_t);
extern uint32_t osKernelGetTickCount(void),r1_structured_log_mode_get(void);
extern void r1_native_delayed_push(void (*)(uint32_t),uint32_t,uint32_t);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static void log_failure(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,sdk);
}
void r1_native_delayed_reschedule(uint32_t input)
{
    uint32_t minimum=UINT32_MAX;
    vPortEnterCritical();uint32_t elapsed=r1_delayed_context[5];vPortExitCritical();
    if (input>>24==255) elapsed=input&0x00ffffff;
    if (osMutexAcquire((void *)(uintptr_t)r1_delayed_context[2],1000))
        log_failure("[RING][fw_evt_loop_timer_callback]fw_event lock fail",
                    "[fw_evt_loop_timer_callback]fw_event lock fail");
    for (uint32_t i=0;i<64;i++) if (r1_delayed_callbacks[i]) {
        uint32_t remaining=r1_delayed_deadlines[i];
        r1_delayed_deadlines[i]=elapsed<remaining ? remaining-elapsed : 0;
        if (!r1_delayed_deadlines[i]) {
            uint32_t callback=r1_delayed_callbacks[i];r1_delayed_callbacks[i]=0;
            r1_native_delayed_push((void (*)(uint32_t))(uintptr_t)callback,r1_delayed_arguments[i],UINT32_MAX);
        }
    }
    for (uint32_t i=0;i<64;i++) if (r1_delayed_callbacks[i] && r1_delayed_deadlines[i]<minimum)
        minimum=r1_delayed_deadlines[i];
    if (osMutexRelease((void *)(uintptr_t)r1_delayed_context[2]))
        log_failure("[RING][fw_evt_loop_timer_callback]fw_event unlock fail",
                    "[fw_evt_loop_timer_callback]fw_event unlock fail");
    /* Stock excludes INT32_MAX, but does not exclude UINT32_MAX. */
    if (minimum!=0x7fffffff && minimum) {
        vPortEnterCritical();r1_delayed_context[5]=minimum;vPortExitCritical();
        int32_t status=osTimerStart((void *)(uintptr_t)r1_delayed_context[3],minimum);
        if (status) {
            const char *ring="[RING]osTimerStart  next_delay %d stat = %d";
            if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
                r1_structured_log_format(0x04800000,ring,ring,minimum,(uint32_t)status);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_2(0x001c0001,"osTimerStart  next_delay %d stat = %d",minimum,(uint32_t)status);
        }
        r1_delayed_context[4]=(osKernelGetTickCount()*UINT32_C(1000))>>10;
    }
}
