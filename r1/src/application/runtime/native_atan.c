#include <stdint.h>
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint64_t r1_binary64_subtract_bits(uint64_t,uint64_t);
extern uint64_t r1_binary64_reverse_subtract_bits(uint64_t,uint64_t);
extern uint64_t r1_native_fabs_core_bits(uint64_t);
extern uint32_t r1_binary64_classify_bits(uint64_t,uint32_t,uint32_t);
extern double r1_math_low_square64(void);
extern double r1_math_self_add64(double);
extern double r1_native_polynomial(double,const uint64_t *,uint32_t);
__attribute__((section(".r1.math.atan_local"),used))
const uint32_t r1_atan_local[22]={0x44100000,0x7ff00000,0x54442d18,0x3ff921fb,0x54442d18,0xbff921fb,0x3fdc0000,0x3e200000,0x3ff30000,0x0,0x0,0x3ff00000,0x3fe60000,0x0,0x0,0x40000000,0x40038000,0x0,0x0,0x3ff80000,0x0,0xbff00000};
__attribute__((section(".r1.math.atan_odd"),used))
const uint64_t r1_atan_odd[6]={UINT64_C(0x3fd555555555550d),UINT64_C(0x3fc24924920083ff),UINT64_C(0x3fb745cdc54c206e),UINT64_C(0x3fb10d66a0d03d51),UINT64_C(0x3fa97b4b24760deb),UINT64_C(0x3f90ad3ae322da11)};
__attribute__((section(".r1.math.atan_even"),used))
const uint64_t r1_atan_even[5]={UINT64_C(0xbfc999999998ebc4),UINT64_C(0xbfbc71c6fe231671),UINT64_C(0xbfb3b0f2af749a6d),UINT64_C(0xbfadde2d52defd9a),UINT64_C(0xbfa2b4442c6a6c2f)};
__attribute__((section(".r1.math.atan_low"),used))
const uint64_t r1_atan_low[4]={UINT64_C(0x3c7a2b7f222f65e2),UINT64_C(0x3c81a62633145c07),UINT64_C(0x3c7007887af0cbbd),UINT64_C(0x3c91a62633145c07)};
__attribute__((section(".r1.math.atan_high"),used))
const uint64_t r1_atan_high[4]={UINT64_C(0x3fddac670561bb4f),UINT64_C(0x3fe921fb54442d18),UINT64_C(0x3fef730bd281f69b),UINT64_C(0x3ff921fb54442d18)};
typedef union {double value;uint64_t bits;} encoded_double;
static double value(uint64_t bits){encoded_double x={.bits=bits};return x.value;}
static uint64_t bits(double value){encoded_double x={.value=value};return x.bits;}
static uint64_t local(unsigned index){return (uint64_t)r1_atan_local[index]|((uint64_t)r1_atan_local[index+1]<<32);}
#define add r1_format_double_add_bits
#define mul r1_format_double_multiply_bits
#define divide r1_format_double_divide_bits
#define sub r1_binary64_subtract_bits
#define reverse_sub r1_binary64_reverse_subtract_bits
double r1_native_atan(double input)
{
    uint64_t x=bits(input);uint32_t original_high=(uint32_t)(x>>32),magnitude=original_high&0x7fffffffu;
    if(magnitude>=r1_atan_local[0]) {
        if(magnitude>r1_atan_local[1]||(magnitude==r1_atan_local[1]&&(uint32_t)x))return r1_math_self_add64(input);
        return value(local((int32_t)original_high>0 ? 2 : 4));
    }
    int reduction;
    if(magnitude<r1_atan_local[6]) {
        if(magnitude<r1_atan_local[7]) {
            if(r1_binary64_classify_bits(x,0,0)==4)(void)r1_math_low_square64();
            return input;
        }
        reduction=-1;
    } else {
        x=r1_native_fabs_core_bits(x);
        if(magnitude<r1_atan_local[8]) {
            if(magnitude<r1_atan_local[12]) {
                reduction=0;uint64_t denominator=add(x,local(14));
                x=divide(sub(mul(x,local(14)),local(10)),denominator);
            } else {
                reduction=1;uint64_t denominator=add(x,local(10));
                x=divide(sub(x,local(10)),denominator);
            }
        } else if(magnitude<r1_atan_local[16]) {
            reduction=2;uint64_t denominator=add(mul(x,local(18)),local(10));
            x=divide(sub(x,local(18)),denominator);
        } else {reduction=3;x=divide(local(20),x);}
    }
    uint64_t square=mul(x,x),fourth=mul(square,square);
    uint64_t odd=mul(bits(r1_native_polynomial(value(fourth),r1_atan_odd,6)),square);
    uint64_t even=mul(bits(r1_native_polynomial(value(fourth),r1_atan_even,5)),fourth);
    uint64_t correction=mul(add(odd,even),x);
    if(reduction<0)return value(reverse_sub(correction,x));
    uint64_t result=reverse_sub(sub(sub(correction,r1_atan_low[reduction]),x),r1_atan_high[reduction]);
    if(original_high>>31)result^=UINT64_C(0x8000000000000000);
    return value(result);
}
