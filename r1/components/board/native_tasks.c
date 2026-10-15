#include <stdint.h>
#include <stddef.h>

struct r1_event_context { void (*create)(void),(*stop)(void); void *thread,*queue; };
struct r1_tx_context { void (*create)(void),(*stop)(void); void *thread,*queue; };
extern struct r1_event_context r1_event_sensor,r1_event_system,r1_event_storage;
extern struct r1_tx_context r1_tx_channel1,r1_tx_shared;
extern void *osMessageQueueNew(uint32_t,uint32_t,const void *);
extern int32_t osMessageQueueGet(void *,void *,uint8_t *,uint32_t);
extern uint32_t osThreadFlagsWait(uint32_t,uint32_t,uint32_t);
extern int32_t osDelay(uint32_t);
extern void r1_native_sync_wait(uint32_t),r1_native_sync_signal(uint32_t),r1_native_suspend_signal(uint32_t);
extern uint32_t r1_native_watchdog_register(const char *,uint32_t);
extern void r1_native_watchdog_arm(uint32_t),r1_native_watchdog_disarm(uint32_t),r1_native_watchdog_feed(uint32_t);
extern void r1_native_worker_park(uint32_t,uint32_t),r1_native_output_worker(void *);
extern void r1_native_event_dispatch(const void *);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_native_sensor_timer_poll(void);
extern void r1_native_motion_interrupt(void);
extern void r1_native_stream_initialize(void),r1_native_accelerometer_singleton(void);
extern void r1_native_stream_register(void),r1_native_temperature_singleton(void),r1_native_health_initialize(void);
extern void r1_native_service_hardware_initialize(void),r1_native_health_database_initialize(void);
extern void r1_native_hr_cache_initialize(void),r1_native_spo2_cache_initialize(void);
extern void r1_native_temperature_cache_initialize(void),r1_native_stress_cache_initialize(void);
extern void r1_native_activity_cache_initialize(void),r1_native_sleep_database_initialize(void);
extern void r1_native_hrv_cache_initialize(void),r1_native_proto_port_reset(void);
extern void r1_native_storage_hardware_initialize(void);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);

#define WATCHDOG(name) uint32_t r1_task_##name##_watchdog __attribute__((section(".r1.task." #name ".watchdog"),aligned(4)))
WATCHDOG(gtx);WATCHDOG(msgtx);WATCHDOG(sensor);WATCHDOG(service);WATCHDOG(storage);

static _Noreturn void fail(void)
{
    __asm__ volatile ("msr basepri, %0" :: "r"(UINT32_C(64)) : "memory");
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
    for (;;) {}
}
static _Noreturn void suspend(uint32_t group,uint32_t *watchdog)
{
    r1_native_watchdog_arm(*watchdog);r1_native_suspend_signal(group);
    for (;;) osDelay(UINT32_MAX);
}
static _Noreturn void output_loop(struct r1_tx_context *context,uint32_t group,uint32_t *watchdog)
{
    for (;;) {
        r1_native_watchdog_arm(*watchdog);
        uint32_t flags=osThreadFlagsWait(0x00ffffff,0,UINT32_MAX);
        r1_native_watchdog_disarm(*watchdog);
        if (flags-1u<UINT32_C(0x7fffffff)) {
            if (flags&1u) r1_native_output_worker(context);
            if (flags&0x800000u) { r1_native_worker_park(group,*watchdog);fail(); }
        }
        r1_native_watchdog_feed(*watchdog);
    }
}
static _Noreturn void record_loop(void **queue,uint32_t group,uint32_t *watchdog,uint32_t sensor)
{
    for (;;) {
        uint32_t timeout=sensor ? r1_native_sensor_timer_poll() : UINT32_MAX;
        r1_native_watchdog_arm(*watchdog);
        uint32_t flags=osThreadFlagsWait(0x00ffffff,0,timeout);
        r1_native_watchdog_disarm(*watchdog);
        if (flags-1u<UINT32_C(0x7fffffff)) {
            if (flags&0x400000u) {
                uint32_t record[4]={0,0,0,0};
                while (osMessageQueueGet(*queue,record,0,0)==0) r1_native_event_dispatch(record);
            }
            if (sensor && (flags&2u)) r1_native_motion_interrupt();
            if (flags&0x800000u) suspend(group,watchdog);
        }
        r1_native_watchdog_feed(*watchdog);
    }
}
void r1_native_task_gtx(void *argument)
{
    (void)argument;r1_native_sync_wait(10);
    r1_tx_shared.queue=osMessageQueueNew(20,4,0);
    if (!r1_tx_shared.queue) fail();
    r1_native_sync_signal(10);
    r1_task_gtx_watchdog=r1_native_watchdog_register("ble_gtx",10000);
    output_loop(&r1_tx_shared,10,&r1_task_gtx_watchdog);
}
void r1_native_task_msgtx(void *argument)
{
    (void)argument;r1_native_sync_wait(3);
    r1_tx_channel1.queue=osMessageQueueNew(50,4,0);
    if (!r1_tx_channel1.queue) fail();
    r1_native_sync_signal(3);
    r1_task_msgtx_watchdog=r1_native_watchdog_register("ble_msgtx",10000);
    output_loop(&r1_tx_channel1,3,&r1_task_msgtx_watchdog);
}
void r1_native_task_sensor(void *argument)
{
    (void)argument;r1_native_sync_wait(5);
    r1_event_system.queue=osMessageQueueNew(50,16,0);
    if (!r1_event_system.queue) fail();
    r1_native_stream_initialize();r1_native_accelerometer_singleton();r1_native_stream_register();
    r1_native_temperature_singleton();r1_native_health_initialize();r1_native_sync_signal(5);
    r1_task_sensor_watchdog=r1_native_watchdog_register("sensor",10000);
    r1_event_publish(5,0,0);
    record_loop(&r1_event_system.queue,5,&r1_task_sensor_watchdog,1);
}
void r1_native_task_service(void *argument)
{
    (void)argument;r1_native_sync_wait(7);
    r1_event_sensor.queue=osMessageQueueNew(50,16,0);
    if (!r1_event_sensor.queue) fail();
    r1_native_service_hardware_initialize();r1_native_health_database_initialize();
    r1_native_hr_cache_initialize();r1_native_spo2_cache_initialize();r1_native_temperature_cache_initialize();
    r1_native_stress_cache_initialize();r1_native_activity_cache_initialize();r1_native_sleep_database_initialize();
    r1_native_hrv_cache_initialize();r1_native_proto_port_reset();r1_native_sync_signal(7);
    r1_task_service_watchdog=r1_native_watchdog_register("service",10000);
    record_loop(&r1_event_sensor.queue,7,&r1_task_service_watchdog,0);
}
void r1_native_storage_delayed_callback(uint32_t argument)
{ (void)argument;r1_event_publish(0x2005,0,0); }
void r1_native_task_storage(void *argument)
{
    (void)argument;r1_native_sync_wait(0);
    r1_event_storage.queue=osMessageQueueNew(10,16,0);
    if (!r1_event_storage.queue) fail();
    r1_native_storage_hardware_initialize();
    r1_native_delayed_schedule(r1_native_storage_delayed_callback,0,3072);
    r1_native_sync_signal(0);
    r1_task_storage_watchdog=r1_native_watchdog_register("storage",10000);
    record_loop(&r1_event_storage.queue,0,&r1_task_storage_watchdog,0);
}
