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
