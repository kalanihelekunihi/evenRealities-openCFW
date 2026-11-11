/* Native inference normalization0x95750 and tensor descriptor0x5d5d0. */
#include <stdint.h>
#include "native_spo2_infer_support.h"
extern void __aeabi_memclr(void *,uint32_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
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


void r1_goodix_native_spo2_clip_normalize(const void *input,uint32_t count,void *output)
{
 uintptr_t in=(uintptr_t)input,out=(uintptr_t)output;uint32_t maximum=0;
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){
  uint32_t value=W(in,i*4u),absolute=value;
  if(!(compare(value,0)&0x20000000u))absolute=value^0x80000000u;
  if(gt(compare(absolute,maximum))){if(!(compare(value,0)&0x20000000u))maximum=value^0x80000000u;else maximum=value;}
 }
 if((int32_t)maximum>=(int32_t)0x3ca3d70au)maximum=0x3ca3d70au;
 if((int32_t)maximum<(int32_t)0x33d6bf95u){__aeabi_memclr(output,count*4u);return;}
 uint32_t negative=maximum^0x80000000u;
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){
  uint32_t value=W(in,i*4u),upper=value;if(gt(compare(value,maximum)))upper=maximum;
  if(!(compare(upper,negative)&0x20000000u))value=negative;
  else if(gt(compare(value,maximum)))value=maximum;
  S(out,i*4u,B(divide(F(value),F(maximum))));
 }
}
void *r1_goodix_native_tensor_descriptor_initialize(void *descriptor,uint32_t batches,uint32_t rows,uint32_t columns,uint32_t element_bytes,void *data)
{
 uintptr_t d=(uintptr_t)descriptor;S(d,0,element_bytes);S(d,4,batches);S(d,8,rows);S(d,12,columns);S(d,16,(uint32_t)(uintptr_t)data);return data;
}
