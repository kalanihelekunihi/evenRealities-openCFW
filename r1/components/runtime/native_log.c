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
extern double r1_math_invalid64(void);
extern double r1_math_divzero64(void);
__attribute__((section(".r1.math.log_prefix"),used))
const uint32_t r1_log_prefix[12]={0x7ff00000,0x0,0x0,0x43500000,0x95f64,0x0,0x0,0x3ff00000,0x35793c76,0x3dea39ef,0xfee00000,0x3fe62e42};
__attribute__((section(".r1.math.log_suffix"),used))
const uint32_t r1_log_suffix[8]={0x0,0x55555555,0x3fd55555,0x0,0x3fe00000,0x0,0x40000000,0xfff9eb86};
__attribute__((section(".r1.math.log_zero"),used))
const uint64_t r1_log_zero[1]={UINT64_C(0x0)};
__attribute__((section(".r1.math.log_even"),used))
const uint64_t r1_log_even[3]={UINT64_C(0x3fd999999997fa04),UINT64_C(0x3fcc71c51d8e78af),UINT64_C(0x3fc39a09d078c69f)};
__attribute__((section(".r1.math.log_odd"),used))
const uint64_t r1_log_odd[4]={UINT64_C(0x3fe5555555555593),UINT64_C(0x3fd2492494229359),UINT64_C(0x3fc7466496cb03de),UINT64_C(0x3fc2f112df3e5244)};
typedef union {double value;uint64_t bits;} encoded_double;
static double value(uint64_t bits){encoded_double x={.bits=bits};return x.value;}
static uint64_t bits(double value){encoded_double x={.value=value};return x.bits;}
static uint32_t word(unsigned address){return address<0x396b8 ? r1_log_prefix[(address-0x39688)/4] : r1_log_suffix[(address-0x396bc)/4];}
static uint64_t number(unsigned address){return (uint64_t)word(address)|((uint64_t)word(address+4)<<32);}
#define add r1_format_double_add_bits
#define mul r1_format_double_multiply_bits
#define divide r1_format_double_divide_bits
#define sub r1_binary64_subtract_bits
#define reverse_sub r1_binary64_reverse_subtract_bits
static uint32_t equal(uint64_t a,uint64_t b){
 register uint32_t r0 __asm__("r0")=(uint32_t)a,r1 __asm__("r1")=(uint32_t)(a>>32);
 register uint32_t r2 __asm__("r2")=(uint32_t)b,r3 __asm__("r3")=(uint32_t)(b>>32);uint32_t status;
 __asm__ volatile("bl r1_binary64_compare_reverse_flags\n\tmrs %[status],APSR":[status]"=r"(status),"+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3)::"lr","cc","memory");return(status>>30)&1u;
}
double r1_native_log(double input)
{
 uint64_t x=bits(input);uint32_t high=(uint32_t)(x>>32),absolute=high&0x7fffffffu;int32_t adjustment=0;
 if((int32_t)high>=(int32_t)word(0x39688)||absolute>word(0x39688)||(absolute==word(0x39688)&&(uint32_t)x))return r1_math_self_add64(input);
 if((int32_t)high<0x100000){
  if(!((uint32_t)x|absolute)){r1_native_errno_set(2);return value(bits(r1_math_divzero64())^UINT64_C(0x8000000000000000));}
  if((int32_t)high<0){r1_native_errno_set(1);return r1_math_invalid64();}
  adjustment=-54;x=mul(x,number(0x39690));high=(uint32_t)(x>>32);
 }
 int32_t k=adjustment+(int32_t)(high>>20)-1023;
 uint32_t mantissa=high&0xfffffu,normalization=(mantissa+word(0x39698))&0x100000u;
 high=mantissa|(normalization^0x3ff00000u);k+=(int32_t)(normalization>>20);
 x=(x&UINT64_C(0xffffffff))|((uint64_t)high<<32);
 uint64_t f=sub(x,number(0x396a0)),low_ln2=number(0x396a8),high_ln2=number(0x396b0);
 if(((mantissa+2)&0xfffffu)<3){
  if(equal(f,r1_log_zero[0])){
   if(k==0)return value(r1_log_zero[0]);
   uint64_t integer=r1_signed32_to_binary64_bits((uint32_t)k),low=mul(integer,low_ln2);
   return value(add(mul(integer,high_ln2),low));
  }
  uint64_t factor=reverse_sub(mul(f,number(0x396c0)),number(0x396c8));
  uint64_t remainder=mul(mul(f,f),factor);
  if(k==0)return value(sub(f,remainder));
  uint64_t integer=r1_signed32_to_binary64_bits((uint32_t)k);
  uint64_t correction=sub(reverse_sub(mul(integer,low_ln2),remainder),f);
  return value(sub(mul(integer,high_ln2),correction));
 }
 uint64_t ratio=divide(f,add(f,number(0x396d0)));
 uint64_t integer=r1_signed32_to_binary64_bits((uint32_t)k),square=mul(ratio,ratio),fourth=mul(square,square);
 uint32_t gate=(mantissa+word(0x396d8))|(0x6b851u-mantissa);
 uint64_t even=mul(bits(r1_native_polynomial(value(fourth),r1_log_even,3)),fourth);
 uint64_t odd=mul(bits(r1_native_polynomial(value(fourth),r1_log_odd,4)),square);
 uint64_t remainder=add(odd,even);
 if((int32_t)gate>0){
  uint64_t half_square=mul(mul(f,number(0x396c8)),f);
  if(k==0)return value(reverse_sub(reverse_sub(mul(add(half_square,remainder),ratio),half_square),f));
  uint64_t low=mul(integer,low_ln2);
  uint64_t correction=add(mul(add(half_square,remainder),ratio),low);
  correction=sub(reverse_sub(correction,half_square),f);
  return value(sub(mul(integer,high_ln2),correction));
 }
 if(k==0)return value(reverse_sub(mul(sub(f,remainder),ratio),f));
 uint64_t low=mul(integer,low_ln2);
 uint64_t correction=sub(sub(mul(sub(f,remainder),ratio),low),f);
 return value(sub(mul(integer,high_ln2),correction));
}
