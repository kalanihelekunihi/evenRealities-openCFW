/* Native SpO2 summary and signal statistics; source-owned math/heap. */
#include <stdint.h>
#include "../runtime/native_f32_integer.h"
#include "native_spo2_summary.h"
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern float r1_native_sqrtf(float);
extern void r1_goodix_native_quartile_mask(float,const void *,uint32_t,void *);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint16_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static uint8_t U(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static void SH(uintptr_t p,uint32_t o,uint16_t v){*(volatile uint16_t *)(p+o)=v;}
static void SB(uintptr_t p,uint32_t o,uint8_t v){*(volatile uint8_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float sub(float a,float b){volatile float v=a-b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float from_signed(uint32_t a){volatile float v=(float)(int32_t)a;return v;}
__attribute__((noinline)) static float from_unsigned(uint32_t a){volatile float v=(float)a;return v;}
static float madd(float acc,float a,float b){return add(acc,mul(a,b));}
static float msub(float acc,float a,float b){return add(acc,F(B(mul(a,b))^0x80000000u));}
__attribute__((noinline)) static uint32_t compare(uint32_t a,uint32_t b)
{
 uint32_t fp=__builtin_arm_get_fpscr(),flags;
 if(fp&(1u<<24)){
  if((a&0x7fffffffu)&&(a&0x7fffffffu)<0x800000u){a&=0x80000000u;fp|=128u;}
  if((b&0x7fffffffu)&&(b&0x7fffffffu)<0x800000u){b&=0x80000000u;fp|=128u;}
 }
 if((a&0x7fffffffu)>0x7f800000u||(b&0x7fffffffu)>0x7f800000u){flags=0x30000000u;fp|=1u;}
 else if(a==b||!((a|b)&0x7fffffffu))flags=0x60000000u;
 else{int less=(a>>31)!=(b>>31)?(a>>31)!=0:((a>>31)?a>b:a<b);flags=less?0x80000000u:0x20000000u;}
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return flags;
}
static int lt(uint32_t f){return ((f>>31)^((f>>28)&1u))!=0;}
static int gt(uint32_t f){return !(f&0x40000000u)&&!lt(f);}


void r1_goodix_native_i16_mean(const void *input,uint32_t count,void *output)
{
 uintptr_t p=(uintptr_t)input;uint32_t sum=0;
 for(uint32_t left=count;left;--left){sum+=(uint32_t)(int32_t)(int16_t)H(p,0);p+=2u;}
 int32_t result=count?(int32_t)sum/(int32_t)count:0;SH((uintptr_t)output,0,(uint16_t)result);
}
void r1_goodix_native_float_mean(const void *input,uint32_t count,void *output)
{
 uintptr_t p=(uintptr_t)input;float sum=0.0f;
 for(uint32_t left=count;left;--left){sum=add(F(W(p,0)),sum);p+=4u;}
 S((uintptr_t)output,0,B(divide(sum,from_unsigned(count))));
}
void r1_goodix_native_i16_window_mean(const void *record,void *output)
{
 uintptr_t p=(uintptr_t)record;if(H(p,4)){SH((uintptr_t)output,0,0);uint32_t count=H(p,4);uintptr_t in=W(p,0);r1_goodix_native_i16_mean((void *)in,count,output);}
}
void r1_goodix_native_float_window_mean(const void *record,void *output)
{
 uintptr_t p=(uintptr_t)record;if(H(p,4)){S((uintptr_t)output,0,0);uint32_t count=H(p,4);uintptr_t in=W(p,0);r1_goodix_native_float_mean((void *)in,count,output);}
}
void r1_goodix_native_sum_squares(const void *input,uint32_t count,void *output)
{
 uintptr_t p=(uintptr_t)input;float sum=0.0f;
 while(count--){float sample=F(W(p,0));p+=4u;sum=madd(sum,sample,sample);}S((uintptr_t)output,0,B(sum));
}
void r1_goodix_native_dot_product(const void *first,const void *second,uint32_t count,void *output)
{
 uintptr_t a=(uintptr_t)first,b=(uintptr_t)second;float sum=0.0f;
 while(count--){float x=F(W(a,0));a+=4u;float y=F(W(b,0));b+=4u;sum=madd(sum,x,y);}S((uintptr_t)output,0,B(sum));
}
void r1_goodix_native_float_min_index(const void *input,uint32_t count,void *minimum,void *index)
{
 uintptr_t p=(uintptr_t)input;uint32_t winner=0,value=W(p,0);p+=4u;
 for(uint32_t left=count-1u;left;--left){uint32_t next=W(p,0);p+=4u;if(gt(compare(value,next))){value=next;winner=count-left;}}
 S((uintptr_t)minimum,0,value);S((uintptr_t)index,0,winner);
}
float r1_goodix_native_window_correlation(const void *first,const void *second,uint32_t count)
{
 uint32_t dot=0,a=0,b=0;r1_goodix_native_dot_product(first,second,count,&dot);
 r1_goodix_native_sum_squares(first,count,&a);r1_goodix_native_sum_squares(second,count,&b);
 if(lt(compare(a,0)))a=0;else a=B(__builtin_sqrtf(F(a)));
 if(lt(compare(b,0)))b=0;else b=B(__builtin_sqrtf(F(b)));
 float result=0.0f;
 if(!(compare(a,0)&0x40000000u)&&!(compare(b,0)&0x40000000u)){
  float quotient=divide(F(dot),mul(F(a),F(b)));if(gt(compare(B(quotient),0)))result=quotient;
 }
 return result;
}
void r1_goodix_native_peak_pair_indices(uint32_t iteration,const void *histories,void *starts,void *ends,void *number)
{
 uintptr_t h=(uintptr_t)histories,s=(uintptr_t)starts,e=(uintptr_t)ends,n=(uintptr_t)number;
 uint32_t maxima=H(h,4),minima=H(h,16);uintptr_t maxbuf=W(h,0),minbuf=W(h,12);S(n,0,0);
 uint32_t i=H(h,8),j=H(h,20),offset=(iteration-5u)*25u;
 for(;(int32_t)i<(int32_t)maxima;++i){
  uint32_t start=W(maxbuf,i*4u)-offset;S(s,W(n,0)*4u,start);
  while((int32_t)j<(int32_t)minima){if((int32_t)W(minbuf,j*4u)>=(int32_t)W(maxbuf,i*4u))break;++j;}
  if((int32_t)j<(int32_t)minima&&((int32_t)i>=(int32_t)(maxima-1u)||(int32_t)W(minbuf,j*4u)<(int32_t)W(maxbuf,(i+1u)*4u))){uint32_t end=W(minbuf,j*4u)-offset;++j;S(e,W(n,0)*4u,end);}
  else S(e,W(n,0)*4u,start);
  S(n,0,W(n,0)+1u);
 }
}
static uint64_t key(uint64_t x){return x>>63?x:UINT64_C(0x8000000000000000)-x;}
static uint64_t scaled(float x,uint64_t factor){return r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(B(x)),factor);}
void r1_goodix_native_spo2_pair_statistics(const void *input,uint32_t count,const void *descriptor,const void *starts,const void *ends,uint32_t pairs,void *output)
{
 (void)descriptor;uintptr_t in=(uintptr_t)input,s=(uintptr_t)starts,e=(uintptr_t)ends,out=(uintptr_t)output;
 uint32_t accepted=0;float sum=0.0f,squares=0.0f,previous=0.0f;
 for(uint32_t i=0;(int32_t)i<(int32_t)pairs;++i){
  float difference=sub(F(W(in,W(s,i*4u)*4u)),F(W(in,W(e,i*4u)*4u)));
  if((compare(B(difference),0)&0x40000000u)&&i==pairs-1u&&(int32_t)accepted>0){
   uint32_t start=W(s,i*4u),minimum,index;r1_goodix_native_float_min_index((void *)(in+start*4u),count-start,&minimum,&index);
   start=W(s,i*4u);if((int32_t)index<(int32_t)(count-start-1u)){
    difference=sub(F(W(in,start*4u)),F(minimum));uint64_t lower=scaled(previous,UINT64_C(0x3feb333333333333));uint64_t value=r1_binary32_to_binary64_bits(B(difference));
    if(key(lower)<key(value))difference=0.0f;
    else{uint64_t upper=scaled(previous,UINT64_C(0x3ff2666666666666));value=r1_binary32_to_binary64_bits(B(difference));if(key(value)<key(upper))difference=0.0f;}
   }
  }
  if(gt(compare(B(difference),0))){squares=madd(squares,difference,difference);sum=add(sum,difference);previous=difference;++accepted;}
 }
 if((int32_t)accepted>0){sum=divide(sum,from_signed(accepted));squares=divide(squares,from_signed(accepted));}
 float variation=-1.0f;
 if((int32_t)accepted>=2&&!(compare(B(sum),0)&0x40000000u)){squares=msub(squares,sum,sum);variation=divide(squares,mul(sum,sum));}
 S(out,8,B(sum));S(out,12,B(variation));uint32_t scaled_count=pairs*5u;int32_t target=(int32_t)scaled_count/6;
 SB(out,17,pairs&&(int32_t)accepted>=target);SB(out,16,(uint8_t)accepted);
}
void r1_goodix_native_spo2_outlier_count(const void *input,uint32_t count,const void *descriptor,void *output)
{
 uintptr_t d=(uintptr_t)descriptor,out=(uintptr_t)output;void *mask=goodix_mem_malloc((int32_t)count);
 r1_goodix_native_quartile_mask(divide(from_unsigned(U(d,64)),10.0f),input,count,mask);
 uint32_t sum=0;S(out,0,0);for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){uint32_t value=(uint32_t)(int32_t)(int8_t)U((uintptr_t)mask,i);if(value)S(out,0,W(out,0)+1u);sum+=value;}
 if(sum){uint32_t magnitude=(int32_t)sum<0?0u-sum:sum;if(magnitude==W(out,0))S(out,0,0);}
 goodix_mem_free(mask);
}
uint32_t r1_goodix_native_spo2_channel_statistics(const void *input,uint32_t count,const void *starts,const void *ends,uint32_t pairs,const void *descriptor,void *output)
{
 r1_goodix_native_spo2_outlier_count(input,count,descriptor,output);r1_goodix_native_spo2_pair_statistics(input,count,descriptor,starts,ends,pairs,output);return 0;
}
void r1_goodix_native_spo2_motion_summary(const void *descriptor,const void *aggregate,void *summary)
{
 uintptr_t d=(uintptr_t)descriptor,a=(uintptr_t)aggregate,out=(uintptr_t)summary;uint32_t count=H(a,12);if(count>=125u)count=125u;
 float squares=0.0f,sum=0.0f;
 for(uint32_t i=0;i<count;++i){float value=from_signed((uint32_t)(int32_t)(int16_t)H(W(a,8),i*2u));squares=madd(squares,value,value);sum=add(sum,value);}
 float mean=divide(sum,from_unsigned(count));float variance=msub(divide(squares,from_unsigned(count)),mean,mean),deviation=0.0f;
 if(compare(B(variance),0)&0x20000000u)deviation=msub(divide(squares,from_unsigned(count)),mean,mean);
 deviation=r1_native_sqrtf(deviation);uint32_t factor=W(d,44),base=W(d,40);
 float scaled_deviation=mul(from_unsigned(factor),deviation);float converted_base=from_unsigned(base);float threshold;
 if(compare(B(scaled_deviation),B(converted_base))&0x20000000u)threshold=mul(from_unsigned(factor),deviation);else threshold=from_unsigned(base);
 uint32_t ceiling=W(d,36);float converted_ceiling=from_unsigned(ceiling);
 if(compare(B(threshold),B(converted_ceiling))&0x20000000u)threshold=from_unsigned(ceiling);
 else{float f=from_unsigned(factor),b=from_unsigned(base);float scaled=mul(f,deviation);if(compare(B(scaled),B(b))&0x20000000u)threshold=mul(from_unsigned(factor),deviation);else threshold=from_unsigned(base);}
 uint32_t trunc_threshold=r1_native_f32_integer_bits(B(threshold),0),trunc_mean=r1_native_f32_integer_bits(B(mean),0),outliers=0;
 for(uint32_t i=0;i<count;++i){int32_t value=(int16_t)H(W(a,8),i*2u),delta=value-(int16_t)trunc_mean;if(delta<0)delta=-delta;if(delta>(int32_t)trunc_threshold)outliers=(outliers+1u)&0xffffu;}
 SH(out,0,(uint16_t)trunc_mean);SB(out,2,(uint8_t)trunc_threshold);SB(out,3,(uint8_t)outliers);
}
void r1_goodix_native_spo2_aux_summary(const void *descriptor,const void *aggregate,void *summary,uint32_t incoming)
{
 (void)descriptor;(void)incoming;uint16_t mean=0;r1_goodix_native_i16_window_mean((const void *)((uintptr_t)aggregate+20u),&mean);SH((uintptr_t)summary,4,mean);
}
uint32_t r1_goodix_native_spo2_common_summary(const void *descriptor,const void *aggregate,void *summary)
{
 r1_goodix_native_spo2_motion_summary(descriptor,aggregate,summary);r1_goodix_native_spo2_aux_summary(descriptor,aggregate,summary,0);return 0;
}
uint32_t r1_goodix_native_spo2_channel_summary(const void *channel,const void *histories,const void *descriptor,uint32_t iteration,void *summary)
{
 uintptr_t c=(uintptr_t)channel,h=(uintptr_t)histories,out=W((uintptr_t)summary,8);uint32_t capacity=H(h,4),number=0;
 uintptr_t starts=(uintptr_t)goodix_mem_malloc((int32_t)(capacity*8u)),ends=starts+capacity*4u;r1_goodix_native_peak_pair_indices(iteration,histories,(void *)starts,(void *)ends,&number);
 uintptr_t first=W(c,216)+(uint32_t)H(c,220)*4u-500u;
 r1_goodix_native_spo2_channel_statistics((void *)first,125,(void *)starts,(void *)ends,number,descriptor,(void *)(out+20u));r1_goodix_native_float_window_mean((void *)(c+84u),(void *)(out+24u));
 uintptr_t second=W(c,232)+(uint32_t)H(c,236)*4u-500u;
 r1_goodix_native_spo2_channel_statistics((void *)second,125,(void *)starts,(void *)ends,number,descriptor,(void *)out);r1_goodix_native_float_window_mean((void *)(c+184u),(void *)(out+4u));
 goodix_mem_free((void *)starts);float correlation=mul(r1_goodix_native_window_correlation((void *)second,(void *)first,125),100.0f);SB(out,40,(uint8_t)r1_native_f32_integer_bits(B(correlation),0));return 0;
}
void r1_goodix_spo2_summary(const void *descriptor,void *aggregate,uint32_t iteration,void *summary)
{
 r1_goodix_native_spo2_common_summary(descriptor,aggregate,summary);uintptr_t a=(uintptr_t)aggregate;
 r1_goodix_native_spo2_channel_summary((void *)(uintptr_t)W(a,0),(void *)(uintptr_t)W(a,28),descriptor,iteration,summary);
}
