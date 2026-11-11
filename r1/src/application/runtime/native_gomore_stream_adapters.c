#include <stdint.h>
#include "native_gomore_authorization.h"
extern uint32_t r1_gomore_sensor_output_dispatch_native(void);
static uint32_t sensor_in_use(uint32_t mask)
{
    for (uint8_t i=0;i<7;i++) {
        uint32_t flags=r1_gomore_authorization_state.entries[i].flags;
        if ((flags&mask) && (flags&1u)) return 1;
    }
    return 0;
}
uint32_t r1_gomore_sensor_take_ready(void)
{
    uint32_t acc=sensor_in_use(2);
    uint32_t raw=sensor_in_use(4);
    if (!(acc|raw)) return raw;
    uint32_t pending=r1_gomore_authorization_state.padding0[0];
    uint32_t acc_ready=pending&1u,raw_ready=(pending>>1)&1u;
    if ((acc && raw) ? (acc_ready && raw_ready) : ((acc && acc_ready)||(raw && raw_ready))) {
        (void)r1_gomore_sensor_output_dispatch_native();
        r1_gomore_authorization_state.padding0[0]=0;
        return 0;
    }
    return raw;
}
typedef int16_t r1_sensor_half __attribute__((may_alias));
static void sample_store(uint32_t address,float value)
{
    union {float value;uint32_t bits;} converted={.value=value};
    *(volatile uint32_t *)(uintptr_t)address=converted.bits;
}
uint32_t r1_gomore_acc_topic_adapter(uint32_t context,volatile void *payload,uint32_t length)
{
    (void)length;
    uint32_t data=(uint32_t)(uintptr_t)payload;
    uint32_t count=*(const volatile uint8_t *)(uintptr_t)(data+180u);
    if (!payload) return context;
    if (count>25) count=25;
    r1_gomore_sensor_state.acc_count=(uint8_t)count;
    for (uint8_t i=0;i<count;i++) {
        uint32_t address=data+(uint32_t)i*6u;
        int32_t y=*(const volatile r1_sensor_half *)(uintptr_t)(address+2u);
        uint32_t destination=r1_gomore_sensor_state.acc_y+(uint32_t)i*4u;
        sample_store(destination,(float)y*(-0.9765625f));
        int32_t x=*(const volatile r1_sensor_half *)(uintptr_t)address;
        destination=r1_gomore_sensor_state.acc_x+(uint32_t)i*4u;
        sample_store(destination,(float)x*0.9765625f);
        int32_t z=*(const volatile r1_sensor_half *)(uintptr_t)(address+4u);
        destination=r1_gomore_sensor_state.acc_z+(uint32_t)i*4u;
        sample_store(destination,(float)z*0.9765625f);
    }
    r1_gomore_authorization_state.padding0[0]|=1u;
    return r1_gomore_sensor_take_ready();
}
uint32_t r1_gomore_raw_hr_topic_adapter(uint32_t context,volatile void *payload,uint32_t length)
{
    (void)length;
    uint32_t data=(uint32_t)(uintptr_t)payload;
    uint32_t count=*(const volatile uint8_t *)(uintptr_t)data;
    if (!payload) return context;
    if (count>25) count=25;
    r1_gomore_sensor_state.raw_hr_count=(uint8_t)count;
    for (uint8_t i=0;i<count;i++) {
        union {float value;uint32_t bits;} sample;
        sample.value=*(const volatile float *)(uintptr_t)(data+4u+(uint32_t)i*4u);
        uint32_t destination=r1_gomore_sensor_state.raw_hr+(uint32_t)i*4u;
        sample_store(destination,(float)sample.bits);
    }
    r1_gomore_authorization_state.padding0[0]|=2u;
    return r1_gomore_sensor_take_ready();
}
