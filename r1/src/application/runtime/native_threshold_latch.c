/* Stock 0x8156c. Unsigned threshold checks use captured samples even if the
 * configuration getter mutates the cache or input. */
#include <stdint.h>
#include "native_factory_mode.h"
extern uint32_t r1_device_info_configuration_byte78_get(void);
extern void r1_kv_nv_r1_byte_set_a(uint32_t);
volatile uint32_t r1_factory_threshold_samples[3]
 __attribute__((section(".r1.factory.threshold.samples"),aligned(4)));
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} sample_word;
void r1_sensor_threshold_flag_latch(uint32_t handle,uint32_t *samples,uint32_t bytes)
{
    (void)handle;
    if(!r1_factory_mode_state.active || bytes<12u)return;
    uint32_t x=((const volatile sample_word *)samples)->value;
    uint32_t y=((const volatile sample_word *)((uintptr_t)samples+4u))->value;
    uint32_t z=((const volatile sample_word *)((uintptr_t)samples+8u))->value;
    r1_factory_threshold_samples[0]=x;
    r1_factory_threshold_samples[1]=y;
    r1_factory_threshold_samples[2]=z;
    uint32_t old=r1_device_info_configuration_byte78_get(),value=old;
    if(x<UINT32_C(8000000))value|=1u;
    if(y<UINT32_C(8000000))value|=2u;
    if(z<UINT32_C(8000000))value|=4u;
    if(value!=old)r1_kv_nv_r1_byte_set_a(value);
}
