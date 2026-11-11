#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
#include "goodix_spo2.h"
#include "native_spo2_teardown.h"
extern void __aeabi_memclr(void *,size_t);
extern float r1_goodix_spo2_quartic(float,const int32_t *);
extern uint32_t r1_goodix_spo2_assemble(const void *,uint32_t,const void *,void *);
extern uint32_t r1_goodix_spo2_batch(void *,const void *,void *);
extern uint32_t r1_goodix_spo2_accumulate(void *,const void *,void *);
#include "native_spo2_spectral.h"
#include "native_spo2_ratio.h"
#include "native_spo2_summary.h"
#include "native_spo2_quality.h"
#include "native_spo2_transition.h"
#include "native_spo2_infer.h"
#include "native_spo2_output_quality.h"
#include "native_spo2_select.h"
extern void r1_goodix_spo2_confidence(void *,const void *,void *);
#include "native_spo2_output.h"
extern void r1_goodix_spo2_failure(const void *,void *,void *);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static uintptr_t C(void){return (uintptr_t)r1_goodix_native_spo2_context;}
static void *P(uintptr_t p){return (void *)p;}
static void *allocate(uint32_t size){return goodix_mem_malloc((int32_t)size);}
static uint32_t bits(float f){union{float f;uint32_t u;}v={.f=f};return v.u;}
static uint32_t truncate_bits(uint32_t value)
{
    uint32_t fp=__builtin_arm_get_fpscr();
    uint32_t magnitude=value&0x7fffffffu;
    uint32_t exponent=magnitude>>23;
    uint32_t fraction=magnitude&0x7fffffu;
    uint32_t sign=value>>31;
    uint32_t result=0,flags=0;
    if (exponent==255) {
        flags=1;
        if (!fraction) result=sign?0x80000000u:0x7fffffffu;
    } else if (exponent==0) {
        if (fraction) flags=(fp&(1u<<24))?128u:16u;
    } else if (exponent<127) {
        flags=16;
    } else if (exponent>158 || (exponent==158 && (!sign || fraction))) {
        result=sign?0x80000000u:0x7fffffffu;flags=1;
    } else {
        uint32_t significand=fraction|0x800000u;
        if (exponent<150) {
            uint32_t shift=150-exponent;
            result=significand>>shift;
            if (significand&((1u<<shift)-1u)) flags=16;
        } else result=significand<<(exponent-150);
        if (sign) result=0u-result;
    }
    __builtin_arm_set_fpscr(fp|flags);
    return result;
}
/* VCMPE.F32 followed by BGE: unordered also enters the adjustment branch. */
static int less_or_unordered(uint32_t a,uint32_t b)
{
    uint32_t fp=__builtin_arm_get_fpscr();
    if(fp&(1u<<24)){
        if((a&0x7fffffffu) && (a&0x7fffffffu)<0x800000u){a&=0x80000000u;fp|=128;}
        if((b&0x7fffffffu) && (b&0x7fffffffu)<0x800000u){b&=0x80000000u;fp|=128;}
    }
    uint32_t flags;
    if((a&0x7fffffffu)>0x7f800000u || (b&0x7fffffffu)>0x7f800000u){fp|=1;flags=0x30000000u;}
    else if(a==b || !((a|b)&0x7fffffffu))flags=0x60000000u;
    else{
        int less=(a>>31)!=(b>>31)?(a>>31)!=0:((a>>31)?a>b:a<b);
        flags=less?0x80000000u:0x20000000u;
    }
    __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);
    return flags==0x80000000u || flags==0x30000000u;
}
goodix_spo2_ret goodix_spo2_calc(goodix_spo2_input_rawdata *raw,goodix_spo2_result *result)
{
    uintptr_t context=C();
    if(!context)return (goodix_spo2_ret)7;
    uintptr_t descriptor=context+12;
    S(context,0,W(context,0)+1u);
    uint32_t assembled[7];__aeabi_memclr(assembled,sizeof(assembled));
    assembled[2]=(uint32_t)(uintptr_t)allocate(W(descriptor,0)*24u);
    uint32_t status=r1_goodix_spo2_assemble(raw,W(C(),0),P(descriptor),assembled);
    if(!status){
        status=r1_goodix_spo2_batch(assembled,P(descriptor),P(C()+108));
        goodix_mem_free(P(assembled[2]));
    }
    if(status){r1_goodix_spo2_failure(P(descriptor),P(C()+168),result);return (goodix_spo2_ret)status;}
    context=C();S(context,4,W(context,4)+1u);
    status=r1_goodix_spo2_accumulate(P(context+108),P(descriptor),P(context+136));
    if(status)return (goodix_spo2_ret)status;
    context=C();S(context,8,W(context,4)/25u);
    r1_goodix_spo2_spectral(P(context+136),P(descriptor));
    context=C();r1_goodix_spo2_ratio(P(context+136),W(context,8),P(descriptor));
    uint32_t summary[3]={0,0,0};
    summary[2]=(uint32_t)(uintptr_t)allocate(W(descriptor,0)*44u);
    context=C();r1_goodix_spo2_summary(P(descriptor),P(context+136),W(context,8),summary);
    context=C();r1_goodix_spo2_quality(P(descriptor),P(context+136),W(context,8),summary);
    context=C();r1_goodix_spo2_transition(P(context+172),summary,P(descriptor),P(context+168));
    void *model=P(C()+176);
    void *inference=allocate(4);float *adjusted=allocate(4);
    context=C();uint32_t inference_status=r1_goodix_spo2_infer(P(context+136),P(descriptor),model,inference,P(context+172));
    float value;
    if(W(descriptor,56)==1){
        volatile float threshold=(float)W(descriptor,60);
        if(less_or_unordered(W(summary[2],4),bits(threshold))){
            value=r1_goodix_spo2_quartic(*(volatile float *)inference,(const int32_t *)descriptor);
            *adjusted=value;
            if(bits(value)+0xbd4bffffu<0xc0000u){value+=1.0f;*adjusted=value;}
            if(bits(value)+0xbd41ffffu<0x3ffffu && (int32_t)truncate_bits(W(summary[2],4))%3==2)value+=1.0f;
            else if(bits(value)+0xbd3e0000u<=0x40000u && (int32_t)truncate_bits(W(summary[2],4))%5==0)value-=1.0f;
            else if(bits(value)+0xbd3e0000u<=0x40000u && (int32_t)truncate_bits(W(summary[2],4))%5==1)value+=1.0f;
            *adjusted=value;
            goto done;
        }
    }
    value=r1_goodix_spo2_quartic(*(volatile float *)inference,(const int32_t *)descriptor);*adjusted=value;
done:
    r1_goodix_spo2_output_quality(P(descriptor),summary,adjusted,P(C()+168));
    void *selected=allocate(4);void *valid=allocate(1);
    context=C();r1_goodix_spo2_select(P(descriptor),P(context+168),W(context,8),selected,valid);
    context=C();r1_goodix_spo2_confidence(P(context+136),P(descriptor),P(context+208));
    context=C();r1_goodix_spo2_output(P(descriptor),inference,selected,valid,P(summary[2]),P(context+208),P(context+168),result);
    goodix_mem_free(P(summary[2]));goodix_mem_free(inference);goodix_mem_free(adjusted);goodix_mem_free(selected);goodix_mem_free(valid);
    return (goodix_spo2_ret)inference_status;
}
