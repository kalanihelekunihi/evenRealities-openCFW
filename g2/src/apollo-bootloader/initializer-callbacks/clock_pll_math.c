/* Independent stock reconstruction, f89a4c46, NOT YET VALIDATED.
 * GCD426d48, integer426db4, fraction426eac, VCO426f6c.
 * Original floor/fmod/round/ceil bodies remain explicit dependencies.
 * Build with -ffp-contract=off; stock VMLS is explicitly retained below. */
#include "clock_generators.h"
#include <stddef.h>
#define FP_ABI __attribute__((pcs("aapcs-vfp")))
extern float opencfw_boot_pll_floor(float) FP_ABI;
extern float opencfw_boot_pll_mod(float,float) FP_ABI;
extern float opencfw_boot_pll_round(float) FP_ABI;
extern float opencfw_boot_pll_ceil(float) FP_ABI;
float opencfw_boot_pll_gcd(float,float) FP_ABI;
uint32_t opencfw_boot_pll_integer(float,float,uint8_t *,uint16_t *) FP_ABI;
uint32_t opencfw_boot_pll_fraction(float,float,uint8_t *,uint16_t *,uint32_t *) FP_ABI;
uint32_t opencfw_boot_pll_vco_generate(opencfw_pll_config *,float,float) FP_ABI;
static uint32_t unsigned_fp(float f){
 uint32_t out;__asm__("vcvt.u32.f32 %1,%1\nvmov %0,%1":"=r"(out),"+t"(f));return out;
}
static uint32_t unsigned_div(uint32_t n,uint32_t d){
 uint32_t out;__asm__("udiv %0,%1,%2":"=r"(out):"r"(n),"r"(d));return out;
}
float opencfw_boot_pll_gcd(float first,float second){
 if(first<second){float tmp=first;first=second;second=tmp;}
 for(unsigned i=0;i<16;i++){
  if(second<0x1p-23f)return first;
  float quotient=opencfw_boot_pll_floor(first/second);
  __asm__("vmls.f32 %0,%1,%2":"+t"(first):"t"(quotient),"t"(second));
  float tmp=first;first=second;second=tmp;
 }
 return -1.0f;
}
uint32_t opencfw_boot_pll_integer(float reference,float target,uint8_t *refdiv,uint16_t *feedback){
 float gcd=opencfw_boot_pll_gcd(target,reference);
 if(gcd<0x1p-23f)return 0;
 float multiplier=target/gcd,divider=reference/gcd;
 if(opencfw_boot_pll_mod(multiplier,1.0f)>0x1p-23f ||
    opencfw_boot_pll_round(multiplier)>960.0f)return 0;
 uint32_t m=unsigned_fp(opencfw_boot_pll_round(multiplier));
 if(opencfw_boot_pll_mod(divider,1.0f)>0x1p-23f ||
    opencfw_boot_pll_round(divider)>63.0f)return 0;
 uint32_t d=unsigned_fp(opencfw_boot_pll_round(divider));
 if(m<4){uint32_t factor=unsigned_div(m+3,m);d*=factor;m*=factor;}
 if(!d||d>=64)return 0;
 if(m-4>=957)return 0;
 *refdiv=d&63;*feedback=m&4095;return 1;
}
uint32_t opencfw_boot_pll_fraction(float reference,float target,uint8_t *refdiv,
 uint16_t *feedback,uint32_t *fraction){
 float ratio=target/reference;
 float d=opencfw_boot_pll_ceil(10.0f/ratio);
 if(d<0x1p-23f||d>63.0f)return 0;
 uint32_t divider=unsigned_fp(d);
 float multiplier=ratio*(float)divider;
 uint32_t frac=unsigned_fp(opencfw_boot_pll_round(
                           opencfw_boot_pll_mod(multiplier,1.0f)*16777216.0f));
 float integer=opencfw_boot_pll_floor(multiplier);
 if(integer<10.0f||integer>96.0f)return 0;
 uint32_t whole=unsigned_fp(opencfw_boot_pll_floor(integer));
 *refdiv=(uint8_t)divider;*feedback=(uint16_t)whole;*fraction=frac;return 1;
}
uint32_t opencfw_boot_pll_vco_generate(opencfw_pll_config *out,float reference,float target){
 uint8_t divider=0;uint16_t feedback=0;uint32_t fraction=0;
 if(!out)return 6;
 if(target<60.0f||target>960.0f)return 5;
 uint32_t integer=opencfw_boot_pll_integer(reference,target,&divider,&feedback);
 uint32_t success=integer;
 if(!integer)success=opencfw_boot_pll_fraction(reference,target,&divider,&feedback,&fraction);
 if(!success)return 1;
 out->vco=target>=240.0f?1:0;out->fraction_mode=integer?1:0;
 out->reference_divider=divider;out->feedback_integer=feedback;
 out->feedback_fraction=fraction;return 0;
}
