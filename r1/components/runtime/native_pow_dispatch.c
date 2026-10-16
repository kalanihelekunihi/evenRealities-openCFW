#include <stdint.h>
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_native_fabs_core_bits(uint64_t);
extern uint64_t r1_native_sqrt_core_abi_bits(uint64_t);
extern uint64_t r1_signed32_to_binary64_bits(uint32_t);
extern uint32_t r1_native_errno_set(uint32_t);
extern double r1_math_add64(double,double);
extern double r1_math_invalid64(void);
extern double r1_math_divzero64(void);
extern double r1_math_high_square64(void);
/* Explicit unresolved source core: absolute base, exponent and sign are encoded. */
extern double r1_pow_reduced(uint64_t,uint64_t,uint64_t);
__attribute__((section(".r1.math.pow_dispatch_prefix"),used))
const uint32_t r1_pow_dispatch_prefix[12]={0x1fffff,0xfffff,0x0,0x3ff00000,0x3ff00000,0x7ff00000,0x43400000,0xfffffc01,0x0,0x7ff00000,0x0,0x0};
__attribute__((section(".r1.math.pow_dispatch_suffix"),used))
const uint32_t r1_pow_dispatch_suffix[7]={0x0,0x0,0x80000000,0x0,0xfff00000,0x0,0xbff00000};
__attribute__((section(".r1.math.pow_dispatch_zero"),used))
const uint64_t r1_pow_dispatch_zero[1]={UINT64_C(0x0)};
typedef union{uint64_t bits;double value;} encoded_double;
static double value(uint64_t bits){encoded_double x={.bits=bits};return x.value;}
static uint64_t bits(double value){encoded_double x={.value=value};return x.bits;}
static uint32_t word(unsigned address){return address<0x39e20 ? r1_pow_dispatch_prefix[(address-0x39df0)/4] : r1_pow_dispatch_suffix[(address-0x39e24)/4];}
static uint64_t number(unsigned address){return (uint64_t)word(address)|((uint64_t)word(address+4)<<32);}
static uint64_t copy_sign(uint64_t result,uint64_t input){return(result&UINT64_C(0x7fffffffffffffff))|(input&UINT64_C(0x8000000000000000));}
static double invalid(void){r1_native_errno_set(1);return r1_math_invalid64();}
double r1_native_pow(double base,double exponent)
{
 uint64_t x=bits(base),y=bits(exponent);uint32_t xl=(uint32_t)x,xh=(uint32_t)(x>>32),yl=(uint32_t)y,yh=(uint32_t)(y>>32),ax=xh&0x7fffffffu,ay=yh&0x7fffffffu;
 uint32_t bias=word(0x39df0);
 if(((xl!=0)+(xh<<1)+bias)<(bias>>1)||((yl!=0)+(yh<<1)+bias)<word(0x39df4))return r1_math_add64(base,exponent);
 uint64_t one=number(0x39df8);
 if(!(ay|yl))return value(one);
 if(xh==word(0x39e00)&&xl==0)return value(one);
 if(((xl!=0)+(xh<<1))>0xffe00000u || ((yl!=0)+(yh<<1))>0xffe00000u)return r1_math_add64(base,exponent);
 uint32_t parity=0;
 if((int32_t)xh<0 && ay<word(0x39e04)){
  if(ay>=word(0x39e08))parity=2;
  else if(ay>=word(0x39e00)){
   int32_t e=(int32_t)(ay>>20)+(int32_t)word(0x39e0c);
   if(e>20){uint32_t shift=52u-(uint32_t)e,part=yl>>shift;if((part<<shift)==yl)parity=2-(part&1);}
   else if(yl==0){uint32_t shift=20u-(uint32_t)e,part=ay>>shift;if((part<<shift)==ay)parity=2-(part&1);}
  }
 }
 if(!(ax|xl)&&(int32_t)yh<0){
  r1_native_errno_set(2);uint64_t result=bits(r1_math_divzero64());
  return value(xh!=0&&parity==1 ? result^UINT64_C(0x8000000000000000) : result);
 }
 uint64_t infinity=number(0x39e10),zero=number(0x39e18);
 if(yl==0){
  if(ay==word(0x39e04)){
   if(x==UINT64_C(0xbff0000000000000))return value(one);
   if(ax<word(0x39e00))return (int32_t)yh<0 ? value(y^UINT64_C(0x8000000000000000)) : value(r1_pow_dispatch_zero[0]);
   return (int32_t)yh>=0 ? exponent : value(r1_pow_dispatch_zero[0]);
  }
  if(ay==word(0x39e00)){
   if((int32_t)yh<0){
    if(ax==0){
     if(xl!=0){r1_native_errno_set(2);return value(copy_sign(bits(r1_math_high_square64()),x));}
     return value(copy_sign(infinity,x));
    }
    if(ax==word(0x39e04)){if(xl==0)return value(copy_sign(zero,x));}
    else if(ax<word(0x39e04))return value(r1_format_double_divide_bits(one,x));
   }
   return base;
  }
  if(ax<word(0x39e04)){
   if(yh==0x40000000u)return value(r1_format_double_multiply_bits(x,x));
   if(yh==0x3fe00000u&&(int32_t)xh>=0)return value(r1_native_sqrt_core_abi_bits(x));
  }
 }
 uint64_t absolute=r1_native_fabs_core_bits(x);
 if(xl==0){
  if(ax==0)return parity==1&&(int32_t)xh<0 ? value(number(0x39e28)) : value(zero);
  if(ax==word(0x39e04)){
   if((int32_t)xh>0)return (int32_t)yh>=0 ? value(infinity) : value(zero);
   if((int32_t)yh>=0)return parity==1 ? value(number(0x39e30)) : value(infinity);
   return parity==1 ? value(number(0x39e28)) : value(zero);
  }
  if(ax==word(0x39e00)){
   if((int32_t)xh<0&&parity==0)return invalid();
   return value(r1_signed32_to_binary64_bits(parity==2 ? 1u : 0xffffffffu));
  }
 }
 if((int32_t)xh<0&&parity==0)return invalid();
 uint64_t sign=(int32_t)xh<0&&parity==1 ? number(0x39e38) : one;
 return r1_pow_reduced(absolute,y,sign);
}
