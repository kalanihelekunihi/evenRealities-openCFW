#include <stdint.h>
#include <stddef.h>
extern uint64_t r1_signed32_to_binary64_bits(uint32_t);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
/* One owner for the30 contiguous nominal TIA words initialized at20007d10.
 * Reserved gain codes retain the native read of surrounding physical SRAM;
 * they do not create duplicate ownership of neighboring state. */
volatile uint32_t r1_goodix_nominal_tia_gain_words[30]
__attribute__((section(".r1.goodix.nominal.tia.gains"),aligned(4)))={
10000,25000,50000,75000,100000,250000,500000,750000,1000000,1250000,1500000,1750000,2000000,
7812,15625,31250,62500,125000,250000,500000,1000000,2000000,
100000,200000,380000,700000,1000000,1480000,1960000,2440000};
static uint32_t word(uintptr_t p,uint32_t offset){return *(const volatile uint32_t *)(p+offset);}
static uint8_t byte(uintptr_t p,uint32_t offset){return *(const volatile uint8_t *)(p+offset);}
static uint32_t left(uint32_t value,uint32_t n){return n<32?value<<n:0;}
static uint32_t arithmetic_right(uint32_t value,uint32_t n)
{
    if(!n)return value;
    if(n>=32)return value>>31?0xffffffffu:0;
    return (value>>n)|((value>>31)?(0xffffffffu<<(32u-n)):0);
}
static uint32_t float_bits(float value){union{float f;uint32_t u;}v={.f=value};return v.u;}
static void store_bits(uintptr_t out,uint32_t value){union{float f;uint32_t u;}v={.u=value};*(volatile float *)out=v.f;}
static uint32_t gain_word(uint32_t chip,uint32_t gain)
{
    uint32_t index=gain+(chip==1?0:chip==2?13:22);
    if(index<30)return r1_goodix_nominal_tia_gain_words[index];
    return *(const volatile uint32_t *)(uintptr_t)(0x20007d10u+index*4u);
}
void r1_goodix_spo2_decode(const void *input,uint32_t channel,uint32_t group,void *output)
{
    uintptr_t raw=(uintptr_t)input,out=(uintptr_t)output;
    uint32_t type=byte(raw,51);
    if(type!=0 && type!=1)return;
    uint32_t bit_count=type?0:byte(raw,49);
    uint32_t channels=byte(raw,4);
    int32_t signed_group=(int32_t)(group&0x7fffu)-(int32_t)(group&0x8000u);
    uint32_t index=channel+(uint32_t)(signed_group*(int32_t)channels);
    uint32_t value=word(word(raw,12),index*4u);
    if(!type){
        uint32_t mask=left(1,bit_count>17?bit_count-1:bit_count)-1u;
        value=arithmetic_right(value&mask,bit_count>17?bit_count-17:0);
    }
    float first=(float)(int32_t)value;
    *(volatile float *)out=first;
    uint32_t drive=*(const volatile uint16_t *)((uintptr_t)word(raw,20)+index*2u);
    if(type){
        if(drive){float intermediate=first/1000.0f;*(volatile float *)(out+4)=intermediate/(float)drive;}
        else store_bits(out+4,0);
        return;
    }
    uint32_t chip=byte(raw,50),gain=0;
    if(chip<=2)gain=gain_word(chip,byte(word(raw,16),index));
    if(!gain || !drive){store_bits(out+4,0);return;}
    uint64_t drive64=r1_signed32_to_binary64_bits(drive);
    uint64_t gain64=r1_signed32_to_binary64_bits(gain);
    uint64_t result;
    if(!chip){
        float scaled=*(const volatile float *)out;
        scaled*=2.0f;scaled*=800.0f;scaled*=1000.0f;
        result=r1_binary32_to_binary64_bits(float_bits(scaled));
        result=r1_format_double_divide_bits(result,UINT64_C(0x4100000000000000));
        result=r1_format_double_multiply_bits(result,UINT64_C(0x408f400000000000));
        result=r1_format_double_divide_bits(result,gain64);
        result=r1_format_double_divide_bits(result,drive64);
    }else{
        result=r1_binary32_to_binary64_bits(float_bits(*(const volatile float *)out));
        result=r1_format_double_multiply_bits(result,UINT64_C(0x3ffccccccccccccd));
        result=r1_format_double_divide_bits(result,UINT64_C(0x4100000000000000));
        result=r1_format_double_divide_bits(result,gain64);
        result=r1_format_double_divide_bits(result,drive64);
        result=r1_format_double_multiply_bits(result,UINT64_C(0x41cdcd6500000000));
    }
    store_bits(out+4,r1_log_double_to_float_bits(result));
}
