#include <stdint.h>
#include <stddef.h>
#include "native_temperature_state.h"
struct r1_event_context {void (*create)(void),(*stop)(void);void *thread,*queue;};
extern struct r1_event_context r1_event_system;
_Static_assert(offsetof(struct r1_event_context,thread)==8,"stock thread reference cell");
extern uint32_t r1_subscriber_register(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern void r1_temp_sleep_status_plan(const volatile void *);
/* Pointer-only contracts: these callbacks are not invoked in this unit. */
extern void r1_native_health_group4_a_callback(const volatile void *);
extern void r1_native_health_group1_a_callback(void);
extern void r1_native_health_group4_b_callback(const volatile void *);
extern void r1_native_health_group1_b_callback(void);
extern void r1_native_health_default_mode_callback(const volatile void *);

uint32_t r1_native_health_events_register_a(void)
{
    uint32_t thread=(uint32_t)(uintptr_t)&r1_event_system.thread;
    (void)r1_subscriber_register(4,(uint32_t)(uintptr_t)r1_native_health_group4_a_callback,thread);
    return r1_subscriber_register(1,(uint32_t)(uintptr_t)r1_native_health_group1_a_callback,thread);
}
uint32_t r1_native_health_events_register_b(void)
{
    uint32_t thread=(uint32_t)(uintptr_t)&r1_event_system.thread;
    (void)r1_subscriber_register(4,(uint32_t)(uintptr_t)r1_native_health_group4_b_callback,thread);
    return r1_subscriber_register(1,(uint32_t)(uintptr_t)r1_native_health_group1_b_callback,thread);
}
void r1_native_temperature_disable_streams_callback(const volatile void *status)
{
    if (*(const volatile uint8_t *)status==1) return;
    for (uint32_t i=0;i<3;i++) {
        uint32_t handle=r1_temperature_mode_handles[i];
        if (handle) {
            r1_sensor_stream_unregister_by_name("temp",handle);
            r1_temperature_mode_handles[i]=0;
        }
    }
}
uint32_t r1_native_health_mode_topics_register(void)
{
    uint32_t thread=(uint32_t)(uintptr_t)&r1_event_system.thread;
    (void)r1_subscriber_register(4,(uint32_t)(uintptr_t)r1_native_temperature_disable_streams_callback,thread);
    return r1_subscriber_register(3,(uint32_t)(uintptr_t)r1_temp_sleep_status_plan,thread);
}
uint32_t r1_native_health_default_mode_initialize(void)
{
    (void)r1_gomore_authorization_dispatch_native(3,1);
    return r1_subscriber_register(4,(uint32_t)(uintptr_t)r1_native_health_default_mode_callback,
        (uint32_t)(uintptr_t)&r1_event_system.thread);
}
