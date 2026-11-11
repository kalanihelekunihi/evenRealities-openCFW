#ifndef R1_NATIVE_F32_INTEGER_H
#define R1_NATIVE_F32_INTEGER_H
#include <stdint.h>
/* VCVT with round-toward-zero, including invalid saturation and FP status. */
static inline uint32_t r1_native_f32_integer_bits(uint32_t value,uint32_t unsigned_result)
{
 uint32_t fp=__builtin_arm_get_fpscr(),magnitude=value&0x7fffffffu,exponent=magnitude>>23,fraction=magnitude&0x7fffffu,sign=value>>31,result=0,flags=0;
 if(exponent==255u){flags=1;if(!fraction)result=unsigned_result?(sign?0u:UINT32_MAX):(sign?0x80000000u:0x7fffffffu);}
 else if(!exponent){if(fraction)flags=(fp&(1u<<24))?128u:16u;}
 else if(exponent<127u)flags=16u;
 else if(unsigned_result&&sign)flags=1u;
 else if(unsigned_result&&exponent>158u){result=UINT32_MAX;flags=1u;}
 else if(!unsigned_result&&(exponent>158u||(exponent==158u&&(!sign||fraction)))){result=sign?0x80000000u:0x7fffffffu;flags=1u;}
 else{
  uint32_t significand=fraction|0x800000u;
  if(exponent<150u){uint32_t shift=150u-exponent;result=significand>>shift;if(significand&((1u<<shift)-1u))flags=16u;}
  else result=significand<<(exponent-150u);
  if(sign)result=0u-result;
 }
 __builtin_arm_set_fpscr(fp|flags);return result;
}
#endif
