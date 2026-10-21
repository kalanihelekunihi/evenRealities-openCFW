#include <stdint.h>
extern uint64_t r1_binary64_round_integral_bits(uint64_t);
extern uint32_t r1_binary32_round_integral_bits(uint32_t);
extern uint64_t r1_binary64_subtract_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
__attribute__((section(".r1.math.round_data"),used))
const uint64_t r1_native_round_data[3]={UINT64_C(0x3ff0000000000000),UINT64_C(0x3fe0000000000000),UINT64_C(0xbfe0000000000000)};
static uint32_t compare_status(uint64_t a,uint64_t b,uint32_t reverse)
{
    register uint32_t r0 __asm__("r0")=(uint32_t)a,r1 __asm__("r1")=(uint32_t)(a>>32);
    register uint32_t r2 __asm__("r2")=(uint32_t)b,r3 __asm__("r3")=(uint32_t)(b>>32);
    uint32_t status;
    if (reverse) {
        __asm__ volatile("bl r1_binary64_compare_reverse_flags\n\tmrs %[status],APSR" : [status]"=r"(status),"+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3) : : "lr","cc","memory");
    } else {
        __asm__ volatile("bl r1_binary64_compare_flags\n\tmrs %[status],APSR" : [status]"=r"(status),"+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3) : : "lr","cc","memory");
    }
    return status;
}
double r1_native_round(double value)
{
    union {double value;uint64_t bits;} input={.value=value},result;
    const uint32_t carry=0x20000000u,zero=0x40000000u;
    const uint64_t one=UINT64_C(0x3ff0000000000000),half=UINT64_C(0x3fe0000000000000);
    result.bits=r1_binary64_round_integral_bits(input.bits);
    uint64_t delta=r1_binary64_subtract_bits(input.bits,result.bits);
    uint32_t reverse=compare_status(delta,half|UINT64_C(0x8000000000000000),1);
    if (input.bits>>63) {
        if (!(reverse&carry) || (reverse&zero)) result.bits=r1_binary64_subtract_bits(result.bits,one);
        else if (!(compare_status(delta,half,0)&carry)) result.bits=r1_format_double_add_bits(result.bits,one);
    } else {
        if (!(reverse&carry)) result.bits=r1_binary64_subtract_bits(result.bits,one);
        else {
            uint32_t forward=compare_status(delta,half,0);
            if (!(forward&carry) || (forward&zero)) result.bits=r1_format_double_add_bits(result.bits,one);
        }
    }
    result.bits=(result.bits&UINT64_C(0x7fffffffffffffff))|(input.bits&UINT64_C(0x8000000000000000));
    return result.value;
}
float r1_native_roundf(float value)
{
    union {float value;uint32_t bits;} input={.value=value},result,delta,one={.bits=0x3f800000u};
    result.bits=r1_binary32_round_integral_bits(input.bits);
    __asm__ volatile("vsub.f32 %0,%1,%2" : "=t"(delta.value) : "t"(value),"t"(result.value));
    uint32_t doubled=delta.bits<<1;
    uint32_t subtract,add;
    if (input.bits>>31) {
        subtract=delta.bits>=0xbf000000u && doubled<=0xff000000u;
        add=!subtract && (int32_t)delta.bits>0x3f000000 && doubled<=0xff000000u;
    } else {
        subtract=delta.bits>0xbf000000u && doubled<=0xff000000u;
        add=!subtract && (int32_t)delta.bits>=0x3f000000 && doubled<=0xff000000u;
    }
    if (subtract) __asm__ volatile("vsub.f32 %0,%0,%1" : "+t"(result.value) : "t"(one.value));
    else if (add) __asm__ volatile("vadd.f32 %0,%0,%1" : "+t"(result.value) : "t"(one.value));
    result.bits=(result.bits&0x7fffffffu)|(input.bits&0x80000000u);
    return result.value;
}
