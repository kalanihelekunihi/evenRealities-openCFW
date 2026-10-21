#include <stdint.h>

/* Product-specific recovery of 0x65b4c. No third-party body attribution.
 * RAM anchors require authenticated layout; initialization and companion
 * immediate-push/reschedule bodies remain separate evidence gates. */
extern volatile uint32_t r1_delayed_context[6];
extern uint32_t r1_delayed_callbacks[64],r1_delayed_arguments[64],r1_delayed_deadlines[64];
extern uint32_t r1_structured_log_mode_get(void),osKernelGetTickCount(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern int32_t osDelay(uint32_t),osMutexAcquire(void *,uint32_t),osMutexRelease(void *),osTimerStop(void *);
extern void r1_native_delayed_push(void (*)(uint32_t),uint32_t,uint32_t);
extern void r1_native_delayed_reschedule(uint32_t);
static void log_failure(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(0x001c0001,sdk);
}
void r1_native_delayed_schedule(void (*callback)(uint32_t),uint32_t argument,uint32_t delay)
{
    if (!r1_delayed_context[1]) {
        log_failure("[RING][fw_evt_loop_push_delayed]wating for fw_evt_loop_thread_id init ok",
                    "[fw_evt_loop_push_delayed]wating for fw_evt_loop_thread_id init ok");
        do { (void)osDelay(10); } while (!r1_delayed_context[1]);
    }
    if (delay<2) { r1_native_delayed_push(callback,argument,UINT32_MAX);return; }
    if (osMutexAcquire((void *)(uintptr_t)r1_delayed_context[2],1000))
        log_failure("[RING][fw_evt_loop_push_delayed]fw_event lock fail",
                    "[fw_evt_loop_push_delayed]fw_event lock fail");
    uint32_t slot=0,elapsed=0;
    for (;slot<64;slot++) if (!r1_delayed_callbacks[slot]) {
        r1_delayed_callbacks[slot]=(uint32_t)(uintptr_t)callback;
        r1_delayed_arguments[slot]=argument;
        /* Stock truncates the multiplication to 32 bits before shifting. */
        elapsed=((osKernelGetTickCount()*UINT32_C(1000))>>10)-r1_delayed_context[4];
        r1_delayed_deadlines[slot]=delay+elapsed;
        break;
    }
    if (osMutexRelease((void *)(uintptr_t)r1_delayed_context[2]))
        log_failure("[RING][fw_evt_loop_push_delayed]fw_event unlock fail",
                    "[fw_evt_loop_push_delayed]fw_event unlock fail");
    if (slot<64) {
        (void)osTimerStop((void *)(uintptr_t)r1_delayed_context[3]);
        r1_native_delayed_reschedule(elapsed|UINT32_C(0xff000000));
    }
}
