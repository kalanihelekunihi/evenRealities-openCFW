#include <stdint.h>
extern void audio_uart_float_domain_error_439ca4(void);
static float inv300_float(uint32_t b){union{uint32_t b;float f;}v={.b=b};return v.f;}
static uint32_t inv300_bits(float f){union{uint32_t b;float f;}v={.f=f};return v.b;}
static float inv300_add(float a,float b){float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_sub(float a,float b){float v;__asm__ volatile("vsub.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_mul(float a,float b){float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_div(float a,float b){float v;__asm__ volatile("vdiv.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float inv300_mla(float a,float b,float c){__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(a):"t"(b),"t"(c));return a;}
static float inv300_neg(float a){float v;__asm__ volatile("vneg.f32 %0,%1":"=t"(v):"t"(a));return v;}
static float inv300_sqrt(float a){float v;__asm__ volatile("vsqrt.f32 %0,%1":"=t"(v):"t"(a));return v;}
static const uint32_t inv300_angles[8]={0x0u,0x3f060a92u,0x3fc90fdbu,0x3f860a92u,0x3fc90fdbu,0x40060a92u,0x40490fdbu,0x40278d36u};
/* Native55e99c..55ea06 plusordinarycoefficient/anglepool55ea08..55ea40.
 * Native callers' consumed mode domain0..15; larger table indices unqualified. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_core_55e99c(uint32_t mode,float x) {
 uint32_t bits=inv300_bits(x);
 if((int32_t)bits>=(int32_t)0x3e8930a4u) {
  float numerator=inv300_mla(inv300_float(0xbf800000u),inv300_float(0x3fddb3d7u),x);
  float denominator=inv300_add(inv300_float(0x3fddb3d7u),x);
  x=inv300_div(numerator,denominator);mode|=2u;bits=inv300_bits(x);
 }
 if((bits<<1)>=0x73000000u) {
  float square=inv300_mul(x,x);
  float cube=inv300_mul(x,square);
  x=inv300_mla(x,cube,inv300_float(0x3f03d56au));
  float denominator=inv300_mla(inv300_float(0x3f592ab8u),inv300_float(0x3da9942bu),square);
  denominator=inv300_mla(inv300_float(0x3f800000u),denominator,square);
  x=inv300_div(x,denominator);
 }
 uint32_t index=mode>>1;
 if(index&2u)x=inv300_neg(x);
 x=inv300_add(x,inv300_float(inv300_angles[index]));
 if(mode&1u)x=inv300_neg(x);
 return x;
}
/* Native58ec74..58ecb8 withliteral58ecb8: unary inverse-ratio entry. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_ratio_58ec74(float x) {
 uint32_t bits=inv300_bits(x),exponent=(bits>>23)&255u;
 if(exponent==0u)return x;
 if(exponent>=153u) {
  if(exponent==255u && (bits&0x7fffffu)!=0u)return x;
  return inv300_float(0x3fc90fdbu|(bits&0x80000000u));
 }
 uint32_t mode=bits>>31;bits&=0x7fffffffu;x=inv300_float(bits);
 if(bits>0x3f800000u){x=inv300_div(inv300_float(0x3f800000u),x);mode+=4u;}
 return audio_uart_float_inverse_core_55e99c(mode,x);
}
/* Native58ecbc..58ed1a withliteral58ed1c: unary inverse-magnitude entry. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_magnitude_58ecbc(float x) {
 uint32_t original=inv300_bits(x),mode=((original>>31)!=0u && (original<<1)!=0u)?8u:4u;
 uint32_t bits=original&0x7fffffffu;x=inv300_float(bits);
 if(bits>0x3f800000u) {
  if(bits<=0x7f800000u){audio_uart_float_domain_error_439ca4();return inv300_float(0x7fffffffu);}
  return x;
 }
 float one=inv300_float(0x3f800000u);
 float difference=inv300_sub(one,x);
 float sum=inv300_add(one,x);
 float root=inv300_sqrt(inv300_mul(sum,difference));
 if(bits>0x3f3504f4u){mode^=4u;x=inv300_div(root,x);}
 else x=inv300_div(x,root);
 return audio_uart_float_inverse_core_55e99c(mode,x);
}
