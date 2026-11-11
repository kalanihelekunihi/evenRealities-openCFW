#include <stdint.h>
#include "native_gomore_authorization.h"
#include <stddef.h>

/* Authorization entry 4 owns the shared cold-RW flag byte (value 4). */
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
/* These are the native interfaces, not the provider-rich analysis-plan APIs. */
extern uint32_t r1_gomore_sleep_interval_update_native(uint32_t,volatile void *);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern uint32_t r1_gomore_sleep_interval_dispatch_native(volatile uint32_t *,volatile void *);
extern void r1_gomore_final_sleep_record_publish_native(volatile uint32_t *,volatile void *);

void r1_gomore_sleep_force_wake_native(void)
{
    volatile uint8_t *sensor=pvPortMalloc(56);
    if (!sensor) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04000000,"[RING]gomore sensor_malloc failed","[RING]gomore sensor_malloc failed");
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0001,"gomore sensor_malloc failed");
        return;
    }
    __aeabi_memclr((void *)sensor,56);
    r1_gomore_sleep_interval_update_native(1,sensor);
    if (r1_gomore_wake_authorization_flags&1u)
        (void)r1_gomore_authorization_dispatch_native(4,0);
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t flags=sensor[8];
        uint32_t second=((const volatile uint32_t *)sensor)[1];
        uint32_t first=((const volatile uint32_t *)sensor)[0];
        (void)r1_structured_log_format(0x0cc00000,"[RING]gomore sleep force wake:%d-%d, %d","[RING]gomore sleep force wake:%d-%d, %d",first,second,flags);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t flags=sensor[8];
        uint32_t first=((const volatile uint32_t *)sensor)[0];
        uint32_t second=((const volatile uint32_t *)sensor)[1];
        nrf_log_frontend_std_3(0x001c0003,"gomore sleep force wake:%d-%d, %d",first,second,flags);
    }
    if (sensor[8]&8u) {
        _Alignas(8) struct {
            volatile uint32_t workspace[22];
            volatile uint32_t count;
        } output;
        output.count=0;
        __aeabi_memclr((void *)output.workspace,88);
        void *payload=pvPortMalloc(2880);
        if (payload) {
            __aeabi_memclr(payload,2880);
            output.workspace[2]=(uint32_t)(uintptr_t)payload;
            r1_gomore_sleep_interval_dispatch_native(&output.count,output.workspace);
            r1_gomore_final_sleep_record_publish_native(&output.count,output.workspace);
            vPortFree(payload);
        } else {
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                (void)r1_structured_log_format(0x04000000,"[RING]gomore sleep malloc failed","[RING]gomore sleep malloc failed");
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_0(0x001c0001,"gomore sleep malloc failed");
        }
    }
    vPortFree((void *)sensor);
}
