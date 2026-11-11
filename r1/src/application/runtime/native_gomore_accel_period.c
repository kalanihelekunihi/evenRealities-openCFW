#include <stdint.h>
#include <stddef.h>
#include "native_gomore_accel_crossing_period.h"
#include "native_gomore_accel_period_helpers.h"
#include "native_float_to_signed.h"
#include "native_float_bits.h"
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
extern void __aeabi_memclr(void *,uint32_t);
extern float r1_native_sqrtf(float);
typedef int32_t (*comparator)(const void *,const void *);
extern void r1_native_qsort(uint8_t *,uint32_t,uint32_t,comparator);
#define FP __attribute__((noinline,noclone))
static FP float convert(uint32_t a) { return (float)(int32_t)a; }
static FP float multiply(float a,float b) { return a*b; }
static FP float divide(float a,float b) { return a/b; }
static FP uint32_t less(float a,float b) { volatile uint32_t result=a<b;return result; }
static uint32_t bits(float a) { union {float f;uint32_t u;} v={.f=a};return v.u; }
static float value(uint32_t a) { union {uint32_t u;float f;} v={.u=a};return v.f; }
static uint32_t signed_div(uint32_t a,uint32_t b)
{
    if(b==0)return 0;
    if(a==0x80000000u && b==UINT32_MAX)return a;
    return (uint32_t)((int32_t)a/(int32_t)b);
}
/* Fields through raw_max retain the native published scratch layout. The tail
   replaces private save slots with C state and the four live native argument words. */
typedef struct {
    uint32_t cursor,sample,current,scale,short_half,long_half,previous_regime,regime;
    uint32_t selected_index,minimum_value,maximum_value,minimum_index,maximum_index;
    uint32_t interval;float estimate;uint32_t initialized,maximum_pair,minimum_pair;
    uint32_t output_history[4],input_history[4],ring[20],endpoint;
    uint8_t intervals[80];uint32_t short_length,long_length,raw_min,raw_max;
    float minimum,maximum,a,b,c;uint32_t long_sum,short_sum;
    uint32_t input,output,mode,baseline;
} period_frame;
_Static_assert(offsetof(period_frame,interval)==0x34,"interval position");
_Static_assert(offsetof(period_frame,output_history)==0x48,"output history position");
_Static_assert(offsetof(period_frame,input_history)==0x58,"input history position");
_Static_assert(offsetof(period_frame,ring)==0x68,"rolling history position");
_Static_assert(offsetof(period_frame,intervals)==0xbc,"interval byte history position");
_Static_assert(offsetof(period_frame,short_length)==0x10c,"native byte overread position");
_Static_assert(offsetof(period_frame,input)==0x138 && sizeof(period_frame)==0x148,"argument positions");
#define ADDRESS(member) ((uint32_t)(uintptr_t)&f.member)
static uint32_t normalized(volatile period_frame *f,uint32_t index)
{
    if(f->scale==0)return 0;
    uint32_t input=*(volatile uint16_t *)(uintptr_t)(f->input+index*2u);
    return signed_div((input-f->baseline)*1000u,f->scale);
}
int32_t r1_gomore_accel_u8_compare_native(const void *a,const void *b)
{
    uint32_t x=*(volatile const uint8_t *)a,y=*(volatile const uint8_t *)b;
    if(x>y)return 1;
    if(x<y)return -1;
    return 0;
}
uint32_t r1_gomore_accel_crossing_period_native(float seed __attribute__((unused)),
                                              uint32_t input,uint32_t output,
                                              uint32_t mode,uint32_t baseline)
{
    _Alignas(8) volatile period_frame f;
    uint32_t selected_value=0;
    f.input=input;f.output=output;f.mode=mode;f.baseline=baseline;
    f.long_length=f.mode==1?20u:12u;f.short_length=f.mode==1?10u:6u;
    __aeabi_memclr((void *)(uintptr_t)ADDRESS(intervals),80);f.endpoint=0;
    __aeabi_memclr((void *)(uintptr_t)ADDRESS(ring),80);
    for(uint32_t i=0;i<4;i++)f.input_history[i]=0;
    for(uint32_t i=0;i<4;i++)f.output_history[i]=0;
    f.minimum_pair=0;f.maximum_pair=0;f.initialized=0;f.estimate=-1.0f;
    f.minimum=f.mode==1?20.0f:6.25f;f.maximum=f.mode==1?50.0f:25.0f;
    f.interval=UINT32_MAX;f.maximum_index=UINT32_MAX;f.minimum_index=UINT32_MAX;
    f.maximum_value=UINT32_MAX;f.minimum_value=UINT32_MAX;
    f.long_sum=0;f.short_sum=0;selected_value=0;f.selected_index=0;
    f.previous_regime=0;f.cursor=10;
    f.long_half=f.long_length/2u;f.short_half=f.short_length/2u;
    uint32_t sum=0;
    for(uint32_t i=0;i<200;i++) {
        uint32_t x=*(volatile uint16_t *)(uintptr_t)(f.input+i*2u)-f.baseline;
        sum+=x*x;
    }
    f.a=convert(signed_div(sum,200));f.a=r1_native_sqrtf(f.a);
    f.scale=r1_native_float_to_signed32(f.a);
    uint32_t input_index=0,tail=0,count=0;
    f.sample=0;
    do {
        if(f.sample==0) {
            f.endpoint=r1_gomore_accel_iir4_native(normalized(&f,input_index),ADDRESS(input_history),ADDRESS(output_history),f.mode);
            input_index=(input_index+1u)&255u;
            for(uint32_t i=0;i<20;i++) {
                if(i<=f.cursor)f.ring[i]=f.endpoint;
                else {
                    f.ring[i]=r1_gomore_accel_iir4_native(normalized(&f,input_index),ADDRESS(input_history),ADDRESS(output_history),f.mode);
                    input_index=(input_index+1u)&255u;
                }
            }
            for(int32_t i=-(int32_t)f.long_half;i<(int32_t)(f.long_length-f.long_half);i++)f.long_sum+=f.ring[f.cursor+(uint32_t)i];
            for(int32_t i=-(int32_t)f.short_half;i<(int32_t)(f.short_length-f.short_half);i++)f.short_sum+=f.ring[f.cursor+(uint32_t)i];
            tail=19;
        } else {
            uint32_t at=f.cursor-f.long_half;if((int32_t)at<0)at+=20;
            f.long_sum-=f.ring[at];at=f.cursor-f.short_half;if((int32_t)at<0)at+=20;
            f.short_sum-=f.ring[at];tail=tail+1u<20u?tail+1u:0;
            if(input_index<200) {
                f.ring[tail]=r1_gomore_accel_iir4_native(normalized(&f,input_index),ADDRESS(input_history),ADDRESS(output_history),f.mode);
                if(input_index==199)f.endpoint=f.ring[tail];
                input_index=(input_index+1u)&255u;
            } else f.ring[tail]=f.endpoint;
            f.cursor=f.cursor+1u<20u?f.cursor+1u:0;
            at=f.long_length-f.long_half+f.cursor-1u;if((int32_t)at>=20)at-=20;
            f.long_sum+=f.ring[at];at=f.short_length-f.short_half+f.cursor-1u;if((int32_t)at>=20)at-=20;
            f.short_sum+=f.ring[at];
        }
        f.current=f.ring[f.cursor];
        f.regime=(int32_t)signed_div(f.long_sum,f.long_length)<(int32_t)signed_div(f.short_sum,f.short_length);
        if(f.sample==0){selected_value=f.current;f.selected_index=0;}
        else if(f.previous_regime==f.regime) {
            if((f.regime==1 && (int32_t)f.current>(int32_t)selected_value) ||
               (f.regime==0 && (int32_t)f.current<(int32_t)selected_value)) {
                selected_value=f.current;f.selected_index=f.sample&255u;
            }
        } else {
            if(f.previous_regime==1) {
                if((int32_t)f.maximum_index>0) {
                    f.interval=f.selected_index-f.maximum_index;f.raw_max=f.interval;
                    if(f.mode==1) {
                        f.a=value(r1_log_double_to_float_bits(r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(bits(f.minimum)),UINT64_C(0x3fe999999999999a))));
                        f.b=convert(selected_value-f.minimum_value);f.c=convert(f.maximum_value-f.minimum_value);
                        (void)r1_gomore_accel_transition_native(f.a,-1.0f,f.c,f.b,ADDRESS(interval),ADDRESS(maximum_pair),ADDRESS(initialized),ADDRESS(estimate));
                    }
                    ((volatile uint8_t *)&f.maximum_pair)[0]=((volatile uint8_t *)&f.maximum_pair)[1];
                    ((volatile uint8_t *)&f.maximum_pair)[1]=(uint8_t)f.raw_max;
                }
                f.maximum_index=f.selected_index;f.maximum_value=selected_value;
            } else {
                if((int32_t)f.minimum_index>0) {
                    f.interval=f.selected_index-f.minimum_index;f.raw_min=f.interval;
                    if(f.mode==1) {
                        f.a=value(r1_log_double_to_float_bits(r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(bits(f.minimum)),UINT64_C(0x3fe999999999999a))));
                        f.b=convert(f.maximum_value-selected_value);f.c=convert(f.maximum_value-f.minimum_value);
                        (void)r1_gomore_accel_transition_native(f.a,-1.0f,f.c,f.b,ADDRESS(interval),ADDRESS(minimum_pair),ADDRESS(initialized),ADDRESS(estimate));
                    }
                    ((volatile uint8_t *)&f.minimum_pair)[0]=((volatile uint8_t *)&f.minimum_pair)[1];
                    ((volatile uint8_t *)&f.minimum_pair)[1]=(uint8_t)f.raw_min;
                }
                f.minimum_index=f.selected_index;f.minimum_value=selected_value;
            }
            f.a=convert(f.interval);
            if(!less(f.maximum,f.a)) {
                f.a=convert(f.interval);
                if(!less(f.a,f.minimum) && count<80)f.intervals[count++]=(uint8_t)f.interval;
            }
            selected_value=f.current;f.selected_index=f.sample&255u;
        }
        f.previous_regime=f.regime;f.sample++;
    } while((int32_t)f.sample<200);
    if(((volatile uint8_t *)&f.initialized)[0]!=0 && count>2) {
        r1_native_qsort((uint8_t *)(uintptr_t)ADDRESS(intervals),count,1,r1_gomore_accel_u8_compare_native);
        f.a=multiply(f.estimate,70.0f);int32_t cutoff=(int16_t)r1_native_float_to_signed32(f.a);
        uint32_t remove=0;
        while((int32_t)(((volatile uint8_t *)&f)[0xbc+remove]*100u)<cutoff && (int32_t)remove<(int32_t)count)remove++;
        for(uint32_t i=0;(int32_t)i<(int32_t)(count-remove);i++)f.intervals[i]=f.intervals[i+remove];
        count=(count-remove)&255u;
    }
    f.maximum=0.0f;*(volatile float *)(uintptr_t)f.output=f.maximum;
    if(count>2) {
        r1_native_qsort((uint8_t *)(uintptr_t)ADDRESS(intervals),count,1,r1_gomore_accel_u8_compare_native);
        uint32_t median=count&1u ? f.intervals[(count-1u)/2u] : (f.intervals[count/2u-1u]+f.intervals[count/2u])/2u;
        f.minimum=convert(median);
        uint64_t number=r1_unsigned32_to_binary64_bits(count);f.long_sum=(uint32_t)number;f.short_sum=(uint32_t)(number>>32);
        f.raw_min=r1_binary64_to_unsigned32_bits(r1_format_double_multiply_bits(number,UINT64_C(0x3fd0000000000000)));
        number=((uint64_t)f.short_sum<<32)|f.long_sum;
        f.raw_max=r1_binary64_to_unsigned32_bits(r1_format_double_multiply_bits(number,UINT64_C(0x3fe8000000000000)));
        f.a=convert((uint32_t)f.intervals[f.raw_max]-(uint32_t)f.intervals[f.raw_min]);f.a=divide(f.a,f.minimum);
        if((int32_t)bits(f.a)<0x3e99999a) {
            uint32_t total=0;
            for(uint32_t i=f.raw_min;(int32_t)i<=(int32_t)f.raw_max;i++)total=(uint32_t)(int32_t)(int16_t)(total+f.intervals[i]);
            uint32_t denominator=f.raw_max-f.raw_min+1u;
            if(denominator!=0){f.a=convert(denominator);f.b=convert(total);f.maximum=divide(f.b,f.a);}
            f.a=divide(25.0f,f.maximum);
        } else f.a=divide(25.0f,f.minimum);
        f.a=multiply(f.a,60.0f);if(f.mode==1)f.a=multiply(f.a,2.0f);
        *(volatile float *)(uintptr_t)f.output=f.a;
    }
    return 0;
}
