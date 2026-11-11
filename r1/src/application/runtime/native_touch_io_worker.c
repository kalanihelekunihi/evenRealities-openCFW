/* Stock touch worker 0x927c8, callback registration 0x8e7b0 and
 * slider callback setter/trampoline 0x67460/0x93388. */
#include <stdint.h>
#include "cmsis_os2.h"
extern void *volatile r1_touch_task_message_queue;
extern void r1_native_sync_wait(uint32_t),r1_native_sync_signal(uint32_t);
extern uint32_t r1_native_watchdog_register(const char *,uint32_t);
extern void r1_native_watchdog_arm(uint32_t),r1_native_watchdog_disarm(uint32_t);
extern void r1_native_watchdog_feed(uint32_t);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
extern void r1_iqs7211e_touch_task_dispatcher(uint32_t);
extern uint32_t r1_touch_ready_callback_setter(uint32_t);
extern uint32_t r1_touch_ready_irq_callback(void),r1_touch_power_on_step(void);
#include "native_touch_slider.h"
volatile uint32_t r1_touch_io_watchdog
 __attribute__((section(".r1.touch.io.watchdog"),aligned(4)))=0;
volatile uint32_t r1_touch_slider_callback_word
 __attribute__((section(".r1.touch.slider_callback"),aligned(4)))=0;
uint32_t r1_touch_slider_callback_setter(uint32_t callback)
{
    if (!callback) return 0;
    r1_touch_slider_callback_word=callback;
    return 1;
}
uint32_t r1_touch_slider_callback_setter_thunk(uint32_t callback)
{
    return r1_touch_slider_callback_setter(callback);
}
uint32_t r1_touch_service_callback_registration(void)
{
    (void)r1_touch_ready_callback_setter((uint32_t)(uintptr_t)r1_touch_ready_irq_callback);
    (void)r1_touch_slider_callback_setter_thunk((uint32_t)(uintptr_t)r1_touch_slider_state_machine);
    return r1_touch_power_on_step();
}
_Noreturn void r1_touch_io_worker(void *argument)
{
    (void)argument;
    r1_native_sync_wait(9);
    osMessageQueueId_t queue=osMessageQueueNew(50,44,NULL);
    r1_touch_task_message_queue=queue;
    if (!queue) r1_bae8_rx_allocation_fault();
    (void)r1_touch_service_callback_registration();
    r1_native_sync_signal(9);
    r1_touch_io_watchdog=r1_native_watchdog_register("touch",10000);
    for (;;) {
        r1_native_watchdog_arm(r1_touch_io_watchdog);
        uint32_t flags=osThreadFlagsWait(0xffffff,0,UINT32_MAX);
        r1_native_watchdog_disarm(r1_touch_io_watchdog);
        if (flags-1u<UINT32_C(0x7fffffff)) r1_iqs7211e_touch_task_dispatcher(flags);
        r1_native_watchdog_feed(r1_touch_io_watchdog);
    }
}
