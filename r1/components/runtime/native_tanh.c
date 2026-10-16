#include <stdint.h>
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint64_t r1_binary64_reverse_subtract_bits(uint64_t,uint64_t);
extern uint64_t r1_native_fabs_core_bits(uint64_t);
extern uint32_t r1_binary64_classify_bits(uint64_t,uint32_t,uint32_t);
extern double r1_math_low_square64(void);
extern double r1_math_self_add64(double);
/* Explicit unresolved source dependency; never replaced with a synthetic body. */
extern double r1_native_expm1(double);
__attribute__((section(".r1.math.tanh_local"),used))
const uint32_t r1_tanh_local[10]={0x7ff00000,0,0,0x3ff00000,0x40360000,0x3ff00000,0,0x40000000,0,0xc0000000};
typedef union {double value;uint64_t bits;} encoded_double;
static double value(uint64_t bits){encoded_double x={.bits=bits};return x.value;}
static uint64_t bits(double value){encoded_double x={.value=value};return x.bits;}
static uint64_t local(unsigned index){return (uint64_t)r1_tanh_local[index]|((uint64_t)r1_tanh_local[index+1]<<32);}
double r1_native_tanh(double input)
{
    uint64_t x=bits(input),sign=x&UINT64_C(0x8000000000000000);
    uint32_t high=(uint32_t)(x>>32)&0x7fffffffu;
    if(high>=r1_tanh_local[0]) {
        if(high!=r1_tanh_local[0]||(uint32_t)x)return r1_math_self_add64(input);
        return value(local(2)|sign);
    }
    if(high>=r1_tanh_local[4])return value(local(2)^sign);
    if(high<0x3c800000u){
        if(r1_binary64_classify_bits(x,0,0)==4)(void)r1_math_low_square64();
        return input;
    }
    uint64_t absolute=r1_native_fabs_core_bits(x),result;
    if(high>=r1_tanh_local[5]) {
        uint64_t exponential=bits(r1_native_expm1(value(r1_format_double_multiply_bits(absolute,local(6)))));
        uint64_t denominator=r1_format_double_add_bits(exponential,local(6));
        uint64_t quotient=r1_format_double_divide_bits(local(6),denominator);
        result=r1_binary64_reverse_subtract_bits(quotient,local(2));
    } else {
        uint64_t exponential=bits(r1_native_expm1(value(r1_format_double_multiply_bits(absolute,local(8)))));
        uint64_t denominator=r1_format_double_add_bits(exponential,local(6));
        result=r1_format_double_divide_bits(exponential^UINT64_C(0x8000000000000000),denominator);
    }
    return value(result^sign);
}
