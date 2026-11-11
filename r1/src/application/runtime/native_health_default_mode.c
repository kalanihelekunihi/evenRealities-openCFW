#include <stdint.h>
#include "native_sleep_wake.h"
extern void r1_temp_sleep_status_report(uint32_t);
extern void r1_gomore_sleep_force_wake_native(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);

__attribute__((section(".text.r1_native_health_default_mode_callback")))
void r1_native_health_default_mode_callback(const volatile void *event)
{
    if (*(const volatile uint8_t *)event!=0) return;
    if (r1_activity_mode!=1) return;
    r1_activity_mode=0;
    r1_temp_sleep_status_report(0);
    r1_gomore_sleep_force_wake_native();
    (void)r1_event_publish(12,(const void *)(uintptr_t)&r1_activity_mode,1);
}
