#include <stdint.h>
extern uint32_t r1_binary32_classify_bits(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_native_errno_set(uint32_t);
extern float r1_math_self_add32(float);
extern float r1_math_high_square32(void);
extern float r1_math_low_square32(void);
__attribute__((section(".r1.math.expf_coeff"),used))
const uint32_t r1_expf_coeff[8]={0x1e500000,0x40b8aa3b,0x3e317000,0x3705fdf4,0x3d2abb12,0x3e2abb12,0x3effffff,0x3f7fffff};
__attribute__((section(".r1.math.expf_scale"),used))
const uint32_t r1_expf_scale[4]={0x4b000000,0x4e7e0000,0x85a00000,0};
/* Native order is base[4], residual[4], multiplier[4]. PC-relative pointer
 * offsets are authenticated separately and replaced by these named arrays. */
__attribute__((section(".r1.math.expf_tables"),used))
const uint32_t r1_expf_tables[12]={0x3f800000,0x3f983000,0x3fb50000,0x3fd74000,0,0x397e0a32,0x391e667f,0x391f995b,0x3f800000,0x3f9837f0,0x3fb504f3,0x3fd744fd};
__attribute__((section(".r1.math.tanhf_coeff"),used))
const uint32_t r1_tanhf_coeff[5]={0x3f0c9f54,0x41102cb3,0xbf52e2c6,0xbb7b11b2,0x401e2a1a};
typedef union {float value;uint32_t bits;} word_float;
static float fbits(uint32_t bits) {word_float x={.bits=bits};return x.value;}
static uint32_t bits(float value) {word_float x={.value=value};return x.bits;}
#define BINARY(name,instruction) static float name(float a,float b) {float r;__asm__ volatile(instruction " %0,%1,%2":"=t"(r):"t"(a),"t"(b));return r;}
BINARY(add,"vadd.f32")
BINARY(sub,"vsub.f32")
BINARY(mul,"vmul.f32")
BINARY(divide,"vdiv.f32")
static float madd(float accumulator,float a,float b)
{__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static float msub(float accumulator,float a,float b)
{__asm__ volatile("vmls.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static uint32_t to_signed(float a)
{word_float r;__asm__ volatile("vcvt.s32.f32 %0,%1":"=t"(r.value):"t"(a));return r.bits;}
static uint32_t to_unsigned(float a)
{word_float r;__asm__ volatile("vcvt.u32.f32 %0,%1":"=t"(r.value):"t"(a));return r.bits;}
static float from_signed(uint32_t a)
{float r;__asm__ volatile("vcvt.f32.s32 %0,%1":"=t"(r):"t"(fbits(a)));return r;}
float r1_native_expf(float value)
{
    uint32_t input=bits(value),slow=0;
    if ((input<<1)+0x99000000u>r1_expf_coeff[0]) {
        if (!(~input&0x7f800000u)) {
            if (input==0xff800000u) return fbits(r1_expf_scale[3]);
            return r1_math_self_add32(value);
        }
        if ((input<<1)<0x67000000u) return fbits(0x3f800000u);
        if ((input<<1)>r1_expf_scale[2]) {
            r1_native_errno_set(2);
            return input>>31 ? r1_math_low_square32() : r1_math_high_square32();
        }
        slow=1;
    }
    float scaled=mul(value,fbits(r1_expf_coeff[1]));
    scaled=add(fbits(input>>31 ? 0xbf000000u : 0x3f000000u),scaled);
    uint32_t integer=to_signed(scaled);float n=from_signed(integer);
    float reduced=msub(value,n,fbits(r1_expf_coeff[2]));
    reduced=msub(reduced,n,fbits(r1_expf_coeff[3]));
    float p=madd(fbits(r1_expf_coeff[5]),reduced,fbits(r1_expf_coeff[4]));
    p=madd(fbits(r1_expf_coeff[6]),reduced,p);
    p=madd(fbits(r1_expf_coeff[7]),reduced,p);
    p=mul(p,reduced);
    uint32_t index=integer&3u;
    float polynomial=madd(fbits(r1_expf_tables[4+index]),fbits(r1_expf_tables[8+index]),p);
    polynomial=add(polynomial,fbits(r1_expf_tables[index]));
    int32_t exponent=(int32_t)integer>>2;
    if (!slow) {
        float encoded=madd(fbits(r1_expf_scale[1]),from_signed((uint32_t)exponent),fbits(r1_expf_scale[0]));
        return mul(fbits(to_unsigned(encoded)),polynomial);
    }
    int32_t half=(int32_t)((uint32_t)exponent+((uint32_t)exponent>>31))>>1;
    float first=fbits(0x3f800000u+((uint32_t)half<<23));
    float second=fbits(0x3f800000u+((uint32_t)(exponent-half)<<23));
    float result=mul(second,mul(first,polynomial));uint32_t encoded=bits(result);
    if (!encoded) {r1_native_errno_set(2);return r1_math_low_square32();}
    if (encoded==0x7f800000u) {r1_native_errno_set(2);return r1_math_high_square32();}
    if (r1_binary32_classify_bits(encoded,0,0,0)==4) (void)r1_math_low_square32();
    return result;
}
float r1_native_tanhf(float value)
{
    uint32_t input=bits(value);float magnitude;
    __asm__ volatile("vabs.f32 %0,%1":"=t"(magnitude):"t"(value));
    if ((input<<1)>0xff000000u) return r1_math_self_add32(value);
    uint32_t absolute=bits(magnitude);float result;
    if ((int32_t)absolute>(int32_t)r1_tanhf_coeff[0] && (absolute<<1)<=0xff000000u) {
        if ((int32_t)absolute>(int32_t)r1_tanhf_coeff[1] && (absolute<<1)<=0xff000000u) result=fbits(0x3f800000u);
        else {
            float exponential=r1_native_expf(add(magnitude,magnitude));
            result=sub(fbits(0x3f800000u),divide(fbits(0x40000000u),add(exponential,fbits(0x3f800000u))));
        }
    } else if ((int32_t)absolute<0x39800000 && (absolute<<1)<=0xff000000u) {
        if (r1_binary32_classify_bits(absolute,0,0,0)==4) (void)r1_math_low_square32();
        result=magnitude;
    } else {
        float square=mul(magnitude,magnitude);
        float numerator=madd(fbits(r1_tanhf_coeff[2]),square,fbits(r1_tanhf_coeff[3]));
        numerator=mul(numerator,square);
        float denominator=add(square,fbits(r1_tanhf_coeff[4]));
        result=madd(magnitude,magnitude,divide(numerator,denominator));
    }
    if (input>>31) __asm__ volatile("vneg.f32 %0,%0":"+t"(result));
    return result;
}
