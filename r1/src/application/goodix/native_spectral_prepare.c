/* Native spectral prepare0x765e4 and copy0x35772. Actual native heap,
 * encoded math, packed5/10 conversion, memory and real FFT dependencies.
 * Own both tail words read by the real FFT; zero-filled heap initializes them.
 */
#include <stdint.h>
#include <stddef.h>
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void *r1_goodix_native_reallocate(void *,uint32_t);
extern void *memmove(void *,const void *,size_t);
extern uint32_t goodix_primitives_packed_5_10_to_f32_bits(uint16_t);
extern void r1_goodix_native_real_transform(void *,uint32_t,uint32_t,const void *);
extern uint64_t r1_unsigned32_to_binary64_bits(uint32_t);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
static uint32_t W(uintptr_t p,uint32_t i){return *(const volatile uint32_t *)(p+i*4u);}
static void S(uintptr_t p,uint32_t i,uint32_t x){*(volatile uint32_t *)(p+i*4u)=x;}
void r1_goodix_native_spectral_prepare(const void *input,uint32_t input_count,uint32_t transform_count,void **output,uint32_t packed,uint32_t unnormalized,uint32_t output_count)
{
 uintptr_t p=(uintptr_t)goodix_mem_malloc((int32_t)(transform_count*4u+8u));
 if(packed){for(uint32_t i=0;i<input_count;++i)S(p,i,goodix_primitives_packed_5_10_to_f32_bits(*(const volatile uint16_t *)((uintptr_t)input+i*2u)));}
 else memmove((void *)p,input,input_count*4u);
 r1_goodix_native_real_transform((void *)p,input_count,transform_count,output);
 if(!unnormalized)for(uint32_t i=0;i<transform_count;++i){
  uint64_t n=r1_unsigned32_to_binary64_bits(input_count);
  uint64_t v=r1_binary32_to_binary64_bits(W(p,i));
  v=r1_format_double_multiply_bits(v,UINT64_C(0x4000000000000000));
  v=r1_format_double_divide_bits(v,n);S(p,i,r1_log_double_to_float_bits(v));
 }
 uintptr_t out=*(const volatile uint32_t *)output;
 if(out){memmove((void *)out,(void *)p,output_count*4u);goodix_mem_free((void *)p);}
 else *(volatile uint32_t *)output=(uint32_t)(uintptr_t)r1_goodix_native_reallocate((void *)p,output_count*4u);
}
/* Explicit ninth argument supplies the stock caller's incoming R9 for legacy
 * non256 calls; the256-point core selects its owned coefficients. */
void r1_goodix_native_spectral_copy(const void *input,uint32_t input_count,uint32_t transform_count,void **output,uint32_t unused_a,uint32_t unused_b,uint32_t output_count,void *scratch,const void *incoming_table)
{
 (void)unused_a;(void)unused_b;memmove(scratch,input,input_count*4u);
 r1_goodix_native_real_transform(scratch,input_count,transform_count,incoming_table);
 memmove((void *)(uintptr_t)*(const volatile uint32_t *)output,scratch,output_count*4u);
}
