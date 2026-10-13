#include <stdint.h>
extern void audio_uart_float_domain_error_439ca4(void);
static uint32_t remainder296_lsr(uint32_t value,uint32_t amount) {
 amount&=255u;return amount>=32u?0u:value>>amount;
}
/* Native577c4c..577d08: integer float-bit remainder, native exceptional policy. */
uint32_t audio_uart_float_remainder_bits_577c4c(uint32_t x,uint32_t y) {
 uint32_t sign=x&0x80000000u, twice_y=y<<1;
 int32_t ex=(int32_t)((x>>23)&255u),ey=(int32_t)(twice_y>>24);
 uint32_t mx,my;
 if(ey!=0 && ex!=255 && ey!=255) {
  if(twice_y>=(x<<1))return twice_y==(x<<1)?sign:x;
  my=(0x80000000u|(twice_y<<7))>>8;
  mx=0x80000000u|(x<<8);
 } else if(twice_y!=0u && ex!=255 && ey!=255) {
  if(twice_y>=(x<<1))return twice_y==(x<<1)?sign:x;
  my=twice_y<<8;
  uint32_t leading=(uint32_t)__builtin_clz(my);
  my<<=leading;ey=-(int32_t)leading;my>>=8;
  if(ex!=0)mx=0x80000000u|(x<<8);
  else {
   mx=x<<9;leading=(uint32_t)__builtin_clz(mx);
   mx<<=leading;ex=-(int32_t)leading;
  }
 } else {
  uint32_t result=x;
  uint32_t carry=((uint64_t)(x<<1)+0x1000000u)>>32;
  if(carry)result=0x7fffffffu;
  else {
   uint32_t sum=twice_y+0x1000000u;
   carry=((uint64_t)twice_y+0x1000000u)>>32;
   if(sum!=0u)result=0x7fffffffu;
  }
  if(!carry)audio_uart_float_domain_error_439ca4();
  return result;
 }
 int32_t difference=ex-ey-8;
 while(difference>0) {
  mx=(mx%my)<<8;
  if(mx==0u)return sign;
  difference-=8;
 }
 mx=remainder296_lsr(mx,(uint32_t)(-difference));
 mx%=my;
 if(mx==0u)return sign;
 uint32_t leading=(uint32_t)__builtin_clz(mx);
 mx<<=leading;int32_t exponent=ey+7-(int32_t)leading;
 if(exponent>=0)return (sign|(mx>>8))+((uint32_t)exponent<<23);
 return sign|remainder296_lsr(mx,(uint32_t)(8-exponent));
}
/* Native577c3c..577c4c: S0/S1 inputs toR0/R1 bit core, R0result backtoS0. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_remainder_577c3c(float x,float y) {
 union {float value;uint32_t bits;} a={.value=x},b={.value=y},result;
 result.bits=audio_uart_float_remainder_bits_577c4c(a.bits,b.bits);
 return result.value;
}
