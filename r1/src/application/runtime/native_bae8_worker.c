/* Stock R1 0x92178: RX queue startup and permanent flag-driven worker. */
#include <stdint.h>
extern void *volatile r1_bae8_rx_queue;
extern uint32_t volatile r1_bae8_rx_watchdog;
extern void r1_native_sync_wait(uint32_t),r1_native_sync_signal(uint32_t),r1_native_suspend_signal(uint32_t);
extern void *osMessageQueueNew(uint32_t,uint32_t,const void *);
extern uint32_t osThreadFlagsWait(uint32_t,uint32_t,uint32_t);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_native_watchdog_register(const char *,uint32_t);
extern void r1_native_watchdog_arm(uint32_t),r1_native_watchdog_disarm(uint32_t),r1_native_watchdog_feed(uint32_t);
extern void r1_message_pump_task(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
/* Native allocation failure sets BASEPRI=64 then writes zero to 0xffffffff.
 * Keep the architectural transition explicit; it is not a portable C operation. */
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
_Noreturn void r1_bae8_input_task_plan_startup(void *argument)
{
    (void)argument;
    r1_native_sync_wait(2);
    void *queue=osMessageQueueNew(50,4,0);
    r1_bae8_rx_queue=queue;
    if (!queue) r1_bae8_rx_allocation_fault();
    r1_native_sync_signal(2);
    r1_bae8_rx_watchdog=r1_native_watchdog_register("ble_msgrx",10000);
    for (;;) {
        r1_native_watchdog_arm(r1_bae8_rx_watchdog);
        uint32_t flags=osThreadFlagsWait(0x00ffffff,0,UINT32_MAX);
        r1_native_watchdog_disarm(r1_bae8_rx_watchdog);
        if (flags-1u<UINT32_C(0x7fffffff)) {
            if (flags&0x400000u) r1_message_pump_task();
            if (flags&0x800000u) {
                r1_native_watchdog_arm(r1_bae8_rx_watchdog);
                r1_native_suspend_signal(2);
                for (;;) (void)osDelay(UINT32_MAX);
            }
        } else {
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                (void)r1_structured_log_format(0x04000000,"[RING]Notify error!","[RING]Notify error!");
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_0(0x001c0001,"Notify error!");
        }
        r1_native_watchdog_feed(r1_bae8_rx_watchdog);
    }
}
