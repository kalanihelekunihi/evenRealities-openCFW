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
__attribute__((section(".r1.math.exp_prefix"),used))
const uint32_t r1_exp_prefix[13]={0x40862e42,0x7ff00000,0x0,0x0,0xfefa39ef,0x40862e42,0xd52d3051,0xc0874910,0x3fd62e42,0x0,0x0,0x3ff00000,0x3ff0a2b2};
__attribute__((section(".r1.math.exp_middle"),used))
const uint32_t r1_exp_middle[3]={0x0,0x652b82fe,0x3ff71547};
__attribute__((section(".r1.math.exp_reduction"),used))
const uint32_t r1_exp_reduction[9]={0x0,0xfee00000,0x3fe62e42,0x35793c76,0x3dea39ef,0x3e300000,0x0,0x8800759c,0x7e37e43c};
__attribute__((section(".r1.math.exp_suffix"),used))
const uint32_t r1_exp_suffix[5]={0x0,0x0,0x40000000,0x0,0x1700000};
__attribute__((section(".r1.math.exp_high"),used))
const uint64_t r1_exp_high[2]={UINT64_C(0x3fe62e42fee00000),UINT64_C(0xbfe62e42fee00000)};
__attribute__((section(".r1.math.exp_low"),used))
const uint64_t r1_exp_low[2]={UINT64_C(0x3dea39ef35793c76),UINT64_C(0xbdea39ef35793c76)};
__attribute__((section(".r1.math.exp_half"),used))
const uint64_t r1_exp_half[2]={UINT64_C(0x3fe0000000000000),UINT64_C(0xbfe0000000000000)};
__attribute__((section(".r1.math.exp_polynomial"),used))
const uint64_t r1_exp_polynomial[5]={UINT64_C(0x3fc555555555553e),UINT64_C(0xbf66c16c16bebd93),UINT64_C(0x3f11566aaf25de2c),UINT64_C(0xbebbbd41c5d26bf1),UINT64_C(0x3e66376972bea4d0)};
typedef union {double value;uint64_t bits;} encoded_double;
static double value(uint64_t bits){encoded_double x={.bits=bits};return x.value;}
static uint64_t bits(double value){encoded_double x={.value=value};return x.bits;}
static uint32_t word(unsigned address){
 if(address<0x38eb4)return r1_exp_prefix[(address-0x38e80)/4];
 if(address<0x38ec8)return r1_exp_middle[(address-0x38ebc)/4];
 if(address<0x38ef0)return r1_exp_reduction[(address-0x38ecc)/4];
 return r1_exp_suffix[(address-0x38ef4)/4];
}
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
double r1_native_exp(double input)
{
 uint64_t x=bits(input);uint32_t high=(uint32_t)(x>>32)&0x7fffffffu,negative=(uint32_t)(x>>63);
 if(high>=word(0x38e80)){
  if(high>=word(0x38e84)){
   if(x&UINT64_C(0xfffffffffffff))return r1_math_self_add64(input);
   return negative ? value(number(0x38e88)) : input;
  }
  if(!forward_carry(x,number(0x38e90))){r1_native_errno_set(2);return r1_math_high_square64();}
  if(!reverse_carry(x,number(0x38e98))){r1_native_errno_set(2);return r1_math_low_square64();}
 }
 uint64_t one=number(0x38ea8),hi=0,lo=0;int32_t k;
 if(high>word(0x38ea0)){
  if(high<word(0x38eb0)){
   hi=sub(x,r1_exp_high[negative]);lo=r1_exp_low[negative];k=1-(int32_t)(2*negative);
  }else{
   k=(int32_t)r1_binary64_to_signed32_bits(add(mul(x,number(0x38ec0)),r1_exp_half[negative]));
   uint64_t integer=r1_signed32_to_binary64_bits((uint32_t)k);
   hi=reverse_sub(mul(integer,number(0x38ed0)),x);lo=mul(integer,number(0x38ed8));
  }
  x=sub(hi,lo);
 }else{
  if(high<word(0x38ee0)&&!forward_carry(add(x,number(0x38ee8)),one))return value(add(x,one));
  k=0;
 }
 uint64_t square=mul(x,x);
 uint64_t c=reverse_sub(mul(bits(r1_native_polynomial(value(square),r1_exp_polynomial,5)),square),x);
 uint64_t two=number(0x38ef8);
 if(k==0){uint64_t quotient=divide(mul(x,c),sub(c,two));return value(reverse_sub(sub(quotient,x),one));}
 uint64_t quotient=divide(mul(x,c),sub(two,c));
 uint64_t result=reverse_sub(sub(reverse_sub(quotient,lo),hi),one);
 if(k>=-1021)return value(scale_high(result,k));
 result=mul(scale_high(result,k+1000),number(0x38f00));
 if(r1_binary64_classify_bits(result,0,0)==4)(void)r1_math_low_square64();
 return value(result);
}
