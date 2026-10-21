#include <stdint.h>
/* Native helper interfaces transport binary64 bits through core registers.
 * They deliberately remain explicit providers: LLVM/Newlib compatibility does
 * not establish the observed native exceptional/subnormal arithmetic. */
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_to_unsigned_bits(uint64_t);
extern uint64_t r1_runtime_udivmod(uint64_t,uint64_t,uint64_t *);
__attribute__((section(".r1.format.decimal_zero"),used))
const uint8_t r1_format_decimal_zero[4]={48,0,0,0};
static uint64_t comparison_key(uint64_t bits)
{ return bits>>63 ? bits : UINT64_C(0x8000000000000000)-bits; }
uint32_t r1_format_decimal_digits(volatile uint32_t *result, uint32_t buffer,
                                uint32_t low, uint32_t high,
                                uint32_t precision, uint32_t mode)
{
    uint32_t exponent=0,begin=0,length=0;
    uint64_t value=((uint64_t)high<<32)|low;
    if (!value) {
        if (mode==1) exponent=~precision;
        result[0]=(uint32_t)(uintptr_t)r1_format_decimal_zero;
        result[1]=exponent;
        result[2]=1;
        result[3]=mode;
        return (uint32_t)(uintptr_t)result;
    }
    exponent=(uint32_t)((int32_t)(((high>>20)-1023u)*UINT32_C(0x4d10))>>16);
    for (;;) {
        uint32_t scale=mode==1 ? 0u-precision : exponent-precision+1u;
        uint32_t magnitude=(int32_t)scale<0 ? 0u-scale : scale;
        uint64_t power=UINT64_C(0x4014000000000000),factor=UINT64_C(0x3ff0000000000000);
        uint64_t binary_scale=(uint64_t)(UINT32_C(0x3ff00000)+(magnitude<<20))<<32;
        while (magnitude) {
            if (magnitude&1) factor=r1_format_double_multiply_bits(factor,power);
            power=r1_format_double_multiply_bits(power,power);
            magnitude=(uint32_t)((int32_t)magnitude>>1);
        }
        uint64_t scaled;
        if ((int32_t)scale<0) {
            scaled=r1_format_double_multiply_bits(value,binary_scale);
            scaled=r1_format_double_multiply_bits(scaled,factor);
        } else {
            scaled=r1_format_double_divide_bits(value,binary_scale);
            scaled=r1_format_double_divide_bits(scaled,factor);
        }
        uint64_t integer=UINT64_MAX;
        if (comparison_key(scaled)>comparison_key(UINT64_C(0x43f0000000000000)))
            integer=r1_format_double_to_unsigned_bits(r1_format_double_add_bits(scaled,UINT64_C(0x3fe0000000000000)));
        int32_t position=16;
        while (integer && position>=0) {
            uint64_t remainder;
            integer=r1_runtime_udivmod(integer,10,&remainder);
            *(volatile uint8_t *)(uintptr_t)(buffer+(uint32_t)position)=(uint8_t)(remainder+48u);
            --position;
        }
        begin=buffer+(uint32_t)(position+1);
        length=17u-(uint32_t)(position+1);
        if (mode==1) {
            if (!integer) { exponent=length-precision-1u;break; }
            precision=17;mode=0;continue;
        }
        if (integer || (int32_t)length>(int32_t)precision) ++exponent;
        else if ((int32_t)length<(int32_t)precision) --exponent;
        else break;
    }
    result[2]=length;
    result[3]=mode;
    result[0]=begin;
    result[1]=exponent;
    return (uint32_t)(uintptr_t)result;
}
