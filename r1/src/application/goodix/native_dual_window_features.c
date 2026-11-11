/* Native dual-window feature extraction0x29144. Eight core arguments,
 * actual C sensor helpers,live histories and native allocation/output order. */
#include "native_dual_window_features.h"
#include <stdint.h>
#include "native_autocorrelation.h"
#include "native_peak_selection.h"
#include "native_spo2_peak_metrics.h"
#include "native_peak_rate.h"
#include "native_packed_conversion.h"
#include "native_spo2_summary.h"
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float F(uint32_t x){union{uint32_t u;float f;}v={.u=x};return v.f;}
static uint32_t B(float x){union{uint32_t u;float f;}v={.f=x};return v.u;}
__attribute__((noinline)) static float add(float a,float b){volatile float v=a+b;return v;}
__attribute__((noinline)) static float mul(float a,float b){volatile float v=a*b;return v;}
__attribute__((noinline)) static float divide(float a,float b){volatile float v=a/b;return v;}
__attribute__((noinline)) static float root(float a){return __builtin_sqrtf(a);}
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

void r1_goodix_native_dual_window_features(const void *record,void *first_rms,void *second_rms,void *correlation,void *first_rate,void *second_rate,void *first_quality,void *second_quality)
{
 uintptr_t p=(uintptr_t)record;void *work=goodix_mem_malloc(500);uintptr_t first=W(p,216)+((uint32_t)H(p,220)-125u)*4u;
 r1_goodix_native_normalized_autocorrelation((void *)first,125,work);void *indices=goodix_mem_malloc(126);uint32_t count=0;
 r1_goodix_native_peak_indices(work,125,0,62,indices,&count);uintptr_t values=(uintptr_t)goodix_mem_malloc(252);
 for(uint32_t i=0;i<count;i=(uint32_t)(int32_t)(int8_t)(i+1u))S(values,i*4u,W((uintptr_t)work,H((uintptr_t)indices,i*2u)*4u));
 if(!count)S((uintptr_t)first_rms,0,0x3f000000u);else{r1_goodix_native_peak_feature_metrics((void *)values,indices,count,125,first_rms,first_quality);r1_goodix_native_peak_rate((void *)values,indices,count,first_rate);}
 goodix_mem_free((void *)values);uint32_t first_energy=0;r1_goodix_native_sum_squares(work,125,&first_energy);void *packed=goodix_mem_malloc(250);r1_goodix_native_pack_array(packed,work,125,r1_goodix_native_pack_5_10);
 uintptr_t second=W(p,232)+((uint32_t)H(p,236)-125u)*4u;r1_goodix_native_normalized_autocorrelation((void *)second,125,work);r1_goodix_native_peak_indices(work,125,0,62,indices,&count);values=(uintptr_t)goodix_mem_malloc(252);
 for(uint32_t i=0;i<count;i=(uint32_t)(int32_t)(int8_t)(i+1u))S(values,i*4u,W((uintptr_t)work,H((uintptr_t)indices,i*2u)*4u));
 if(!count)S((uintptr_t)second_rms,0,0x3f000000u);else{r1_goodix_native_peak_feature_metrics((void *)values,indices,count,125,second_rms,second_quality);r1_goodix_native_peak_rate((void *)values,indices,count,second_rate);}
 goodix_mem_free((void *)values);goodix_mem_free(indices);uint32_t second_energy=0;r1_goodix_native_sum_squares(work,125,&second_energy);float sum=0.0f;
 for(uint32_t i=0;i<125;++i){float a=r1_goodix_native_unpack_5_10(H((uintptr_t)packed,i*2u)),b=F(W((uintptr_t)work,i*4u));sum=add(sum,mul(a,b));}
 uint32_t flags=compare(first_energy,0);if(((flags>>31)^(flags>>28))&1u)first_energy=0;else first_energy=B(root(F(first_energy)));
 flags=compare(second_energy,0);if(((flags>>31)^(flags>>28))&1u)second_energy=0;else second_energy=B(root(F(second_energy)));
 if(compare(first_energy,0)==0x60000000u||compare(second_energy,0)==0x60000000u)S((uintptr_t)correlation,0,0);else S((uintptr_t)correlation,0,B(divide(sum,mul(F(first_energy),F(second_energy)))));
 goodix_mem_free(packed);goodix_mem_free(work);
}
