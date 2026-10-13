#include <stdint.h>
static float trig298_float(uint32_t bits) {union {uint32_t bits;float value;} v={.bits=bits};return v.value;}
static uint32_t trig298_bits(float value) {union {uint32_t bits;float value;} v={.value=value};return v.bits;}
static float trig298_mul(float a,float b) {float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float trig298_add(float a,float b) {float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float trig298_mla(float a,float b,float c) {__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(a):"t"(b),"t"(c));return a;}
static float trig298_neg(float a) {float v;__asm__ volatile("vneg.f32 %0,%1":"=t"(v):"t"(a));return v;}
static uint32_t trig298_compare(float a,float b) {uint32_t flags;__asm__ volatile("vcmp.f32 %1,%2\n\tvmrs %0,fpscr":"=r"(flags):"t"(a),"t"(b));return flags;}
static uint32_t trig298_integer(float a) {float v;__asm__ volatile("vcvt.s32.f32 %0,%1":"=t"(v):"t"(a));return trig298_bits(v);}
static float trig298_fixed14(uint32_t bits) {float a=trig298_float(bits),v;__asm__ volatile("vcvt.f32.s32 %0,%1,#14":"=t"(v):"t"(a));return v;}
/* Native5094c0..50964c plusauthenticatedordinaryconstantpool50964c..50968c.
 * Named architectural float operations preserve native rounding/NaN/flags order. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_core_5094c0(uint32_t mode,float angle) {
 float scaled=trig298_mul(angle,trig298_float(0x3f22f983u));
 uint32_t scaled_bits=trig298_bits(scaled),quadrant;
 float absolute=trig298_float(scaled_bits&0x7fffffffu);
 if(trig298_compare(absolute,trig298_float(0x4f000000u))&0x80000000u) {
  float half=trig298_float((scaled_bits&0x80000000u)|0x3f000000u);
  scaled=trig298_add(half,scaled);quadrant=trig298_integer(scaled);
  if(quadrant!=0u) {
   float fixed=trig298_fixed14(quadrant);
   angle=trig298_mla(angle,fixed,trig298_float(0xc6c90000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xc0fda000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xbaa22000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xb3340000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xaec23000u));
  }
 } else {
  uint32_t bits=trig298_bits(angle);
  if(((bits>>23)&255u)==255u) {
   if((bits&0x7fffffu)!=0u)return angle;
   return trig298_float(0x7fffffffu);
  }
  if((bits<<1)==0u)return mode==0u?angle:trig298_float(0x3f800000u);
  scaled=trig298_add(trig298_float((scaled_bits&0x80000000u)|0x3f000000u),scaled);
  scaled_bits=trig298_bits(scaled);
  if((scaled_bits<<1)!=0u) {
   int32_t shift=150-(int32_t)((scaled_bits>>23)&255u);
   if(shift>=24)scaled_bits&=0x80000000u;
   else if(shift>0)scaled_bits=(scaled_bits>>(uint32_t)shift)<<(uint32_t)shift;
   scaled=trig298_float(scaled_bits);
  }
  if((trig298_bits(scaled)<<1)!=0u) {
   float fixed=trig298_mul(scaled,trig298_float(0x38800000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xc6c90000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xc0fda000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xbaa22000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xb3340000u));
   angle=trig298_mla(angle,fixed,trig298_float(0xaec23000u));
  }
  quadrant=trig298_integer(scaled);
 }
 mode+=(quadrant&3u);
 if(trig298_compare(trig298_float(trig298_bits(angle)&0x7fffffffu),trig298_float(0x39800000u))&0x80000000u) {
  if(mode&1u)angle=trig298_float(0x3f800000u);
 } else {
  float square=trig298_mul(angle,angle);
  if(mode&1u) {
   float v=trig298_mla(trig298_float(0x3d2aa036u),square,trig298_float(0xbab24993u));
   v=trig298_mla(trig298_float(0xbeffffdfu),v,square);
   angle=trig298_mla(trig298_float(0x3f800000u),v,square);
  } else {
   float v=trig298_mla(trig298_float(0x3c088342u),square,trig298_float(0xb94c8c6eu));
   float product=trig298_mul(angle,square);
   v=trig298_mla(trig298_float(0xbe2aaaa1u),v,square);
   angle=trig298_mla(angle,product,v);
  }
 }
 if(mode&2u)angle=trig298_neg(angle);
 return angle;
}
