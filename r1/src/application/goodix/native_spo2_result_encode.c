/* Stock 0x76a68: cached SpO2 result, including partial/error windows.
 * Keep owner reloads and ordered volatile stores: output may alias state.
 * Encoded software conversions intentionally preserve native edge semantics.
 */
#include <stdint.h>
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint32_t r1_binary64_to_signed32_bits(uint64_t);
static uint32_t word(uintptr_t p,uint32_t offset){return *(const volatile uint32_t *)(p+offset);}
static uint8_t byte(uintptr_t p,uint32_t offset){return *(const volatile uint8_t *)(p+offset);}
static void put(uintptr_t p,uint32_t offset,uint32_t value){*(volatile uint32_t *)(p+offset)=value;}
static uint32_t rounded_bits(uint32_t bits)
{
    uint64_t value=r1_binary32_to_binary64_bits(bits);
    value=r1_format_double_add_bits(value,UINT64_C(0x3fe0000000000000));
    return r1_binary64_to_signed32_bits(value);
}
static uint32_t scaled(uintptr_t state,uint32_t offset,float scale)
{
    union{float f;uint32_t u;} value;
    value.f=*(const volatile float *)(state+offset)*scale;
    return rounded_bits(value.u);
}
void r1_goodix_spo2_failure(const void *descriptor,void *owner,void *output)
{
    (void)descriptor;
    uintptr_t p=(uintptr_t)owner,out=(uintptr_t)output;
    put(out,0,scaled(word(p,0),24,10000.0f));
    uint32_t level=byte(word(p,0),28);
    put(out,4,(level&128u)?level|0xffffff00u:level);
    put(out,8,byte(word(p,0),29));put(out,12,0);
    put(out,16,rounded_bits(word(word(p,0),36)));
    put(out,20,scaled(word(p,0),40,100.0f));
    put(out,24,byte(word(p,0),44));
    put(out,28,scaled(word(p,0),48,100000.0f));
    put(out,32,scaled(word(p,0),52,100000.0f));
    put(out,36,0);put(out,40,0);
    put(out,44,scaled(word(p,0),64,10000.0f));
    put(out,48,0);put(out,52,0);put(out,56,0);put(out,60,0);
}
