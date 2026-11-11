#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_binary64_reverse_subtract_bits(uint64_t,uint64_t);
__attribute__((section(".r1.math.ceil_data"),used))
const uint32_t r1_native_ceil_data[6]={0x8800759cu,0x7e37e43cu,0,0,0x3ff00000u,0x000fffffu};
__attribute__((section(".r1.math.floor_data"),used))
const uint32_t r1_native_floor_data[6]={0x8800759cu,0x7e37e43cu,0,0,0xbff00000u,0x000fffffu};
static uint32_t compare_carry(uint64_t a,uint64_t b)
{
    return (r1_binary64_comparison_cz(a,b)>>29)&1u;
}
static uint64_t directed_bits(uint64_t bits,uint32_t down)
{
    uint32_t low=(uint32_t)bits,high=(uint32_t)(bits>>32);
    int32_t exponent=(int32_t)((high>>20)&2047u)-1023;
    const uint64_t huge=UINT64_C(0x7e37e43c8800759c);
    if (exponent<20) {
        if (exponent<0) {
            if (compare_carry(r1_format_double_add_bits(bits,huge),0)) return bits;
            if (down) {
                if ((int32_t)high>=0) return 0;
                if ((high&0x7fffffffu)|low) return UINT64_C(0xbff0000000000000);
            } else {
                if ((int32_t)high<0) return UINT64_C(0x8000000000000000);
                if (high|low) return UINT64_C(0x3ff0000000000000);
            }
            return bits;
        }
        uint32_t mask=0xfffffu>>(uint32_t)exponent;
        if (!((high&mask)|low)) return bits;
        if (compare_carry(r1_format_double_add_bits(bits,huge),0)) return bits;
        if (down ? (int32_t)high<0 : (int32_t)high>0) high+=0x100000u>>(uint32_t)exponent;
        high&=~mask;low=0;
    } else {
        if (exponent>51) return bits;
        uint32_t mask=0xffffffffu>>((uint32_t)exponent-20u);
        if (!(low&mask)) return bits;
        if (compare_carry(r1_binary64_reverse_subtract_bits(bits,huge),0)) return bits;
        if (down ? (int32_t)high<0 : (int32_t)high>0) {
            if (exponent==20) ++high;
            else {
                uint32_t incremented=low+(1u<<(52u-(uint32_t)exponent));
                high+=(incremented<low);low=incremented;
            }
        }
        low&=~mask;
    }
    return ((uint64_t)high<<32)|low;
}
double r1_native_ceil(double value)
{
    union {double value;uint64_t bits;} input={.value=value};
    input.bits=directed_bits(input.bits,0);return input.value;
}
double r1_native_floor(double value)
{
    union {double value;uint64_t bits;} input={.value=value};
    input.bits=directed_bits(input.bits,1);return input.value;
}
