#include <stdint.h>
#include <stddef.h>

struct r1_event_context {void (*create)(void),(*stop)(void);void *thread,*queue;};
extern struct r1_event_context r1_event_system;
_Static_assert(offsetof(struct r1_event_context,thread)==8,"stock thread reference cell");
volatile uint32_t r1_health_algorithm_stream_handle
    __attribute__((section(".r1.health.algorithm.stream_handle"),aligned(4)))=0;
volatile uint8_t r1_health_module_status
    __attribute__((section(".bss.r1.health.module.status")));
extern uint32_t r1_health_module_field_set(uint32_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern uint32_t r1_subscriber_register(uint32_t,uint32_t,uint32_t);
/* Pointer-only contracts: startup does not invoke these callback bodies. */
extern void r1_wear_adt_status_topic_callback(uint32_t);
extern void r1_wear_motion_topic_callback(uint32_t,uint32_t,uint32_t);
extern void r1_native_health_module_group4_callback(const volatile void *);
extern void r1_wear_sleep_status_topic_callback(const volatile void *);
extern uint32_t r1_wear_raw_hr_probe_start(void);

uint32_t r1_native_health_module_initialize(void)
{
    (void)r1_health_module_field_set((uint32_t)(uintptr_t)r1_wear_adt_status_topic_callback);
    if (!r1_health_algorithm_stream_handle) {
        uint32_t handle=r1_sensor_stream_register_by_name("acc","algo",
            (uintptr_t)r1_wear_motion_topic_callback,1,1);
        r1_health_algorithm_stream_handle=handle;
    }
    r1_health_module_status=2;
    uint32_t thread=(uint32_t)(uintptr_t)&r1_event_system.thread;
    (void)r1_subscriber_register(4,(uint32_t)(uintptr_t)r1_native_health_module_group4_callback,thread);
    (void)r1_subscriber_register(3,(uint32_t)(uintptr_t)r1_wear_sleep_status_topic_callback,thread);
    return r1_wear_raw_hr_probe_start();
}
