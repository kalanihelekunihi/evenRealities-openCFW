/* Native quantile0x30cd8, insertion sort0x35812 and quartile mask0x7309c.
 * Preserve original-input endpoints, encoded double comparisons and every
 * interval comparison. Actual C math helpers retain the native bit semantics.
 */
#include <stdint.h>
#include <stddef.h>
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void *memmove(void *,const void *,size_t);
extern uint64_t r1_signed32_to_binary64_bits(uint32_t);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
static uint32_t W(uintptr_t p,uint32_t i){return *(const volatile uint32_t *)(p+i*4u);}
static void S(uintptr_t p,uint32_t i,uint32_t v){*(volatile uint32_t *)(p+i*4u)=v;}
static float value(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t bits(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
static uint32_t compare(uint32_t a,uint32_t b)
{
 uint32_t fp=__builtin_arm_get_fpscr();
 if(fp&(1u<<24)){
  if((a&0x7fffffffu)&&(a&0x7fffffffu)<0x800000u){a&=0x80000000u;fp|=128;}
  if((b&0x7fffffffu)&&(b&0x7fffffffu)<0x800000u){b&=0x80000000u;fp|=128;}
 }
 uint32_t flags;
 if((a&0x7fffffffu)>0x7f800000u||(b&0x7fffffffu)>0x7f800000u){flags=0x30000000u;fp|=1;}
 else if(a==b||!((a|b)&0x7fffffffu))flags=0x60000000u;
 else{uint32_t less=(a>>31)!=(b>>31)?a>>31:(a>>31)?a>b:a<b;flags=less?0x80000000u:0x20000000u;}
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return flags;
}
void r1_goodix_native_sort_floats(void *input,uint32_t count)
{
 uintptr_t p=(uintptr_t)input;
 for(uint32_t i=1;(int32_t)i<(int32_t)count;++i){
  uint32_t pivot=W(p,i),j=i-1u;
  while((int32_t)j>=0){uint32_t sample=W(p,j);if(compare(sample,pivot)!=0x20000000u)break;S(p,j+1u,sample);--j;}
  S(p,j+1u,pivot);
 }
}
static uint64_t key(uint64_t input){return input>>63?input:UINT64_C(0x8000000000000000)-input;}
__attribute__((noinline)) static float add(float a,float b){return a+b;}
__attribute__((noinline)) static float interpolate(float q,float lower,float upper,float a,float b)
{return add(a,((q-lower)/(upper-lower))*(b-a));}
float r1_goodix_native_quantile(float q,const void *input,uint32_t count)
{
 uint64_t n=r1_signed32_to_binary64_bits(count),half=UINT64_C(0x3fe0000000000000);
 uintptr_t scratch=(uintptr_t)goodix_mem_malloc((int32_t)(count*4u));memmove((void *)scratch,input,count*4u);r1_goodix_native_sort_floats((void *)scratch,count);
 float result=0;uint64_t lower=r1_format_double_divide_bits(half,n),converted=r1_binary32_to_binary64_bits(bits(q));
 if(key(lower)<=key(converted))result=value(W((uintptr_t)input,0));
 else{
  uint64_t last=r1_signed32_to_binary64_bits(count-1u);last=r1_format_double_add_bits(last,half);last=r1_format_double_divide_bits(last,n);converted=r1_binary32_to_binary64_bits(bits(q));
  if(key(converted)<key(last))result=value(W((uintptr_t)input,count-1u));
  else for(uint32_t i=0;(int32_t)i<(int32_t)(count-1u);++i){
   uint64_t a=r1_signed32_to_binary64_bits(i);a=r1_format_double_add_bits(a,half);a=r1_format_double_divide_bits(a,n);float lo=value(r1_log_double_to_float_bits(a));
   uint64_t b=r1_signed32_to_binary64_bits(i+1u);b=r1_format_double_add_bits(b,half);b=r1_format_double_divide_bits(b,n);float hi=value(r1_log_double_to_float_bits(b));
   if(compare(bits(lo),bits(q))==0x80000000u){uint32_t relation=compare(bits(q),bits(hi));if(relation!=0x20000000u&&relation!=0x30000000u)result=interpolate(q,lo,hi,value(W(scratch,i)),value(W(scratch,i+1u)));}
  }
 }
 goodix_mem_free((void *)scratch);return result;
}
__attribute__((noinline)) static float subtract(float a,float b){return a-b;}
__attribute__((noinline)) static float multiply(float a,float b){return a*b;}
void r1_goodix_native_quartile_mask(float weight,const void *input,uint32_t count,void *mask)
{
 float upper_q=r1_goodix_native_quantile(0.75f,input,count);
 float lower_q=r1_goodix_native_quantile(0.25f,input,count);
 float difference=subtract(upper_q,lower_q);
 float upper=add(upper_q,multiply(difference,weight));
 float lower=subtract(lower_q,multiply(difference,weight));
 uintptr_t p=(uintptr_t)input,out=(uintptr_t)mask;
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){
  *(volatile uint8_t *)(out+i)=0;uint32_t sample=W(p,i);
  if(compare(sample,bits(upper))==0x20000000u||compare(sample,bits(lower))==0x80000000u)*(volatile uint8_t *)(out+i)=1;
  if(compare(W(p,i),bits(lower))==0x80000000u)*(volatile uint8_t *)(out+i)=255;
 }
}
