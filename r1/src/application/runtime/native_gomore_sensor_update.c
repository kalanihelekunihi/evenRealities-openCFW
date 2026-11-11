#include <stdint.h>
#include "native_float_bits.h"
extern volatile uint32_t r1_gomore_native_context;
volatile uint8_t r1_gomore_sensor_debug
    __attribute__((section(".r1.gomore.sensor.debug"),aligned(1)))=0;
extern void r1_gomore_log_native(uint32_t,uint32_t,const char *,...);
extern int32_t r1_gomore_runtime_validate_native(uint32_t,uint32_t);
extern uint32_t r1_gomore_host_input_update_native(volatile void *,uint32_t);
extern void r1_gomore_copy_output_native(volatile void *);
extern void gomore_primitives_noop_76500(void);
struct __attribute__((packed,may_alias)) sensor_update_word {uint32_t value;};
struct __attribute__((packed,may_alias)) sensor_update_half {int16_t value;};
static uint32_t word(uint32_t address)
{ return ((const volatile struct sensor_update_word *)(uintptr_t)address)->value; }
static void put_word(uint32_t address,uint32_t value)
{ ((volatile struct sensor_update_word *)(uintptr_t)address)->value=value; }
static double promote(uint32_t bits)
{
    union {uint64_t bits;double value;} result={.bits=r1_binary32_to_binary64_bits(bits)};
    return result.value;
}
uint32_t r1_gomore_timestamp_clamp_native(uint32_t timestamp)
{
    if (!timestamp) return 1;
    uint32_t last=word(word(r1_gomore_native_context+0x39dcu)+4u);
    if (last+3u>=timestamp && last<=timestamp+3u) return last+1u;
    return timestamp;
}
uint32_t r1_gomore_sensor_update_native(volatile void *packet)
{
    uint32_t data=(uint32_t)(uintptr_t)packet;
    if (r1_gomore_sensor_debug==1) {
        int32_t offset=((const volatile struct sensor_update_half *)(uintptr_t)(data+4u))->value;
        r1_gomore_log_native(2,0,"[Update] ts=%u tZ=%d",word(data),offset);
        double hr=promote(word(data+40u));
        r1_gomore_log_native(2,0,"hr=%f ",hr);
        r1_gomore_log_native(2,0,"[Update] accLen=%u\r\n",*(const volatile uint8_t *)(uintptr_t)(data+20u));
        for (uint32_t i=0;i<*(const volatile uint8_t *)(uintptr_t)(data+20u);i++) {
            double z=promote(word(word(data+16u)+i*4u));
            double y=promote(word(word(data+12u)+i*4u));
            double x=promote(word(word(data+8u)+i*4u));
            r1_gomore_log_native(2,0,"[Update][acc][%d] x=%f y=%f z=%f \r\n",i,x,y,z);
        }
        r1_gomore_log_native(2,0,"[Update] ppgLen=%u\r\n",*(const volatile uint8_t *)(uintptr_t)(data+28u));
        for (uint32_t i=0;i<*(const volatile uint8_t *)(uintptr_t)(data+28u);i++) {
            double sample=promote(word(word(data+24u)+i*4u));
            r1_gomore_log_native(2,0,"[Update][ppg][%d][%f]\r\n",i,sample);
        }
    }
    uint32_t context=r1_gomore_native_context;
    int32_t ready=*(const volatile int8_t *)(uintptr_t)(context+0x39d8u);
    if (ready<0) return (uint32_t)ready;
    int32_t status=r1_gomore_runtime_validate_native(word(data),0);
    if (status<0) {
        r1_gomore_log_native(2,1,"[Update][errorCode]=%d\r\n",status);
        return (uint32_t)status;
    }
    uint32_t index=r1_gomore_timestamp_clamp_native(word(data));
    context=r1_gomore_native_context;
    uint32_t slot=word(context+0x39dcu);
    if (!word(slot+4u)) put_word(slot+4u,index-1u);
    slot=word(context+0x39dcu);
    if (word(slot+4u)>=index) {
        r1_gomore_log_native(2,1,"[Update][errorCode]=%d\r\n",-4);
        return UINT32_C(0xfffffffc);
    }
    uint32_t result=r1_gomore_host_input_update_native(packet,index);
    /* Native 0x76500 is the existing C no-op; its result is unused. */
    gomore_primitives_noop_76500();
    r1_gomore_copy_output_native(packet);
    context=r1_gomore_native_context;
    slot=word(context+0x39dcu);
    put_word(slot+4u,index);
    slot=word(context+0x39dcu);
    uint32_t value=word(slot);
    value=((value<<1)|(value>>31))+2u;
    put_word(slot,(value>>1)|(value<<31));
    return result;
}
