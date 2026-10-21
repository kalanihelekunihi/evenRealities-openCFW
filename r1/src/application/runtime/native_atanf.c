#include <stdint.h>
extern uint32_t r1_binary32_classify_bits(uint32_t,uint32_t,uint32_t,uint32_t);
extern float r1_math_low_square32(void);
extern float r1_math_self_add32(float);
__attribute__((section(".r1.math.atanf_data"),used))
const uint32_t r1_atanf_data[14]={0,0xbfc90000,0xb9fdaa22,0x3fc90000,0x39fdaa22,0x3eed6000,0x37ce0ac3,0xbd65ad2d,0x3dd5b88f,0xbe11b50f,0x3e4cc861,0xbeaaaaa8,0xbfc90fdb,0x3fc90fdb};
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
float r1_native_atanf(float value)
{
    uint32_t input=bits(value),doubled=input<<1;
    if (doubled+0x8e000000u>=0x25000000u) {
        if (doubled<0x72000000u) {
            if (r1_binary32_classify_bits(input,0,0,0)==4) (void)r1_math_low_square32();
            return value;
        }
        if (doubled>0xff000000u) return r1_math_self_add32(value);
        return fbits(r1_atanf_data[input>>31 ? 12 : 13]);
    }
    float low,high,reduced=value;
    if (doubled<=0x7f000000u) low=high=fbits(r1_atanf_data[0]);
    else {
        high=fbits(r1_atanf_data[input>>31 ? 1 : 3]);
        low=fbits(r1_atanf_data[input>>31 ? 2 : 4]);
        reduced=divide(fbits(0xbf800000u),value);
    }
    uint32_t encoded=bits(reduced);
    if ((encoded<<1)>0x7e000000u) {
        float half;
        if (encoded>>31) {
            half=fbits(0xbf000000u);
            high=sub(high,fbits(r1_atanf_data[5]));low=sub(low,fbits(r1_atanf_data[6]));
        } else {
            half=fbits(0x3f000000u);
            high=add(high,fbits(r1_atanf_data[5]));low=add(low,fbits(r1_atanf_data[6]));
        }
        float numerator=sub(reduced,half);
        float denominator=madd(fbits(0x3f800000u),reduced,half);
        reduced=divide(numerator,denominator);
    }
    float square=mul(reduced,reduced);
    float polynomial=madd(fbits(r1_atanf_data[8]),square,fbits(r1_atanf_data[7]));
    polynomial=madd(fbits(r1_atanf_data[9]),square,polynomial);
    polynomial=madd(fbits(r1_atanf_data[10]),square,polynomial);
    polynomial=madd(fbits(r1_atanf_data[11]),square,polynomial);
    float cube=mul(reduced,square);
    float result=madd(low,cube,polynomial);
    result=add(result,reduced);
    return add(result,high);
}
