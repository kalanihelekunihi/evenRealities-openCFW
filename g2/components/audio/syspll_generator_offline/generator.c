#include "generator.h"
/* Original firmware math-library providers execute; these are not stubs. */
extern float stock_floorf(float),stock_roundf(float),stock_ceilf(float);
extern float stock_fmodf(float,float);
/* Explicit named VFP operations retain rounding, exception flags and quiet
 * VCMP unordered predicates. C comparisons can emit signaling VCMPE instead.
 * These are compiler-assembled instructions, not retained firmware bytes. */
static uint32_t compare(float a,float b){uint32_t f;__asm__ volatile("vcmp.f32 %1,%2\n\tvmrs %0,fpscr":"=r"(f):"t"(a),"t"(b));return f;}
static uint32_t negative(uint32_t f){return f>>31;}
static uint32_t less(uint32_t f){return ((f>>31)^(f>>28))&1;}
static uint32_t uint_from_float(float x){float y;uint32_t v;__asm__ volatile("vcvt.u32.f32 %0,%2\n\tvmov %1,%0":"=&t"(y),"=r"(v):"t"(x));return v;}
static float float_from_uint(uint32_t x){float y;__asm__ volatile("vmov %0,%1\n\tvcvt.f32.u32 %0,%0":"=&t"(y):"r"(x));return y;}
static float divide(float a,float b){float y;__asm__ volatile("vdiv.f32 %0,%1,%2":"=t"(y):"t"(a),"t"(b));return y;}
static float multiply(float a,float b){float y;__asm__ volatile("vmul.f32 %0,%1,%2":"=t"(y):"t"(a),"t"(b));return y;}
static float subtract_product(float a,float b,float c){__asm__ volatile("vmls.f32 %0,%1,%2":"+t"(a):"t"(b),"t"(c));return a;}
static uint32_t udivide(uint32_t a,uint32_t b){return b?a/b:0;}
static const uint8_t postdiv_table[50]={0x00,0x11,0x21,0x31,0x41,0x51,0x61,0x71,0x42,0x33,0x52,0x62,0x62,0x72,0x72,0x53,0x44,0x63,0x63,0x54,0x54,0x73,0x64,0x64,0x64,0x55,0x74,0x74,0x74,0x65,0x65,0x75,0x75,0x75,0x75,0x75,0x66,0x76,0x76,0x76,0x76,0x76,0x76,0x77,0x77,0x77,0x77,0x77,0x77,0x77};
static const uint32_t points_a[4]={435700,465700,131525,139025},points_b[4]={228000,396000,228000,396000};
float audio_pll_gcd(float a,float b){
 if(negative(compare(a,b))){float t=a;a=b;b=t;}
 for(uint32_t i=0;i<16;i++){
  if(negative(compare(b,0x1p-23f)))return a;
  float quotient=stock_floorf(divide(a,b));
  float next=subtract_product(a,quotient,b);a=b;b=next;
 }
 return -1.0f;
}
uint32_t audio_pll_integer(float reference,float vco,uint8_t *refdiv,uint16_t *fbdiv){
 float gcd=audio_pll_gcd(vco,reference);
 if(negative(compare(gcd,0x1p-23f)))return 0;
 float multiplier=divide(vco,gcd),divider=divide(reference,gcd);
 /* Stock represents inclusive bounds as strict < nextafter(bound,+Inf). */
 if(!less(compare(stock_fmodf(multiplier,1.0f),0x1.000002p-23f)))return 0;
 if(!less(compare(stock_roundf(multiplier),0x1.e00002p+9f)))return 0;
 uint32_t m=uint_from_float(stock_roundf(multiplier));
 if(!less(compare(stock_fmodf(divider,1.0f),0x1.000002p-23f)))return 0;
 if(!less(compare(stock_roundf(divider),0x1.f80002p+5f)))return 0;
 uint32_t d=uint_from_float(stock_roundf(divider));
 if(m<4){uint32_t factor=udivide(m+3,m);d*=factor;m*=factor;}
 if(d==0||d>=64||(m-4)>=957)return 0;
 *refdiv=d&63;*fbdiv=m&4095;return 1;
}
uint32_t audio_pll_fraction(float reference,float vco,uint8_t *refdiv,uint16_t *fbdiv,uint32_t *fraction){
 float ratio=divide(vco,reference);
 float rd=stock_ceilf(divide(10.0f,ratio));
 if(negative(compare(rd,0x1p-23f)))return 0;
 if(!less(compare(rd,0x1.f80002p+5f)))return 0;
 uint32_t r=uint_from_float(rd);
 float feedback=multiply(float_from_uint(r),ratio);
 uint32_t frac=uint_from_float(stock_roundf(multiply(stock_fmodf(feedback,1.0f),16777216.0f)));
 float integral=stock_floorf(feedback);
 if(negative(compare(integral,10.0f)))return 0;
 if(!less(compare(integral,0x1.800002p+6f)))return 0;
 uint32_t f=uint_from_float(stock_floorf(integral));
 *refdiv=r;*fbdiv=f;*fraction=frac;return 1;
}
uint32_t audio_pll_generate(audio_pll_config *c,float reference,float vco){
 uint8_t rd=0;uint16_t fb=0;uint32_t frac=0;
 if(!c)return 6;
 if(negative(compare(vco,60.0f)))return 5;
 if(!less(compare(vco,0x1.e00002p+9f)))return 5;
 uint32_t integer=audio_pll_integer(reference,vco,&rd,&fb);
 if(!integer&&!audio_pll_fraction(reference,vco,&rd,&fb,&frac))return 1;
 c->vco=less(compare(vco,240.0f))?0:1;c->mode=integer?1:0;
 c->refdiv=rd;c->fbdiv=fb;c->fraction=frac;return 0;
}
uint32_t audio_pll_min_vco(audio_pll_config *c,uint32_t reference,uint32_t output,uint32_t minimum){
 float ref_mhz=divide(float_from_uint(reference),1000000.0f);
 float out_mhz=divide(float_from_uint(output),1000000.0f);
 if(negative(compare(audio_pll_gcd(out_mhz,ref_mhz),1.0f))){
  uint32_t pfd_limit=udivide(reference,udivide(reference,10000000))*10;
  if(pfd_limit>minimum)minimum=pfd_limit;
 }
 uint8_t p1,p2;
 if(output>=minimum){p1=1;p2=1;}
 else{
  uint32_t d=udivide(minimum,output);
  if(minimum-output*d)d++;
  if(d>=50)return 5;
  uint8_t packed=postdiv_table[d];p1=packed>>4;p2=packed&15;
 }
 uint32_t vco=output*(uint32_t)p1*p2;
 float vco_mhz=divide(float_from_uint(vco),1000000.0f);
 ref_mhz=divide(float_from_uint(reference),1000000.0f);
 uint32_t status=audio_pll_generate(c,ref_mhz,vco_mhz);
 if(status)return status;
 uint32_t pfd=udivide(reference,c->refdiv);
 if(reference-(uint32_t)c->refdiv*pfd)pfd++;
 if(pfd<(c->mode==0?10000000u:1000000u))return 5;
 c->postdiv1=p1;c->postdiv2=p2;return 0;
}
static uint32_t score(const audio_pll_config *c,uint32_t reference,uint32_t output){
 uint32_t idx=(c->mode==0?1:0)+(c->vco==1?2:0);
 uint32_t refpoints=udivide((reference/1000000u)*points_b[idx],c->refdiv);
 return refpoints+((output*c->postdiv1*c->postdiv2)/1000000u)*points_a[idx];
}
uint32_t audio_pll_postdiv(audio_pll_config *c,uint32_t reference,uint32_t output){
 audio_pll_config low,high;const audio_pll_config *selected=0;
 uint32_t l=audio_pll_min_vco(&low,reference,output,60000000);
 uint32_t h=audio_pll_min_vco(&high,reference,output,240000000);
 if(l==0&&h==0)selected=score(&low,reference,output)<score(&high,reference,output)?&low:&high;
 else if(h==0)selected=&high;else if(l==0)selected=&low;
 if(!selected)return 5;
 c->vco=selected->vco;c->mode=selected->mode;c->refdiv=selected->refdiv;
 c->postdiv1=selected->postdiv1;c->postdiv2=selected->postdiv2;
 c->fbdiv=selected->fbdiv;c->fraction=selected->fraction;return 0;
}
