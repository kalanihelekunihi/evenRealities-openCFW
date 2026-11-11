/* Stock 0x6f304. The frame count is at input byte 180; the callback handle
 * and any stream length argument do not select the path. */
#include <stdint.h>
#include <stddef.h>
#include "native_factory_mode.h"
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_legacy_bounded_reply_send(const void *,uint32_t);
volatile uint16_t r1_factory_motion_samples[3]
 __attribute__((section(".r1.factory.motion.samples"),aligned(2)));
typedef struct __attribute__((packed,may_alias)) {uint16_t value;} motion_half;
static inline uint16_t read_half(const void *p)
{return ((const volatile motion_half *)p)->value;}
static inline void write_half(void *p,uint16_t value)
{((volatile motion_half *)p)->value=value;}
void r1_motion_sample_event_adapter(uint32_t handle,uint16_t *samples)
{
    (void)handle;
    if(samples && read_half((const uint8_t *)samples+180) && !r1_factory_mode_state.active){
        _Alignas(8) uint8_t packet[36];
        __aeabi_memclr(packet,36);
        ((volatile uint8_t *)packet)[0]=0;
        ((volatile uint8_t *)packet)[1]=1;
        ((volatile uint8_t *)packet)[2]=64;
        ((volatile uint8_t *)packet)[3]=4;
        write_half(packet+4,read_half(samples));
        write_half(packet+6,read_half((const uint8_t *)samples+2));
        write_half(packet+8,read_half((const uint8_t *)samples+4));
        r1_legacy_bounded_reply_send(packet,10);
    }else if(r1_factory_mode_state.active && samples && read_half((const uint8_t *)samples+180)){
        r1_factory_motion_samples[0]=read_half(samples);
        r1_factory_motion_samples[1]=read_half((const uint8_t *)samples+2);
        r1_factory_motion_samples[2]=read_half((const uint8_t *)samples+4);
    }
}
