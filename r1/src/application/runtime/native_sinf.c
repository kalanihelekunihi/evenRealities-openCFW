#include <stdint.h>
extern uint32_t r1_binary32_classify_bits(uint32_t,uint32_t,uint32_t,uint32_t);
extern float r1_math_low_square32(void);
extern float r1_native_trig_reduce32(uint32_t *,uint32_t,float);
extern void r1_native_errno_set(uint32_t);
extern float r1_math_invalid32(void);
extern float r1_math_self_add32(float);
__attribute__((section(".r1.math.sinf_data"),used))
const uint32_t r1_sinf_data[14]={0x7e921fb6,0xbab23ab9,0x3d2a9fca,0xbeffffdd,0x46490e49,0x3f22f983,0x4b000000,0x3fc90000,0x39fda000,0x33a22000,0x2c34611a,0x394c6d33,0x3c0882da,0xbe2aaaa0};
typedef union {uint32_t bits;float value;} word_float;
static float fbits(uint32_t bits){word_float x={.bits=bits};return x.value;}
static uint32_t bits(float value){word_float x={.value=value};return x.bits;}
#define BINARY(name,instruction) static float name(float a,float b){float r;__asm__ volatile(instruction " %0,%1,%2":"=t"(r):"t"(a),"t"(b));return r;}
BINARY(add,"vadd.f32")
BINARY(sub,"vsub.f32")
BINARY(mul,"vmul.f32")
static float madd(float accumulator,float a,float b){__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static float msub(float accumulator,float a,float b){__asm__ volatile("vmls.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static float negate(float value){__asm__ volatile("vneg.f32 %0,%0":"+t"(value));return value;}
static uint32_t to_integer(float value){__asm__ volatile("vcvt.s32.f32 %0,%0":"+t"(value));return bits(value);}
float r1_native_sinf(float value)
{
    uint32_t input=bits(value),doubled=input<<1,quadrant;
    if(doubled<r1_sinf_data[0]) quadrant=doubled<0x73000000u ? 0xffffffffu : 0;
    else if((input&0x7fffffffu)<r1_sinf_data[4]) {
        float scaled=mul(value,fbits(r1_sinf_data[5]));
        float bias=fbits(r1_sinf_data[6]);
        float integral=input>>31 ? add(sub(scaled,bias),bias) : sub(add(scaled,bias),bias);
        quadrant=to_integer(integral)&3;
        value=msub(value,integral,fbits(r1_sinf_data[7]));
        value=msub(value,integral,fbits(r1_sinf_data[8]));
        value=msub(value,integral,fbits(r1_sinf_data[9]));
        value=msub(value,integral,fbits(r1_sinf_data[10]));
    } else value=r1_native_trig_reduce32(&quadrant,input,value);
    if(quadrant>>31) {
        if((bits(value)<<1)<0xff000000u){
            if(r1_binary32_classify_bits(bits(value),0,0,0)==4)(void)r1_math_low_square32();
            return value;
        }
        if((bits(value)<<1)==0xff000000u){r1_native_errno_set(1);return r1_math_invalid32();}
        return r1_math_self_add32(value);
    }
    float square=mul(value,value),result;
    if(quadrant&1) {
        float polynomial=madd(fbits(r1_sinf_data[2]),square,fbits(r1_sinf_data[1]));
        polynomial=madd(fbits(r1_sinf_data[3]),square,polynomial);
        result=madd(fbits(0x3f800000u),square,polynomial);
    } else {
        float polynomial=msub(fbits(r1_sinf_data[12]),square,fbits(r1_sinf_data[11]));
        polynomial=madd(fbits(r1_sinf_data[13]),square,polynomial);
        polynomial=mul(polynomial,square);
        result=madd(value,value,polynomial);
    }
    if(quadrant&2)result=negate(result);
    return result;
}
