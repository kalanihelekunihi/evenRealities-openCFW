#include <stdint.h>
/* Authenticated native data spans; emitted separately for source ownership.
 * Their verification placement is distinct from original image identity. */
__attribute__((section(".r1.math.ceilf_data"),used))
const uint32_t r1_native_ceilf_data[2]={0x7149f2cau,0x007fffffu};
__attribute__((section(".r1.math.floorf_data"),used))
const uint32_t r1_native_floorf_data[3]={0x7149f2cau,0xbf800000u,0x007fffffu};
/* Native integer ordering, including NaN payloads and both zero encodings.
 * R0 returns a flag word; APSR NZCVQ is also the public runtime contract. */
uint32_t r1_binary32_compare_flags(uint32_t a,uint32_t b)
{
    uint32_t ka=(int32_t)a<0 ? a : 0x80000000u-a;
    uint32_t kb=(int32_t)b<0 ? b : 0x80000000u-b;
    uint32_t flags=kb<ka ? 0x80000000u : kb==ka ? 0x60000000u : 0x20000000u;
    __asm__ volatile("msr APSR_nzcvq,%0" : : "r"(flags) : "cc");
    return flags;
}
float r1_native_fmaxf(float a,float b)
{
    union {float value;uint32_t bits;} x={.value=a},y={.value=b};
    uint32_t flags=r1_binary32_compare_flags(x.bits,y.bits);
    return flags!=0x20000000u && (y.bits&0x7fffffffu)<=0x7f800000u ? b : a;
}
float r1_native_fminf(float a,float b)
{
    union {float value;uint32_t bits;} x={.value=a},y={.value=b};
    uint32_t flags=r1_binary32_compare_flags(x.bits,y.bits);
    return flags!=0x80000000u && (y.bits&0x7fffffffu)<=0x7f800000u ? b : a;
}
static float add_huge(float value)
{
    union {float value;uint32_t bits;} huge={.bits=0x7149f2cau};float sum;
    /* Native adds before checking whether an integral input needs rounding. */
    __asm__ volatile("vadd.f32 %0,%1,%2" : "=t"(sum) : "t"(value),"t"(huge.value));
    return sum;
}
static uint32_t compare_zero(float value)
{
    uint32_t status;
    __asm__ volatile("vcmpe.f32 %1,#0.0\n\tvmrs %0,fpscr" : "=r"(status) : "t"(value) : "cc");
    return status;
}
float r1_native_ceilf(float value)
{
    union {float value;uint32_t bits;} input={.value=value};
    int32_t exponent=(int32_t)((input.bits>>23)&255u)-127;
    if (exponent>=23) return value;
    float sum=add_huge(value);
    if (exponent<0) {
        if ((compare_zero(sum)>>28)==2u) {
            if ((int32_t)input.bits>0) input.bits=0x3f800000u;
            else if ((int32_t)input.bits<0) input.bits=0x80000000u;
        }
    } else {
        uint32_t mask=0x7fffffu>>(uint32_t)exponent;
        if (!(input.bits&mask)) return value;
        if ((compare_zero(sum)>>28)==2u) {
            if ((int32_t)input.bits>0) input.bits+=0x800000u>>(uint32_t)exponent;
            input.bits&=~mask;
        }
    }
    return input.value;
}
float r1_native_floorf(float value)
{
    union {float value;uint32_t bits;} input={.value=value};
    int32_t exponent=(int32_t)((input.bits>>23)&255u)-127;
    if (exponent>=23) return value;
    float sum=add_huge(value);
    if (exponent<0) {
        if ((compare_zero(sum)>>28)==2u) {
            if ((int32_t)input.bits>=0) input.bits=0;
            else if (input.bits!=0x80000000u) input.bits=0xbf800000u;
        }
    } else {
        uint32_t mask=0x7fffffu>>(uint32_t)exponent;
        if (!(input.bits&mask)) return value;
        if ((compare_zero(sum)>>28)==2u) {
            if ((int32_t)input.bits<0) input.bits+=0x800000u>>(uint32_t)exponent;
            input.bits&=~mask;
        }
    }
    return input.value;
}
double r1_native_fabs(double value)
{
    union {double value;uint64_t bits;} x={.value=value};
    x.bits&=UINT64_C(0x7fffffffffffffff);return x.value;
}
uint64_t r1_native_fabs_core_bits(uint64_t bits)
{
    uint64_t result=bits&UINT64_C(0x7fffffffffffffff);
    /* The native core-register entry additionally exposes its result in D0. */
    __asm__ volatile("vmov d0,%Q0,%R0" : : "r"(result) : "d0");
    return result;
}
float r1_native_compare_absf(float value)
{
    if (!(compare_zero(value)&0x20000000u)) {
        float negative;
        __asm__ volatile("vneg.f32 %0,%1" : "=t"(negative) : "t"(value));
        return negative;
    }
    return value;
}
