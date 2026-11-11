/* Native5/10 and6/9 packed conversion ABI and array callback.
 * Actual portable bit backends; hard-float S0 input/return, core packed return.
 */
#include "native_packed_conversion.h"
#include <stdint.h>
extern uint32_t goodix_primitives_packed_5_10_to_f32_bits(uint16_t);
extern uint32_t goodix_primitives_packed_6_9_to_f32_bits(uint16_t);
extern uint16_t goodix_primitives_f32_bits_to_packed_5_10(uint32_t);
extern uint16_t goodix_primitives_f32_bits_to_packed_6_9(uint32_t);
static float F(uint32_t u){union{uint32_t u;float f;}v={.u=u};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
float r1_goodix_native_unpack_5_10(uint32_t x){return F(goodix_primitives_packed_5_10_to_f32_bits((uint16_t)x));}
float r1_goodix_native_unpack_6_9(uint32_t x){return F(goodix_primitives_packed_6_9_to_f32_bits((uint16_t)x));}
uint32_t r1_goodix_native_pack_5_10(float x){return goodix_primitives_f32_bits_to_packed_5_10(B(x));}
uint32_t r1_goodix_native_pack_6_9(float x){return goodix_primitives_f32_bits_to_packed_6_9(B(x));}

/* Native0x28dec: callback receives float in S0 and returns a core word.
 * Cached bases/count/callback; signed count; live input reads and u16 stores. */
void r1_goodix_native_pack_array(void *output,const void *input,int32_t count,uint32_t (*convert)(float))
{
 uintptr_t out=(uintptr_t)output,in=(uintptr_t)input;
 for(int32_t i=0;i<count;++i){uint32_t bits=*(const volatile uint32_t *)(in+(uint32_t)i*4u);uint32_t value=convert(F(bits));*(volatile uint16_t *)(out+(uint32_t)i*2u)=(uint16_t)value;}
}
