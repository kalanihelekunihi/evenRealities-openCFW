#include <stdint.h>
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
__attribute__((section(".r1.math.divzero64_data"),used)) const uint64_t r1_divzero64_data[2]={0,UINT64_C(0x3ff0000000000000)};
__attribute__((section(".r1.math.invalid64_data"),used)) const uint64_t r1_invalid64_data=0;
__attribute__((section(".r1.math.high64_data"),used)) const uint64_t r1_high64_data=UINT64_C(0x7000000000000000);
__attribute__((section(".r1.math.low64_data"),used)) const uint64_t r1_low64_data=UINT64_C(0x1000000000000000);
__attribute__((section(".r1.math.divzero32_data"),used)) const uint32_t r1_divzero32_data=0;
__attribute__((section(".r1.math.invalid32_data"),used)) const uint32_t r1_invalid32_data=0;
__attribute__((section(".r1.math.high32_data"),used)) const uint32_t r1_high32_data=0x70000000u;
__attribute__((section(".r1.math.low32_data"),used)) const uint32_t r1_low32_data=0x10000000u;
static double as_double(uint64_t bits)
{ union {uint64_t bits;double value;} x={.bits=bits};return x.value; }
double r1_math_divzero64(void)
{ return as_double(r1_format_double_divide_bits(UINT64_C(0x3ff0000000000000),0)); }
double r1_math_self_add64(double value)
{ union {double value;uint64_t bits;} x={.value=value};return as_double(r1_format_double_add_bits(x.bits,x.bits)); }
double r1_math_add64(double a,double b)
{ union {double value;uint64_t bits;} x={.value=a},y={.value=b};return as_double(r1_format_double_add_bits(x.bits,y.bits)); }
double r1_math_invalid64(void)
{ return as_double(r1_format_double_divide_bits(0,0)); }
double r1_math_high_square64(void)
{ return as_double(r1_format_double_multiply_bits(UINT64_C(0x7000000000000000),UINT64_C(0x7000000000000000))); }
double r1_math_low_square64(void)
{ return as_double(r1_format_double_multiply_bits(UINT64_C(0x1000000000000000),UINT64_C(0x1000000000000000))); }
float r1_math_divzero32(void)
{
    union {uint32_t bits;float value;} one={.bits=0x3f800000u},zero={.bits=0};float result;
    __asm__ volatile("vdiv.f32 %0,%1,%2" : "=t"(result) : "t"(one.value),"t"(zero.value));return result;
}
float r1_math_self_add32(float value)
{ float result;__asm__ volatile("vadd.f32 %0,%1,%1" : "=t"(result) : "t"(value));return result; }
float r1_math_add32(float a,float b)
{ float result;__asm__ volatile("vadd.f32 %0,%1,%2" : "=t"(result) : "t"(a),"t"(b));return result; }
float r1_math_invalid32(void)
{ union {uint32_t bits;float value;} zero={.bits=0};float result;__asm__ volatile("vdiv.f32 %0,%1,%1" : "=t"(result) : "t"(zero.value));return result; }
float r1_math_high_square32(void)
{ union {uint32_t bits;float value;} high={.bits=0x70000000u};float result;__asm__ volatile("vmul.f32 %0,%1,%1" : "=t"(result) : "t"(high.value));return result; }
float r1_math_low_square32(void)
{ union {uint32_t bits;float value;} low={.bits=0x10000000u};float result;__asm__ volatile("vmul.f32 %0,%1,%1" : "=t"(result) : "t"(low.value));return result; }
