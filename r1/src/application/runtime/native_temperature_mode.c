#include <stdint.h>
#include <stddef.h>

/* Authenticated fields only: cold RW8 @20006e4c, ZI handles12 @2001e3cc,
 * and timing record14 @2001e3dc. Adjacent measurement state is not owned. */
#include "native_temperature_state.h"
volatile struct r1_temperature_mode_control r1_temperature_mode_control
    __attribute__((section(".r1.temperature.mode.control"),aligned(4))) = {0};
volatile uint32_t r1_temperature_mode_handles[3]
    __attribute__((section(".bss.r1.temperature.mode.handles"),aligned(4)));
volatile uint8_t r1_temperature_timing_record[14]
    __attribute__((section(".bss.r1.temperature.timing.record"),aligned(2)));

extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_health_mode_get(void);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
/* Native sample callback is supplied by native_temperature_sample.c. */
extern void r1_temperature_stream_sample_callback(uint32_t,uint32_t,uint32_t);

void r1_temperature_periodic_timer_callback(void)
{
    if (!r1_health_mode_get() || r1_temperature_mode_handles[1]) return;
    __aeabi_memclr((void *)r1_temperature_timing_record,14);
    r1_temperature_timing_record[12]=1;
    r1_temperature_mode_handles[1]=r1_sensor_stream_register_by_name(
        "temp","timing",(uintptr_t)r1_temperature_stream_sample_callback,1,1);
}

void r1_temperature_mode_transition(uint32_t old_mode,uint32_t new_mode)
{
    if (old_mode==new_mode) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x0c000000,"[RING]temp mode is same","[RING]temp mode is same");
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0003,"temp mode is same");
        return;
    }
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c800000,"[RING]algo temp mode change: old_mode:%d, new_mode:%d","[RING]algo temp mode change: old_mode:%d, new_mode:%d",old_mode,new_mode);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0003,"algo temp mode change: old_mode:%d, new_mode:%d",old_mode,new_mode);
    /* Native indexing has no old-mode bounds check. Preserve its 32-bit
     * address calculation without C out-of-bounds array indexing. */
    volatile uint32_t *slot=(volatile uint32_t *)(uintptr_t)
        ((uint32_t)(uintptr_t)r1_temperature_mode_handles+(old_mode<<2));
    uint32_t handle=*slot;
    if (handle) {
        r1_sensor_stream_unregister_by_name("temp",handle);
        *slot=0;
    }
    if (old_mode==1) {
        uint32_t timer=r1_temperature_mode_control.timer;
        if (timer) {
            (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
            r1_temperature_mode_control.timer=0;
        }
    }
    if (new_mode==1 && !r1_temperature_mode_control.timer) {
        r1_temperature_mode_control.timer=r1_stream_timer_create_front(
            (uint32_t)(uintptr_t)r1_temperature_periodic_timer_callback,600000,0);
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x0c400000,"[RING]algo temp timing mode timer %d create","[RING]algo temp timing mode timer %d create",600);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0003,"algo temp timing mode timer %d create",600);
    }
}

void r1_temperature_mode_set(uint32_t mode)
{
    if (mode>=3) return;
    r1_temperature_mode_transition(r1_temperature_mode_control.mode,mode);
    r1_temperature_mode_control.mode=(uint8_t)mode;
}
extern void r1_event_service_0004bab4(uint32_t)
    __attribute__((alias("r1_temperature_mode_set")));
