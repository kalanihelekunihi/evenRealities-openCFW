/* Independent reconstruction of locked f89a4c46 bootloader:
 * HF2 426c24, PLL minimum-VCO 427040, PLL selection 427160.
 * Not integrated/validated yet. Remaining FP helpers are explicit dependencies.
 * Public Ambiq SDK is corroborating evidence, not copied implementation. */
#include "clock_generators.h"
#include <stddef.h>
extern float opencfw_boot_pll_gcd(float,float) __attribute__((pcs("aapcs-vfp")));
extern uint32_t opencfw_boot_pll_vco_generate(opencfw_pll_config *,float,float)
 __attribute__((pcs("aapcs-vfp")));
static uint32_t divide(uint32_t a,uint32_t b){
 uint32_t out;__asm__("udiv %0,%1,%2":"=r"(out):"r"(a),"r"(b));return out;
}
uint32_t opencfw_boot_startup_hf2_generate(uint32_t reference,uint32_t target,
 uint32_t shift,uint32_t *out){
 uint32_t divisor,value;
 /* Keep architectural register-shift, UDIV and fixed-point VCVT semantics,
  * including shift>=32 and invalid/saturating FP conversion. No C cast UB. */
 __asm__ volatile(
  "movs %0,#1\nlsls.w %0,%0,%3\nudiv %1,%2,%0\n"
  "vmov s0,%4\nvcvt.f32.u32 s0,s0\n"
  "vmov s1,%1\nvcvt.f32.u32 s1,s1\nvdiv.f32 s0,s0,s1\n"
  "vcvt.u32.f32 s0,s0,#15\nvmov %1,s0"
  :"=&r"(divisor),"=&r"(value):"r"(reference),"r"(shift),"r"(target)
  :"s0","s1","cc");
 *out=value;return 0;
}
uint32_t opencfw_boot_pll_min_generate(opencfw_pll_config *out,
 uint32_t reference,uint32_t target,uint32_t minimum){
 static const uint8_t post[50]={0x00,0x11,0x21,0x31,0x41,0x51,0x61,0x71,
  0x42,0x33,0x52,0x62,0x62,0x72,0x72,0x53,0x44,0x63,0x63,0x54,
  0x54,0x73,0x64,0x64,0x64,0x55,0x74,0x74,0x74,0x65,0x65,0x75,
  0x75,0x75,0x75,0x75,0x66,0x76,0x76,0x76,0x76,0x76,0x76,0x77,
  0x77,0x77,0x77,0x77,0x77,0x77};
 uint32_t div;uint8_t p1,p2;
 if(opencfw_boot_pll_gcd((float)target/1000000.0f,
                       (float)reference/1000000.0f)<1.0f){
  uint32_t limit=divide(reference,divide(reference,10000000))*10u;
  if(minimum<limit)minimum=limit;
 }
 if(target>=minimum){div=1;p1=1;p2=1;}
 else{
  div=divide(minimum,target);
  if(minimum-target*div)++div;
  if(div>=50)return 5;
  p1=post[div]>>4;p2=post[div]&15;div=p1*p2;
 }
 uint32_t status=opencfw_boot_pll_vco_generate(out,(float)reference/1000000.0f,
                                             (float)(target*div)/1000000.0f);
 if(status)return status;
 uint32_t pfd=divide(reference,out->reference_divider);
 if(reference-pfd*out->reference_divider)++pfd;
 if(pfd<(out->fraction_mode==0?10000000u:1000000u))return 5;
 out->post1=p1;out->post2=p2;return 0;
}
static uint32_t score(const opencfw_pll_config *c,uint32_t reference,uint32_t target){
 static const uint32_t a[4]={435700,465700,131525,139025};
 static const uint32_t b[4]={228000,396000,228000,396000};
 unsigned i=(c->fraction_mode==0)+(c->vco==1?2:0);
 return divide((reference/1000000u)*b[i],c->reference_divider)
       +((target*c->post1*c->post2)/1000000u)*a[i];
}
uint32_t opencfw_boot_startup_pll_generate(uint8_t *destination,
 uint32_t reference,uint32_t target){
 opencfw_pll_config low,high;const opencfw_pll_config *chosen=NULL;
 uint32_t lo=opencfw_boot_pll_min_generate(&low,reference,target,60000000);
 uint32_t hi=opencfw_boot_pll_min_generate(&high,reference,target,240000000);
 if(!lo&&!hi)chosen=score(&low,reference,target)<score(&high,reference,target)?&low:&high;
 else if(!hi)chosen=&high;else if(!lo)chosen=&low;
 if(!chosen)return 5;
 /* Caller owns reference selection; offset0 is deliberately retained. */
 const uint8_t *bytes=(const uint8_t *)chosen;
 for(unsigned i=1;i<12;i++)destination[i]=bytes[i];
 return 0;
}
