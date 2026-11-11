/* Native harmonic grouping0x35850, including shared tail0x35c78.
 * Ordinary C preserves encoded comparison rules, ordered FP operations,
 * the six-allocation lifecycle and live buffers. No inline assembly.
 */
#include <stdint.h>
#include <stddef.h>
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void *memmove(void *,const void *,size_t);
extern void __aeabi_memclr(void *,size_t);
extern float r1_native_sqrtf(float);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
static uint32_t W(uintptr_t p,uint32_t i){return *(const volatile uint32_t *)(p+i*4u);}
static void S(uintptr_t p,uint32_t i,uint32_t v){*(volatile uint32_t *)(p+i*4u)=v;}
static uint8_t B(uintptr_t p,uint32_t i){return *(const volatile uint8_t *)(p+i);}
static void SB(uintptr_t p,uint32_t i,uint8_t v){*(volatile uint8_t *)(p+i)=v;}
static float value(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t bits(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
static float negate(float f){return value(bits(f)^0x80000000u);}
__attribute__((noinline)) static float add(float a,float b){return a+b;}
__attribute__((noinline)) static float subtract(float a,float b){return a-b;}
__attribute__((noinline)) static float multiply(float a,float b){return a*b;}
__attribute__((noinline)) static float divide(float a,float b){return a/b;}
__attribute__((noinline)) static float convert(uint32_t a){return (float)(int32_t)a;}
static float mla(float d,float a,float b){return add(d,multiply(a,b));}
static float mls(float d,float a,float b){return add(d,negate(multiply(a,b)));}
static float nmls(float d,float a,float b){return add(negate(d),multiply(a,b));}
static uint64_t key(uint64_t input){return input>>63?input:UINT64_C(0x8000000000000000)-input;}
static uint32_t encoded_less(uint64_t a,uint64_t b){return key(a)<key(b);}
static uint32_t sdiv(uint32_t a,uint32_t b){if(!b)return 0;if(a==0x80000000u&&b==0xffffffffu)return a;return (uint32_t)((int32_t)a/(int32_t)b);}
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

void r1_goodix_native_harmonic_select(float weight,const void *peak_indices,const void *peak_values,uint32_t peak_count,void *output_indices,void *output_flags,uint32_t harmonics)
{
 uint32_t bytes=harmonics*4u;uintptr_t best=(uintptr_t)goodix_mem_malloc((int32_t)bytes);
 void *unused=goodix_mem_malloc((int32_t)bytes);uintptr_t best_flags=(uintptr_t)goodix_mem_malloc((int32_t)harmonics);
 uintptr_t current=(uintptr_t)goodix_mem_malloc((int32_t)bytes),amplitudes=(uintptr_t)goodix_mem_malloc((int32_t)bytes),flags=(uintptr_t)goodix_mem_malloc((int32_t)harmonics);
 uintptr_t peaks=(uintptr_t)peak_indices,values=(uintptr_t)peak_values;float best_amplitude=0,best_score=0,scale=multiply(weight,60.0f);
 for(uint32_t seed=0;(int32_t)seed<(int32_t)peak_count;++seed){
  float center=convert(W(peaks,seed));
  for(uint32_t base=1;(int32_t)base<=(int32_t)harmonics;++base){
   float ratio=divide(center,convert(base));__aeabi_memclr((void *)current,bytes);__aeabi_memclr((void *)amplitudes,bytes);__aeabi_memclr((void *)flags,harmonics);
   for(uint32_t j=1;(int32_t)j<=(int32_t)harmonics;++j){
    float predicted=multiply(convert(j),ratio),distance=10000.0f;
    for(uint32_t q=0;(int32_t)q<(int32_t)peak_count;++q){
     uint32_t index=W(peaks,q);float delta=subtract(predicted,convert(index));uint32_t relation=compare(bits(delta),0);float observed=convert(index);
     float error=(relation&0x20000000u)?subtract(predicted,observed):subtract(observed,predicted);error=multiply(scale,error);
     uint32_t c=compare(bits(error),bits(distance));
     if(c==0x80000000u)goto nearest;
     c=compare(bits(error),bits(distance));
     if(c==0x60000000u&&compare(W(values,q),W(amplitudes,j-1u))==0x20000000u){
 nearest:distance=error;S(current,j-1u,index);S(amplitudes,j-1u,W(values,q));
     }
    }
    float limit=10.0f;
    if(j!=base){float r=divide(convert(j),convert(base)),squared=mla(1.0f,r,r);float first=multiply(r1_native_sqrtf(squared),5.0f);limit=(int32_t)bits(first)>=0x41700000?15.0f:multiply(r1_native_sqrtf(squared),5.0f);}
    uint32_t c=compare(bits(distance),bits(limit));if(!(c&0x20000000u)||(c&0x40000000u))SB(flags,j-1u,1);
   }
   uint32_t sum_weights=0;float sum=0;
   for(uint32_t j=1;(int32_t)j<=(int32_t)harmonics;++j)if(B(flags,j-1u)==1){sum_weights+=j;sum=add(convert(W(current,j-1u)),sum);}
   float mean=divide(sum,convert(sum_weights)),error_sum=0,norm=0;
   for(uint32_t j=1;(int32_t)j<=(int32_t)harmonics;++j)if(B(flags,j-1u)==1){
    uint32_t others=0;for(uint32_t k=1;(int32_t)k<=(int32_t)harmonics;++k)if(k!=j&&B(flags,k-1u)==1)++others;
    uint32_t sample=W(current,j-1u);float residual=mls(convert(sample),convert(j),mean);uint32_t c=compare(bits(residual),0);
    float a=convert(sample),b=convert(j);residual=(c&0x20000000u)?mls(a,b,mean):nmls(a,b,mean);
    error_sum=mla(error_sum,scale,residual);
    float numerator=convert(others*j*j),u=convert(sum_weights-j),v=convert(sum_weights-j);numerator=mla(numerator,u,v);
    norm=add(r1_native_sqrtf(divide(numerator,convert(sum_weights*sum_weights))),norm);
   }
   if((int32_t)bits(norm)<=(int32_t)0x358637bdu)norm=value(0x358637bdu);
   float score=divide(error_sum,norm),amplitude=0;
   for(uint32_t j=1;(int32_t)j<=(int32_t)harmonics;++j)if(B(flags,j-1u)==1)amplitude=add(value(W(amplitudes,j-1u)),amplitude);
   if((int32_t)bits(score)<0x40a00000&&B(flags,0)==1){
    uint32_t banned=0;
    uint64_t candidate=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(bits(amplitude)),UINT64_C(0x3feccccccccccccd));
    if(encoded_less(r1_binary32_to_binary64_bits(bits(best_amplitude)),candidate)&&(int32_t)bits(best_score)<0x3f800000){
     float threshold=multiply(best_score,2.0f);uint64_t threshold64=(int32_t)bits(threshold)>0x3f000000?r1_binary32_to_binary64_bits(bits(threshold)):UINT64_C(0x3fe0000000000000);
     if(encoded_less(r1_binary32_to_binary64_bits(bits(score)),threshold64))goto suppress;
    }
    candidate=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(bits(amplitude)),UINT64_C(0x3fe3333333333333));
    if(encoded_less(r1_binary32_to_binary64_bits(bits(best_amplitude)),candidate)&&(int32_t)bits(best_score)<0x3f000000){
     float threshold=multiply(best_score,2.0f);if((int32_t)bits(threshold)<=0x40400000)threshold=3.0f;
     if(compare(bits(threshold),bits(score))==0x80000000u)goto suppress;
    }
    goto select;
 suppress:
    if(B(best_flags,0)==1&&B(flags,1)==1&&W(best,0)==W(current,1)&&B(best_flags,1)==1&&B(flags,3)==1&&W(best,1)==W(current,3)){
     uint32_t ratio=sdiv(W(best,2),W(current,0));if(ratio!=6||B(best_flags,2)==0){banned=1;goto select;}
    }
 select:
    if(compare(bits(amplitude),bits(best_amplitude))==0x20000000u&&!banned){best_amplitude=amplitude;memmove((void *)best,(void *)current,bytes);memmove((void *)best_flags,(void *)flags,harmonics);best_score=score;}
   }
  }
  if((B(best_flags,0)==1&&B(best_flags,1)==1&&B(best_flags,2)==1)||(int32_t)seed>=2)break;
 }
 memmove(output_indices,(void *)best,bytes);memmove(output_flags,(void *)best_flags,harmonics);
 goodix_mem_free((void *)best);goodix_mem_free(unused);goodix_mem_free((void *)best_flags);goodix_mem_free((void *)current);goodix_mem_free((void *)amplitudes);goodix_mem_free((void *)flags);
}
