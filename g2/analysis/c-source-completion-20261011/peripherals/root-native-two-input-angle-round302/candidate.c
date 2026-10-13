#include <stdint.h>
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_core_55e99c(uint32_t,float);
extern void audio_uart_float_domain_error_439ca4(void);
static float angle302_float(uint32_t b){union{uint32_t b;float f;}v={.b=b};return v.f;}
static uint32_t angle302_bits(float f){union{uint32_t b;float f;}v={.f=f};return v.b;}
static float angle302_abs(float a){float v;__asm__ volatile("vabs.f32 %0,%1":"=t"(v):"t"(a));return v;}
static float angle302_add(float a,float b){float v;__asm__ volatile("vadd.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_sub(float a,float b){float v;__asm__ volatile("vsub.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_mul(float a,float b){float v;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_div(float a,float b){float v;__asm__ volatile("vdiv.f32 %0,%1,%2":"=t"(v):"t"(a),"t"(b));return v;}
static float angle302_sqrt(float a){float v;__asm__ volatile("vsqrt.f32 %0,%1":"=t"(v):"t"(a));return v;}
/* Native50969c..509706: mode/sign gates before magnitude ratio andspecialvalues. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_two_input_angle_50969c(float y,float x) {
 uint32_t original_y=angle302_bits(y),original_x=angle302_bits(x);
 y=angle302_abs(y);
 uint32_t mode=original_y>>31;
 uint32_t twice_y=original_y<<1,twice_x=original_x<<1;
 x=angle302_abs(x);
 if(original_x>>31)mode+=12u;
 uint32_t abs_y=original_y&0x7fffffffu,abs_x=original_x&0x7fffffffu;
 if(abs_y<0x7f800000u && abs_x<0x7f800000u) {
  uint32_t reciprocal=twice_x<twice_y;
  if(reciprocal)mode^=4u;
  if(twice_x==0u)return audio_uart_float_inverse_core_55e99c(mode,angle302_float(0u));
  float ratio=reciprocal?angle302_div(x,y):angle302_div(y,x);
  return audio_uart_float_inverse_core_55e99c(mode,ratio);
 }
 if(abs_y==0x7f800000u)mode^=4u;
 if(abs_y>0x7f800000u || abs_x>0x7f800000u)return angle302_float(0x7fffffffu);
 return audio_uart_float_inverse_core_55e99c(mode,angle302_float(twice_x==twice_y?0x3f800000u:0u));
}
/* Native509708..509760 withordinarythreshold509760: signedunaryentry. */
__attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_signed_509708(float x) {
 uint32_t original=angle302_bits(x),mode=original>>31,bits=original&0x7fffffffu;
 if(bits==0u)return x;
 x=angle302_float(bits);
 if(bits>0x3f800000u) {
  if(bits<=0x7f800000u){audio_uart_float_domain_error_439ca4();return angle302_float(0x7fffffffu);}
  return x;
 }
 float one=angle302_float(0x3f800000u);
 float difference=angle302_sub(one,x),sum=angle302_add(one,x);
 float root=angle302_sqrt(angle302_mul(sum,difference));
 if(bits>0x3f3504f4u){mode^=4u;x=angle302_div(root,x);}
 else x=angle302_div(x,root);
 return audio_uart_float_inverse_core_55e99c(mode,x);
}
