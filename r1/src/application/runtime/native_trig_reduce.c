#include <stdint.h>
/* Authenticated window includes four words before the nominal table. The
 * native signed index reaches these words for small encoded exponents. */
__attribute__((section(".r1.math.trig_reduce_table"),used))
const uint32_t r1_trig_reduce_table[12]={0x6e09c32d,0xbe8afdb7,0,0,0,0xa2f9836e,0x4e441529,0xfc2757d1,0xf534ddc0,0xdb629599,0x3c439041,0xfe5163ab};
__attribute__((section(".r1.math.trig_reduce_coeff"),used))
const uint32_t r1_trig_reduce_coeff[5]={0x36000000,0x2c800000,0x29fdaa22,0x2fc90fdb,0x2fc90000};
typedef union {uint32_t bits;float value;} word_float;
static float fbits(uint32_t bits){word_float x={.bits=bits};return x.value;}
static uint32_t bits(float value){word_float x={.value=value};return x.bits;}
#define BINARY(name,instruction) static float name(float a,float b){float r;__asm__ volatile(instruction " %0,%1,%2":"=t"(r):"t"(a),"t"(b));return r;}
BINARY(add,"vadd.f32")
BINARY(sub,"vsub.f32")
BINARY(mul,"vmul.f32")
static float madd(float accumulator,float a,float b){__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static float convert(uint32_t x,int is_signed){float r=fbits(x);if(is_signed)__asm__ volatile("vcvt.f32.s32 %0,%0":"+t"(r));else __asm__ volatile("vcvt.f32.u32 %0,%0":"+t"(r));return r;}
/* Raw ABI: R0 output pointer, R1 input encoding, S0 incoming/result slot. */
float r1_native_trig_reduce32(uint32_t *quadrant,uint32_t input,float incoming_s0)
{
    if((input<<1)>=0xff000000u){*quadrant=0xffffffffu;return incoming_s0;}
    uint32_t significand=0x80000000u|(input<<8);
    int32_t exponent=(int32_t)((input>>23)&255)-120;
    uint32_t index=(uint32_t)((exponent>>5)+4),shift=(uint32_t)exponent&31;
    uint32_t a=r1_trig_reduce_table[index],b=r1_trig_reduce_table[index+1],c=r1_trig_reduce_table[index+2];
    if(shift){a=(a<<shift)|(b>>(32-shift));b=(b<<shift)|(c>>(32-shift));c=(c<<shift)|(r1_trig_reduce_table[index+3]>>(32-shift));}
    uint64_t pa=(uint64_t)a*significand,pb=(uint64_t)b*significand,pc=(uint64_t)c*significand;
    uint32_t low=(uint32_t)pb+(uint32_t)(pc>>32),carry=low<(uint32_t)(pc>>32);
    uint32_t mid=(uint32_t)(pb>>32)+(uint32_t)pa+carry;
    uint32_t top=(uint32_t)(pa>>32)+(carry ? mid<=(uint32_t)(pb>>32) : mid<(uint32_t)(pb>>32));
    uint32_t q=(top+32)>>6;
    float signed_part=convert((top<<26)|((mid>>19)<<13),1);
    float fraction=convert(mid<<13,0);
    *quadrant=q;
    float upper=mul(fraction,fbits(r1_trig_reduce_coeff[0]));
    float lower=mul(convert(low,0),fbits(r1_trig_reduce_coeff[1]));
    float combined=add(add(signed_part,upper),lower);
    float rounded=fbits((bits(combined)+0x800u)&~0xfffu);
    float correction=sub(lower,sub(sub(rounded,signed_part),upper));
    float result=mul(rounded,fbits(r1_trig_reduce_coeff[2]));
    result=madd(result,correction,fbits(r1_trig_reduce_coeff[3]));
    result=madd(result,rounded,fbits(r1_trig_reduce_coeff[4]));
    if(input>>31){*quadrant=0x10000000u-q;__asm__ volatile("vneg.f32 %0,%0":"+t"(result));}
    return result;
}
