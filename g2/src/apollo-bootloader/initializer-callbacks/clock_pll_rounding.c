/* Independent IEEE-754 bit reconstruction; UNVALIDATED pending quiet release.
 * floor427c90/427ca0, round427d98/427da8, ceil427dd0/427de0.
 * No generic libm substitution or original opcode arrays. */
#include <stdint.h>
#define FP_ABI __attribute__((pcs("aapcs-vfp")))
float opencfw_boot_pll_floor(float) FP_ABI;
float opencfw_boot_pll_round(float) FP_ABI;
float opencfw_boot_pll_ceil(float) FP_ABI;
typedef union {float f;uint32_t bits;} binary32;
float opencfw_boot_pll_floor(float value){
 binary32 x={.f=value};int shift=(int)((x.bits>>23)&255)-126;
 if(shift<=0){
  if((x.bits<<1)!=0)x.bits=(x.bits>>31)?0xbf800000u:0;
 }else if(shift<24){
  uint32_t mask=0x00ffffffu>>shift;
  if(x.bits>>31)x.bits+=mask;
  x.bits&=~mask;
 }
 return x.f;
}
float opencfw_boot_pll_round(float value){
 binary32 x={.f=value};int shift=(int)((x.bits>>23)&255)-126;
 if(shift<=0){
  x.bits&=0x80000000u;
  if(shift==0)x.bits|=0x3f800000u;
 }else if(shift<24){
  uint32_t mask=0x00ffffffu>>shift;
  x.bits&=~(mask>>1);x.bits+=mask;x.bits&=~mask;
 }
 return x.f;
}
float opencfw_boot_pll_ceil(float value){
 binary32 x={.f=value};int shift=(int)((x.bits>>23)&255)-126;
 if(shift<=0){
  if((x.bits<<1)!=0)x.bits=(x.bits>>31)?0x80000000u:0x3f800000u;
 }else if(shift<24){
  uint32_t mask=0x00ffffffu>>shift;
  if(!(x.bits>>31))x.bits+=mask;
  x.bits&=~mask;
 }
 return x.f;
}
