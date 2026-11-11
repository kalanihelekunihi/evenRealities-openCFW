#include "native_spo2_spectral.h"
#include <stddef.h>
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void r1_goodix_native_quartile_mask(float,const void *,uint32_t,void *);
extern void r1_goodix_native_zero_masked_runs(const void *,uint32_t,const void *,void *);
extern void r1_goodix_native_scale_copy(const void *,uint32_t,uint32_t,void *,void *);
extern void r1_goodix_native_spectral_prepare(const void *,uint32_t,uint32_t,void **,uint32_t,uint32_t,uint32_t);
extern void r1_goodix_native_peak_select(float,const void *,uint32_t,int32_t,int32_t,int32_t,int32_t,void *,void *,void *);
extern void r1_goodix_native_harmonic_select(float,const void *,const void *,uint32_t,void *,void *,uint32_t);
extern float r1_native_ceilf(float),r1_native_floorf(float);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint16_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static float value(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t bits(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float add(float a,float b){return a+b;}
__attribute__((noinline)) static float divide(float a,float b){return a/b;}
/* Native 0x766ac: preprocessing and spectral analysis of the live optical
 * window. The heap provider zero-fills allocations, including samples.
 * Keep the accumulator-first addition and native allocation/free order:
 * NaN selection, FPSCR and FFT tail reads expose their effects.
 * The parent currently discards the temporary peak/group outputs, as stock
 * does; subsequent ratio/quality stages remain separate dependencies. */
uint32_t r1_goodix_spo2_spectral(void *context,const void *descriptor)
{
 uintptr_t samples=(uintptr_t)goodix_mem_malloc(500),record=W((uintptr_t)context,0);
 uintptr_t input=W(record,0xd8);uint32_t offset=(uint32_t)H(record,0xdc)*4u-500u;
 for(uint32_t i=0;i<125u;++i)S(samples,i*4u,bits(add(value(W(samples,i*4u)),value(W(input,offset+i*4u)))));
 void *mask=goodix_mem_malloc(125);float weight=divide((float)*(const volatile uint8_t *)((uintptr_t)descriptor+0x40u),10.0f);
 r1_goodix_native_quartile_mask(weight,(void *)samples,125,mask);
 uint32_t bins=(uint32_t)r1_native_ceilf(value(0x4250cccdu)),capacity=bins<125u?125u:bins;
 void *clean=goodix_mem_malloc((int32_t)(capacity*4u));r1_goodix_native_zero_masked_runs((void *)samples,125,mask,clean);goodix_mem_free(mask);goodix_mem_free((void *)samples);
 capacity=bins<125u?125u:bins;void *window=goodix_mem_malloc((int32_t)(capacity*4u));uint32_t factor=0x3f800000u;
 r1_goodix_native_scale_copy(clean,125,1,window,&factor);goodix_mem_free(clean);
 r1_goodix_native_spectral_prepare(window,125,256,&window,0,1,bins);
 void *indices=goodix_mem_malloc(20),*amplitudes=goodix_mem_malloc(20);
 uint64_t width=r1_binary32_to_binary64_bits(factor);width=r1_format_double_multiply_bits(width,UINT64_C(0x3fe999999999999a));width=r1_format_double_multiply_bits(width,UINT64_C(0x4070000000000000));width=r1_format_double_divide_bits(width,UINT64_C(0x405f400000000000));
 int32_t radius=(int32_t)r1_native_floorf(value(r1_log_double_to_float_bits(width))),begin=(int32_t)r1_native_floorf(value(0x40a3d70au));uint32_t count=0;
 r1_goodix_native_peak_select(value(0x3dcccccdu),window,bins,begin,(int32_t)bins,radius,5,indices,amplitudes,&count);
 void *groups=goodix_mem_malloc(12),*flags=goodix_mem_malloc(3);
 r1_goodix_native_harmonic_select(value(0x3dc80000u),indices,amplitudes,count,groups,flags,3);
 goodix_mem_free(window);goodix_mem_free(indices);goodix_mem_free(amplitudes);goodix_mem_free(groups);goodix_mem_free(flags);return 0;
}
