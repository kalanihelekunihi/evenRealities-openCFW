#include <stdint.h>
#include "native_float_bits.h"
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_native_errno_set(uint32_t);
extern double r1_math_high_square64(void);
extern double r1_math_low_square64(void);
extern double r1_native_polynomial(double,const uint64_t *,uint32_t);
extern const uint64_t r1_pow_dispatch_zero[1];
__attribute__((section(".r1.math.pow_near"),used))
const uint32_t r1_pow_near[10]={0x41e00000,0x43f00000,0x3fefffff,0x0,0x0,0x3fd00000,0x55555555,0x3fd55555,0x0,0x3fe00000};
__attribute__((section(".r1.math.pow_normal"),used))
const uint32_t r1_pow_normal[10]={0x60000000,0x3ff71547,0x652b82fe,0x3ff71547,0xf85ddf44,0x3e54ae0b,0x0,0x43400000,0x3988e,0xbb67a};
__attribute__((section(".r1.math.pow_log"),used))
const uint32_t r1_pow_log[9]={0x0,0x0,0x40080000,0xe0000000,0x3feec709,0xdc3a03fd,0x3feec709,0x145b01f5,0xbe3e2fe0};
__attribute__((section(".r1.math.pow_limits"),used))
const uint32_t r1_pow_limits[8]={0x40900000,0x0,0x652b82fe,0x3c971547,0x4090cc00,0x3f6f3400,0xfffffc01,0x3fe00000};
__attribute__((section(".r1.math.pow_scaling"),used))
const uint32_t r1_pow_scaling[7]={0xfffff,0x0,0x3fe62e43,0xca86c39,0xbe205c61,0xfefa39ef,0x3fe62e42};
__attribute__((section(".r1.math.pow_tail"),used))
const uint32_t r1_pow_tail[3]={0x0,0x0,0x40000000};
__attribute__((section(".r1.math.pow_base"),used))
const uint64_t r1_pow_base[2]={UINT64_C(0x3ff0000000000000),UINT64_C(0x3ff8000000000000)};
__attribute__((section(".r1.math.pow_log_high"),used))
const uint64_t r1_pow_log_high[2]={UINT64_C(0x0),UINT64_C(0x3fe2b80340000000)};
__attribute__((section(".r1.math.pow_log_low"),used))
const uint64_t r1_pow_log_low[2]={UINT64_C(0x0),UINT64_C(0x3e4cfdeb43cfd006)};
__attribute__((section(".r1.math.pow_log_poly"),used))
const uint64_t r1_pow_log_poly[6]={UINT64_C(0x3fe3333333333303),UINT64_C(0x3fdb6db6db6fabff),UINT64_C(0x3fd55555518f264d),UINT64_C(0x3fd17460a91d4101),UINT64_C(0x3fcd864a93c9db65),UINT64_C(0x3fca7e284a454eef)};
__attribute__((section(".r1.math.pow_exp_poly"),used))
const uint64_t r1_pow_exp_poly[5]={UINT64_C(0x3fc555555555553e),UINT64_C(0xbf66c16c16bebd93),UINT64_C(0x3f11566aaf25de2c),UINT64_C(0xbebbbd41c5d26bf1),UINT64_C(0x3e66376972bea4d0)};
typedef union{uint64_t bits;double value;} encoded_double;
static double value(uint64_t bits){encoded_double x={.bits=bits};return x.value;}
static uint64_t bits(double value){encoded_double x={.value=value};return x.bits;}
static uint32_t word(unsigned a){
 if(a<0x3a288)return r1_pow_near[(a-0x39e40)/4];
 if(a<0x3a2b0)return r1_pow_normal[(a-0x3a288)/4];
 if(a<0x3a2e0)return r1_pow_log[(a-0x3a2bc)/4];
 if(a<0x3a5f0)return r1_pow_limits[(a-0x3a5d0)/4];
 if(a<0x3a610)return r1_pow_scaling[(a-0x3a5f4)/4];
 return r1_pow_tail[(a-0x3a614)/4];
}
static uint64_t number(unsigned a){return(uint64_t)word(a)|((uint64_t)word(a+4)<<32);}
#define add r1_format_double_add_bits
#define mul r1_format_double_multiply_bits
#define divide r1_format_double_divide_bits
#define sub r1_binary64_subtract_bits
#define reverse_sub r1_binary64_reverse_subtract_bits
static uint64_t truncated(uint64_t x){return(x&UINT64_C(0xffffffff00000000))|(uint32_t)r1_pow_dispatch_zero[0];}
static uint32_t right(uint32_t x,uint32_t n){n&=255u;return n<32 ? x>>n : 0;}
static uint32_t compare_status(uint64_t a,uint64_t b){
 register uint32_t r0 __asm__("r0")=(uint32_t)a,r1 __asm__("r1")=(uint32_t)(a>>32);
 register uint32_t r2 __asm__("r2")=(uint32_t)b,r3 __asm__("r3")=(uint32_t)(b>>32);uint32_t status;
 __asm__ volatile("bl r1_binary64_compare_flags\n\tmrs %[status],APSR":[status]"=r"(status),"+r"(r0),"+r"(r1),"+r"(r2),"+r"(r3)::"lr","cc","memory");return status;
}
static double range_error(uint64_t sign,uint32_t overflow){r1_native_errno_set(2);uint64_t result=bits(overflow ? r1_math_high_square64() : r1_math_low_square64());return value((result&UINT64_C(0x7fffffffffffffff))|(sign&UINT64_C(0x8000000000000000)));}
/* Raw encoded arguments are the internal source ABI, not the original
 * interior register/stack ABI. Operations preserve native software ordering. */
double r1_pow_reduced(uint64_t absolute,uint64_t exponent,uint64_t sign)
{
 const uint64_t one=UINT64_C(0x3ff0000000000000);
 uint32_t ax=(uint32_t)(absolute>>32),yh=(uint32_t)(exponent>>32),ay=yh&0x7fffffffu;
 uint64_t log_high,log_low;
 if(ay>word(0x39e40)){
  if(ay>word(0x39e44)){
   if(ax<=word(0x39e48))return range_error(sign,yh>>31);
   if(ax>=0x3ff00000u)return range_error(sign,!(yh>>31));
  }
  if(ax<word(0x39e48))return range_error(sign,yh>>31);
  if(ax>0x3ff00000u)return range_error(sign,!(yh>>31));
  uint64_t t=sub(absolute,one);
  uint64_t q=reverse_sub(mul(t,number(0x39e50)),number(0x39e58));
  q=reverse_sub(mul(q,t),number(0x39e60));q=mul(mul(t,t),q);
  uint64_t high=mul(t,number(0x3a288));q=mul(q,number(0x3a290));uint64_t low=sub(mul(t,number(0x3a298)),q);
  log_high=truncated(add(high,low));log_low=reverse_sub(sub(log_high,high),low);
 }else{
  int32_t adjustment=0;
  if(ax<0x100000u){absolute=mul(absolute,number(0x3a2a0));adjustment=-53;ax=(uint32_t)(absolute>>32);}
  int32_t k=adjustment+(int32_t)(ax>>20)-1023;uint32_t mantissa=ax&0xfffffu,bucket;
  ax=mantissa|0x3ff00000u;
  if(mantissa<=word(0x3a2a8))bucket=0;
  else if(mantissa<word(0x3a2ac))bucket=1;
  else{bucket=0;ax-=0x100000u;++k;}
  absolute=(absolute&UINT64_C(0xffffffff))|((uint64_t)ax<<32);
  uint64_t base=r1_pow_base[bucket],numerator=sub(absolute,base),reciprocal=divide(one,add(absolute,base));
  uint64_t ratio=mul(numerator,reciprocal),ratio_high=truncated(ratio);
  uint32_t high_word=(ax>>1)|0x20000000u;high_word+=(bucket<<18)+0x80000u;
  uint64_t denominator_high=((uint64_t)high_word<<32)|(uint32_t)r1_pow_dispatch_zero[0];
  uint64_t denominator_low=reverse_sub(sub(denominator_high,base),absolute);
  uint64_t low_product=mul(ratio_high,denominator_low),high_product=mul(ratio_high,denominator_high);
  uint64_t ratio_low=mul(sub(reverse_sub(high_product,numerator),low_product),reciprocal);
  uint64_t square=mul(ratio,ratio);
  uint64_t remainder=mul(mul(square,square),bits(r1_native_polynomial(value(square),r1_pow_log_poly,6)));
  remainder=add(mul(add(ratio_high,ratio),ratio_low),remainder);
  uint64_t high_square=mul(ratio_high,ratio_high),three=number(0x3a2c0);
  uint64_t t=truncated(add(add(high_square,three),remainder));
  uint64_t t_low=reverse_sub(sub(sub(t,three),high_square),remainder);
  uint64_t u=mul(ratio_high,t),v=add(mul(ratio_low,t),mul(t_low,ratio));
  uint64_t product_high=truncated(add(u,v)),product_low=reverse_sub(sub(product_high,u),v);
  uint64_t high=mul(product_high,number(0x3a2c8));
  uint64_t low=mul(product_low,number(0x3a2d0));low=add(mul(product_high,number(0x3a2d8)),low);low=add(low,r1_pow_log_low[bucket]);
  uint64_t integer=r1_signed32_to_binary64_bits((uint32_t)k);
  log_high=truncated(add(add(add(high,low),r1_pow_log_high[bucket]),integer));
  log_low=reverse_sub(sub(sub(sub(log_high,integer),r1_pow_log_high[bucket]),high),low);
 }
 uint64_t exponent_high=truncated(exponent);
 uint64_t product_low=add(mul(exponent,log_low),mul(sub(exponent,exponent_high),log_high));
 uint64_t product_high=mul(exponent_high,log_high),total=add(product_low,product_high);
 uint32_t high=(uint32_t)(total>>32),low=(uint32_t)total;
 if((int32_t)high>=(int32_t)word(0x3a5d0)){
  if(low || high!=word(0x3a5d0))return range_error(sign,1);
  uint64_t residual=sub(total,product_high);uint32_t flags=compare_status(add(product_low,number(0x3a5d8)),residual);
  if(!(flags&0x20000000u))return range_error(sign,1);
 }else if((high&0x7fffffffu)>=word(0x3a5e0)){
  if(low || high+word(0x3a5e4))return range_error(sign,0);
  uint32_t flags=compare_status(sub(total,product_high),product_low);
  if(!(flags&0x20000000u)||(flags&0x40000000u))return range_error(sign,0);
 }
 int32_t scale=0;uint32_t magnitude=high&0x7fffffffu;
 if(magnitude>word(0x3a5ec)){
  uint32_t e=(magnitude>>20)+word(0x3a5e8),adjusted=high+right(0x100000u,e+1);
  uint32_t n=((adjusted>>20)&2047u)-1023u;
  uint32_t rounded_integer=right((adjusted&0xfffffu)|0x100000u,20u-n);
  scale=(int32_t)high<0 ? -(int32_t)rounded_integer : (int32_t)rounded_integer;
  uint32_t cleared=adjusted&~right(word(0x3a5f4),n);
  uint64_t integer=((uint64_t)cleared<<32)|(uint32_t)r1_pow_dispatch_zero[0];product_high=sub(product_high,integer);
 }
 uint64_t u=truncated(add(product_low,product_high));
 uint64_t high_ln2=mul(u,number(0x3a5f8));
 uint64_t low_ln2=mul(u,number(0x3a600));
 uint64_t correction=reverse_sub(sub(u,product_high),product_low);correction=mul(correction,number(0x3a608));correction=add(correction,low_ln2);
 uint64_t z=add(high_ln2,correction),w=reverse_sub(sub(z,high_ln2),correction),square=mul(z,z);
 uint64_t c=reverse_sub(mul(bits(r1_native_polynomial(value(square),r1_pow_exp_poly,5)),square),z);
 uint64_t error=add(mul(z,w),w),quotient=divide(mul(z,c),sub(c,number(0x3a618)));
 uint64_t result=reverse_sub(sub(sub(quotient,error),z),one);
 uint32_t scaled_high=(uint32_t)(result>>32)+((uint32_t)scale<<20);
 if(((int32_t)scaled_high>>20)>0)result=(result&UINT64_C(0xffffffff))|((uint64_t)scaled_high<<32);
 else{
  uint64_t probe=r1_binary64_scale_power2_bits(result,(uint32_t)scale);
  if(r1_binary64_classify_bits(probe,0,0)==4)(void)r1_math_low_square64();
  result=r1_binary64_scale_power2_bits(result,(uint32_t)scale);
 }
 return value(mul(sign,result));
}
