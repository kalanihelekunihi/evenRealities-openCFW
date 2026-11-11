#include "native_float_to_signed.h"
#define FP __attribute__((noinline,noclone))
/* GCC9 strict IEEE evaluation makes 0/0 raise only IOC, as VCVT does for
 * NaN or overflow. A volatile result keeps this effect when logging is off. */
static FP float invalid(float numerator,float denominator){return numerator/denominator;}
uint32_t r1_native_float_to_signed32(float value)
{
 union {float value;uint32_t bits;} input={.value=value};
 uint32_t magnitude=input.bits&0x7fffffffu;
 if(magnitude>=0x4f000000u) {
  if(input.bits==0xcf000000u)return 0x80000000u;
  volatile float raised=invalid(0.0f,0.0f);(void)raised;
  if(magnitude>0x7f800000u)return 0;
  return input.bits>>31?0x80000000u:0x7fffffffu;
 }
 return (uint32_t)(int32_t)value;
}
