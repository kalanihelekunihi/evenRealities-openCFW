#include <stdint.h>
extern uint32_t r1_native_errno_set(uint32_t);
extern float r1_math_self_add32(float);
extern float r1_math_invalid32(void);
extern float r1_math_divzero32(void);
__attribute__((section(".r1.math.log10f_coeff"),used)) const uint32_t r1_log10f_coeff[2]={0x3e3202de,0x3e943d3b};
__attribute__((section(".r1.math.log10f_high"),used)) const uint32_t r1_log10f_high=0x3e9a2000;
__attribute__((section(".r1.math.log10f_tail"),used)) const uint32_t r1_log10f_tail[8]={0x369a84fc,0x3f5e5bd9,0x3da94f92,0xbdde7972,0x3e143e2d,0xbe5e5bd8,0x3c4b7b15,0x4b000000};
__attribute__((section(".r1.math.logf_coeff"),used)) const uint32_t r1_logf_coeff[2]={0x3eccf166,0x3f2aaaaa};
__attribute__((section(".r1.math.logf_high"),used)) const uint32_t r1_logf_high=0x3f317000;
__attribute__((section(".r1.math.logf_tail"),used)) const uint32_t r1_logf_tail[6]={0x3805fdf4,0x3e42ed21,0xbe80110a,0x3eaaabc1,0xbeffffff,0x4b000000};
/* Original order: log10 high[8], log10 low[8], log high[8], log low[8]. */
__attribute__((section(".r1.math.float_log_tables"),used)) const uint32_t r1_float_log_tables[32]={0,0x3d518000,0x3dc67000,0x3e0d9000,0x3e345000,0x3e57e000,0x3e78d000,0x3e8bc000,0,0x36a9d60a,0x378c1c43,0x38738f65,0x36a22d83,0x381f1d12,0x386f75b3,0x385a53d2,0,0x3df13000,0x3e647000,0x3ea30000,0x3ecf9000,0x3ef89000,0x3f0f4000,0x3f20e000,0,0x3783b715,0x387be3cd,0x38c5e10e,0x3891f660,0x380f5faf,0x383ebce1,0x3947f423};
typedef union {uint32_t bits;float value;} word_float;
static float fbits(uint32_t bits) {word_float x={.bits=bits};return x.value;}
static uint32_t bits(float value) {word_float x={.value=value};return x.bits;}
#define BINARY(name,instruction) static float name(float a,float b) {float r;__asm__ volatile(instruction " %0,%1,%2":"=t"(r):"t"(a),"t"(b));return r;}
BINARY(add,"vadd.f32")
BINARY(sub,"vsub.f32")
BINARY(mul,"vmul.f32")
BINARY(divide,"vdiv.f32")
static float madd(float accumulator,float a,float b)
{__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static float from_signed(uint32_t value)
{float r;__asm__ volatile("vcvt.f32.s32 %0,%1":"=t"(r):"t"(fbits(value)));return r;}
static uint32_t compare_zero(float value)
{uint32_t status;__asm__ volatile("vcmpe.f32 %1,#0.0\n\tvmrs %0,fpscr":"=r"(status):"t"(value):"cc");return status;}
static float kernel(float value,uint32_t base10)
{
    uint32_t input=bits(value);int32_t correction=0;
    if (input-0x800000u>=0x7f000000u) {
        if ((input<<1)>0xff000000u) return r1_math_self_add32(value);
        if (input==0x7f800000u) return value;
        if (!(compare_zero(value)&0x20000000u)) {r1_native_errno_set(1);return r1_math_invalid32();}
        if (compare_zero(value)&0x40000000u) {
            r1_native_errno_set(2);float result=r1_math_divzero32();
            __asm__ volatile("vneg.f32 %0,%0":"+t"(result));return result;
        }
        value=mul(value,fbits(0x4b000000u));input=bits(value);correction=-23;
    }
    uint32_t rounded=input+0x80000u,index=(rounded>>20)&7u;
    int32_t exponent=((int32_t)rounded>>23)-127;
    float anchor=fbits(0x3f800000u+(index<<20));
    float reduced=fbits(input-((uint32_t)exponent<<23));exponent+=correction;
    if ((uint32_t)exponent|index) {
        float numerator=sub(reduced,anchor),denominator=add(reduced,anchor);
        float ratio=divide(numerator,denominator),square=mul(ratio,ratio),cube,p;
        if (base10) {
            cube=mul(ratio,square);p=madd(fbits(r1_log10f_coeff[1]),square,fbits(r1_log10f_coeff[0]));
        } else {
            p=madd(fbits(r1_logf_coeff[1]),square,fbits(r1_logf_coeff[0]));cube=mul(ratio,square);
        }
        float polynomial=mul(cube,p);uint32_t table=base10 ? 0u : 16u;
        float high=madd(fbits(r1_float_log_tables[table+index]),from_signed((uint32_t)exponent),fbits(base10 ? r1_log10f_high : r1_logf_high));
        float low=madd(fbits(r1_float_log_tables[table+8+index]),from_signed((uint32_t)exponent),fbits(base10 ? r1_log10f_tail[0] : r1_logf_tail[0]));
        float sum=add(low,polynomial);
        sum=madd(sum,ratio,fbits(base10 ? r1_log10f_tail[1] : 0x40000000u));
        return add(high,sum);
    }
    float delta=sub(reduced,fbits(0x3f800000u)),p,square;
    if (base10) {
        p=madd(fbits(r1_log10f_tail[3]),delta,fbits(r1_log10f_tail[2]));square=mul(delta,delta);
        p=madd(fbits(r1_log10f_tail[4]),delta,p);p=madd(fbits(r1_log10f_tail[5]),delta,p);
        float result=mul(square,p);result=madd(result,delta,fbits(r1_log10f_tail[6]));
        return madd(result,delta,fbits(0x3ed80000u));
    }
    p=madd(fbits(r1_logf_tail[2]),delta,fbits(r1_logf_tail[1]));square=mul(delta,delta);
    p=madd(fbits(r1_logf_tail[3]),delta,p);p=madd(fbits(r1_logf_tail[4]),delta,p);
    return add(delta,mul(square,p));
}
float r1_native_logf(float value) {return kernel(value,0);}
float r1_native_log10f(float value) {return kernel(value,1);}
