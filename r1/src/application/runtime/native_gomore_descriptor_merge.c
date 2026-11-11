#include <stdint.h>
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
struct __attribute__((packed,may_alias)) merge_word { uint32_t value; };
static volatile struct merge_word *word(uint32_t address)
{ return (volatile struct merge_word *)(uintptr_t)address; }
static float mean(uint32_t address)
{ return *(const volatile float *)(uintptr_t)address; }
uint32_t r1_gomore_interval_descriptor_merge_native(uint32_t output,uint32_t initial,
        int32_t unused,uint32_t bypass,uint32_t previous,volatile void *addition_pointer,int32_t profile)
{
    (void)unused;
    uint32_t addition=(uint32_t)(uintptr_t)addition_pointer;
    __aeabi_memclr((void *)(uintptr_t)output,40);
    *(volatile uint8_t *)(uintptr_t)(output+36u)=3;
    word(output)->value=initial;
    *(volatile uint8_t *)(uintptr_t)(output+37u)=(uint8_t)profile;
    if (bypass) return 3;
    word(output)->value=word(previous)->value;
    const uint8_t offsets[5]={8,20,12,16,24};
    for (uint32_t i=0;i<5;i++) {
        uint32_t offset=offsets[i];
        uint32_t first=word(previous+offset)->value;
        uint32_t second=word(addition+offset)->value;
        word(output+offset)->value=first+second;
    }
    uint32_t first_count=word(previous+32u)->value;
    uint32_t second_count=word(addition+32u)->value;
    uint32_t total=first_count+second_count;
    if (total && !(total&UINT32_C(0x80000000))) {
        word(output+32u)->value=total;
        uint32_t count_bits=word(previous+32u)->value;
        float first_mean=mean(previous+28u);
        float second_mean=mean(addition+28u);
        float count=(float)(int32_t)count_bits;
        float first_product=count*first_mean;
        float next_count=(float)(int32_t)word(addition+32u)->value;
        float second_product=next_count*second_mean;
        float numerator=first_product+second_product;
        float denominator=(float)(int32_t)total;
        *(volatile float *)(uintptr_t)(output+28u)=numerator/denominator;
    }
    return total;
}
