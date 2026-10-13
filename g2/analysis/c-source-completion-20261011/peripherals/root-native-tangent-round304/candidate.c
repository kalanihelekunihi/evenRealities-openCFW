#include <stdint.h>
static float tan304_float(uint32_t bits) {union {uint32_t bits;float value;} v={.bits=bits};return v.value;}
static uint32_t tan304_bits(float value) {union {uint32_t bits;float value;} v={.value=value};return v.bits;}
static float tan304_mul(float a,float b) {float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float tan304_add(float a,float b) {float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float tan304_mla(float a,float b,float c) {__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(a):"t"(b),"t"(c));return a;}
static float tan304_neg(float a) {float v;__asm__ volatile("vneg.f32 %0,%1":"=t"(v):"t"(a));return v;}
static uint32_t tan304_compare(float a,float b) {uint32_t flags;__asm__ volatile("vcmp.f32 %1,%2\n\tvmrs %0,fpscr":"=r"(flags):"t"(a),"t"(b));return flags;}
static uint32_t tan304_integer(float a) {float v;__asm__ volatile("vcvt.s32.f32 %0,%1":"=t"(v):"t"(a));return tan304_bits(v);}
static float tan304_fixed14(uint32_t bits) {float a=tan304_float(bits),v;__asm__ volatile("vcvt.f32.s32 %0,%1,#14":"=t"(v):"t"(a));return v;}
static float tan304_div(float a,float b){float v;__asm__ volatile("vdiv.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
/* Native563f40..5640ae plusordinaryliteralpool5640b0..5640e4. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_tangent_563f40(float angle) {
 float scaled=tan304_mul(angle,tan304_float(0x3f22f983u));
 uint32_t scaled_bits=tan304_bits(scaled),quadrant;
 float absolute=tan304_float(scaled_bits&0x7fffffffu);
 if(tan304_compare(absolute,tan304_float(0x4f000000u))&0x80000000u) {
  float half=tan304_float((scaled_bits&0x80000000u)|0x3f000000u);
  scaled=tan304_add(half,scaled);quadrant=tan304_integer(scaled);
  if(quadrant!=0u) {
   float fixed=tan304_fixed14(quadrant);
   angle=tan304_mla(angle,fixed,tan304_float(0xc6c90000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xc0fda000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xbaa22000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xb3340000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xaec23000u));
  }
 } else {
  uint32_t bits=tan304_bits(angle);
  if(((bits>>23)&255u)==255u) {
   if((bits&0x7fffffu)!=0u)return angle;
   return tan304_float(0x7fffffffu);
  }
  if((bits<<1)==0u)return angle;
  scaled=tan304_add(tan304_float((scaled_bits&0x80000000u)|0x3f000000u),scaled);
  scaled_bits=tan304_bits(scaled);
  if((scaled_bits<<1)!=0u) {
   int32_t shift=150-(int32_t)((scaled_bits>>23)&255u);
   if(shift>=24)scaled_bits&=0x80000000u;
   else if(shift>0)scaled_bits=(scaled_bits>>(uint32_t)shift)<<(uint32_t)shift;
   scaled=tan304_float(scaled_bits);
  }
  if((tan304_bits(scaled)<<1)!=0u) {
   float fixed=tan304_mul(scaled,tan304_float(0x38800000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xc6c90000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xc0fda000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xbaa22000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xb3340000u));
   angle=tan304_mla(angle,fixed,tan304_float(0xaec23000u));
  }
  quadrant=tan304_integer(scaled);
 }
 if(tan304_compare(tan304_float(tan304_bits(angle)&0x7fffffffu),tan304_float(0x39800000u))&0x80000000u) {
  if(quadrant&1u)return tan304_div(tan304_float(0xbf800000u),angle);
  return angle;
 }
 float square=tan304_mul(angle,angle);
 float denominator=tan304_mla(tan304_float(0xbedbb51eu),square,tan304_float(0x3c1f166du));
 denominator=tan304_mla(tan304_float(0x3f800000u),denominator,square);
 float product=tan304_mul(angle,square);
 float numerator=tan304_mla(angle,product,tan304_float(0xbdc42983u));
 if(quadrant&1u)return tan304_neg(tan304_div(denominator,numerator));
 return tan304_div(numerator,denominator);
}
