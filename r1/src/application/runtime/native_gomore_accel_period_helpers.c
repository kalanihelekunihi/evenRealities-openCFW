#include "native_gomore_accel_period_helpers.h"
#include "native_float_bits.h"
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
#define FP __attribute__((noinline,noclone))
static uint32_t word(uint32_t at) { return *(volatile uint32_t *)(uintptr_t)at; }
static uint32_t byte(uint32_t at) { return *(volatile uint8_t *)(uintptr_t)at; }
static void put_word(uint32_t at,uint32_t value) { *(volatile uint32_t *)(uintptr_t)at=value; }
static void put_byte(uint32_t at,uint32_t value) { *(volatile uint8_t *)(uintptr_t)at=(uint8_t)value; }
static uint32_t bits(float value) { union {float f;uint32_t u;} v={.f=value};return v.u; }
static FP float convert(uint32_t value) { return (float)(int32_t)value; }
static FP float divide(float a,float b) { return a/b; }
static FP uint32_t greater(float a,float b) { volatile uint32_t result=a>b;return result; }
static FP uint32_t equal_zero(float a) { volatile uint32_t result=a==0.0f;return result; }
static FP uint32_t above_or_unordered(float a,float b) { volatile uint32_t result=a<=b;return !result; }
uint32_t r1_gomore_accel_iir4_native(uint32_t input,uint32_t input_history,
                                   uint32_t output_history,uint32_t profile)
{
    /* Typed integer tables at stock 0xbd294..0xbd2e3, not executable words. */
    static const int32_t feedback[2][5]={{1000,-2595,2746,-1459,347},{1000,-3722,5276,-3374,822}};
    static const int32_t forward[2][5]={{9131,0,-18262,0,9131},{434,0,-869,0,434}};
    uint32_t selected=profile==1u;
    uint32_t accumulated=(uint32_t)forward[selected][0]*input;
    for(uint32_t i=0;i<4;i++) {
        uint32_t before=word(input_history+i*4u);
        accumulated+=before*(uint32_t)forward[selected][i+1u];
        uint32_t after=word(output_history+i*4u);
        accumulated-=after*(uint32_t)feedback[selected][i+1u];
    }
    for(uint32_t i=3;i>0;i--) {
        put_word(input_history+i*4u,word(input_history+(i-1u)*4u));
        put_word(output_history+i*4u,word(output_history+(i-1u)*4u));
    }
    put_word(input_history,input);
    uint32_t result=(uint32_t)((int32_t)accumulated/1000);
    put_word(output_history,result);
    return result;
}
static uint64_t key(uint64_t value)
{ return value>>63 ? value : UINT64_C(0x8000000000000000)-value; }
static uint32_t carry_reverse(uint64_t a,uint64_t b) { return key(b)>=key(a); }
static uint32_t absolute(uint32_t value) { return (int32_t)value<0 ? 0u-value : value; }
uint32_t r1_gomore_accel_transition_native(float target,float unused __attribute__((unused)),
                                         float first,float second,uint32_t interval,
                                         uint32_t pair,uint32_t flag,uint32_t estimate)
{
    uint32_t current=byte(pair+1u),previous=byte(pair);
    uint32_t accumulated=word(interval),sum=accumulated+current;
    uint32_t consistency=accumulated-previous;
    if(byte(flag)!=0) {
        uint64_t total=r1_signed32_to_binary64_bits(sum);
        uint64_t prior=r1_binary32_to_binary64_bits(word(estimate));
        uint64_t low=r1_format_double_multiply_bits(prior,UINT64_C(0x3feccccccccccccd));
        if(carry_reverse(low,total))return (uint32_t)key(low);
        prior=r1_binary32_to_binary64_bits(word(estimate));
        uint64_t high=r1_format_double_multiply_bits(prior,UINT64_C(0x3ff199999999999a));
        if(carry_reverse(total,high))return (uint32_t)key(total);
        uint32_t delta=absolute(consistency);
        if((int32_t)delta>2)return delta;
        put_word(interval,sum);
        uint64_t quarter=r1_format_double_multiply_bits(total,UINT64_C(0x3fd0000000000000));
        prior=r1_binary32_to_binary64_bits(word(estimate));
        uint64_t old=r1_format_double_multiply_bits(prior,UINT64_C(0x3fe8000000000000));
        uint32_t result=r1_log_double_to_float_bits(r1_format_double_add_bits(old,quarter));
        put_word(estimate,result);
        return result;
    }
    float maximum=greater(first,second)?first:second;
    float shape_ratio=0.0f;
    if(!equal_zero(maximum)) {
        uint32_t above=greater(first,second);
        float minimum=above?second:first;
        maximum=above?first:second;
        shape_ratio=divide(minimum,maximum);
    }
    uint32_t integer_max=(int32_t)current>(int32_t)accumulated?current:accumulated;
    float integer_ratio=0.0f;
    if(integer_max!=0) {
        uint32_t minimum=(int32_t)current>(int32_t)accumulated?accumulated:current;
        float low=convert(minimum),high=convert(integer_max);
        integer_ratio=divide(low,high);
    }
    if((int32_t)bits(shape_ratio)>=0x3f19999a && above_or_unordered(convert(accumulated),target))return accumulated;
    uint32_t ratio=bits(integer_ratio);
    if((int32_t)ratio<=0x3f333333)return ratio;
    uint64_t limit=r1_format_double_multiply_bits(r1_binary32_to_binary64_bits(bits(target)),UINT64_C(0x4004000000000000));
    uint64_t total=r1_signed32_to_binary64_bits(sum);
    if(carry_reverse(total,limit))return (uint32_t)key(total);
    uint32_t delta=absolute(consistency);
    if((int32_t)delta>2)return delta;
    put_word(interval,sum);put_byte(flag,1);
    put_word(estimate,bits(convert(sum)));
    return 1;
}
