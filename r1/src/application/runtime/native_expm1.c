#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern double r1_math_self_add64(double);
extern double r1_math_low_square64(void);
extern double r1_math_high_square64(void);
extern void r1_native_errno_set(uint32_t);
extern double r1_native_polynomial(double,const uint64_t *,uint32_t);
__attribute__((section(".r1.math.expm1_prefix"),used))
const uint32_t r1_expm1_prefix[28]={0x4043687a,0x40862e42,0x0,0xbff00000,0x7ff00000,0x0,0xfefa39ef,0x40862e42,0xc2f8f359,0x1a56e1f,0x0,0x0,0x3fd62e42,0x0,0x0,0x3fe00000,0x3ff0a2b2,0x0,0xfee00000,0x3fe62e42,0x35793c76,0x3dea39ef,0x35793c76,0xbdea39ef,0x652b82fe,0x3ff71547,0x0,0xbfe00000};
__attribute__((section(".r1.math.expm1_suffix"),used))
const uint32_t r1_expm1_suffix[15]={0x0,0x0,0x3ff00000,0x0,0x40080000,0x0,0x40180000,0x3c900000,0x0,0x0,0xbfd00000,0x0,0xc0000000,0x0,0x40000000};
__attribute__((section(".r1.math.expm1_polynomial"),used))
const uint64_t r1_expm1_polynomial[5]={UINT64_C(0xbfa11111111110f4),UINT64_C(0x3f5a01a019fe5585),UINT64_C(0xbf14ce199eaadbb7),UINT64_C(0x3ed0cfca86e65239),UINT64_C(0xbe8afdb76e09c32d)};
typedef union {double value;uint64_t bits;} encoded_double;
static double value(uint64_t bits){encoded_double x={.bits=bits};return x.value;}
static uint64_t bits(double value){encoded_double x={.value=value};return x.bits;}
static uint32_t word(unsigned address){return address<0x3ba58 ? r1_expm1_prefix[(address-0x3b9e8)/4] : r1_expm1_suffix[(address-0x3ba5c)/4];}
static uint64_t number(unsigned address){return (uint64_t)word(address)|((uint64_t)word(address+4)<<32);}
#define add r1_format_double_add_bits
#define mul r1_format_double_multiply_bits
#define divide r1_format_double_divide_bits
#define sub r1_binary64_subtract_bits
#define reverse_sub r1_binary64_reverse_subtract_bits
#define COMPARE(name,target) static uint32_t name(uint64_t a,uint64_t b){ \
 register uint32_t r0 __asm__("r0")=(uint32_t)a,r1 __asm__("r1")=(uint32_t)(a>>32); \
 register uint32_t r2 __asm__("r2")=(uint32_t)b,r3 __asm__("r3")=(uint32_t)(b>>32);uint32_t status; \
 __asm__ volatile("bl " target "\n\tmrs %[status],APSR":[status]"=r"(status),"+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3)::"lr","cc","memory");return(status>>29)&1u;}
COMPARE(forward_carry,"r1_binary64_compare_flags")
COMPARE(reverse_carry,"r1_binary64_compare_reverse_flags")
static uint64_t scale_high(uint64_t x,int32_t k){uint32_t high=(uint32_t)(x>>32)+((uint32_t)k<<20);return (x&UINT64_C(0xffffffff))|((uint64_t)high<<32);}
double r1_native_expm1(double input)
{
 uint64_t x=bits(input);uint32_t high=(uint32_t)(x>>32)&0x7fffffffu,negative=(uint32_t)(x>>63);
 if(high>=word(0x3b9e8)) {
  if(high>=word(0x3b9ec)) {
   if(high>=word(0x3b9f8)) {
    if((x&UINT64_C(0xfffffffffffff)))return r1_math_self_add64(input);
    return negative ? value(number(0x3b9f0)) : input;
   }
   if(!forward_carry(x,number(0x3ba00))){r1_native_errno_set(2);return r1_math_high_square64();}
  }
  if(negative && !reverse_carry(add(x,number(0x3ba08)),number(0x3ba10)))return value(number(0x3b9f0));
 }
 int32_t k;uint64_t correction=0,half=number(0x3ba20);
 if(high>word(0x3ba18)) {
  uint64_t hi,lo;
  if(high<word(0x3ba28)) {
   if(negative){hi=add(x,number(0x3ba30));lo=number(0x3ba40);k=-1;}
   else {hi=sub(x,number(0x3ba30));lo=number(0x3ba38);k=1;}
  } else {
   uint64_t scaled=mul(x,number(0x3ba48));
   k=(int32_t)r1_binary64_to_signed32_bits(add(scaled,negative ? number(0x3ba50) : half));
   uint64_t integer=r1_signed32_to_binary64_bits((uint32_t)k);
   hi=reverse_sub(mul(integer,number(0x3ba30)),x);
   lo=mul(integer,number(0x3ba38));
  }
  x=sub(hi,lo);correction=sub(reverse_sub(x,hi),lo);
 } else {
  if(high<word(0x3ba78)){
   if(r1_binary64_classify_bits(x,0,0)==4)(void)r1_math_low_square64();
   return input;
  }
  k=0;
 }
 uint64_t half_x=mul(x,half),square=mul(x,half_x);
 uint64_t r=add(mul(bits(r1_native_polynomial(value(square),r1_expm1_polynomial,5)),square),number(0x3ba60));
 uint64_t t=reverse_sub(mul(r,half_x),number(0x3ba68));
 uint64_t denominator=reverse_sub(mul(x,t),number(0x3ba70));
 uint64_t e=mul(divide(sub(r,t),denominator),square);
 if(k==0)return value(reverse_sub(sub(mul(x,e),square),x));
 e=sub(sub(mul(sub(e,correction),x),correction),square);
 if(k==-1)return value(sub(mul(sub(x,e),half),half));
 if(k==1){
  if(!reverse_carry(x,number(0x3ba80)))return value(mul(reverse_sub(add(x,half),e),number(0x3ba88)));
  return value(add(mul(sub(x,e),number(0x3ba90)),number(0x3ba60)));
 }
 if(k<=-2||k>56)return value(sub(scale_high(reverse_sub(reverse_sub(x,e),number(0x3ba60)),k),number(0x3ba60)));
 if(k<20){
  uint64_t base=(uint64_t)(0x3ff00000u-(0x200000u>>(uint32_t)k))<<32;
  return value(scale_high(reverse_sub(reverse_sub(x,e),base),k));
 }
 uint64_t base=(uint64_t)((1023u-(uint32_t)k)<<20)<<32;
 return value(scale_high(add(reverse_sub(add(e,base),x),number(0x3ba60)),k));
}
