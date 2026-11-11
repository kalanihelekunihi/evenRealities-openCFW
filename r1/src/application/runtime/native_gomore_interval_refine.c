#include <stdint.h>
#include <stddef.h>
extern void *r1_native_memory_move(void *,const void *,size_t);
struct __attribute__((packed,may_alias)) refine_word { uint32_t value; };
struct __attribute__((packed,may_alias)) refine_half { int16_t value; };
static volatile struct refine_word *word(uint32_t address)
{ return (volatile struct refine_word *)(uintptr_t)address; }
static uint8_t byte(uint32_t address)
{ return *(const volatile uint8_t *)(uintptr_t)address; }
uint32_t r1_gomore_sleep_interval_refine_native(volatile void *output,
        uint32_t unused,uint32_t previous,volatile void *current_pointer,
        uint32_t aggregation,uint32_t policy,uint32_t unused_timezone)
{
    (void)unused;(void)unused_timezone;
    uint32_t current=(uint32_t)(uintptr_t)current_pointer;
    _Alignas(8) volatile uint8_t snapshot[32];
    r1_native_memory_move((void *)snapshot,(const void *)current_pointer,32);
    if (byte(current+26u)&8u) {
        uint32_t end=word(current+4u)->value;
        uint32_t previous_start=word(previous)->value;
        uint32_t span=end-previous_start;
        uint32_t start=word(current)->value;
        uint32_t previous_end=word(previous+4u)->value;
        uint32_t gap=start-previous_end;
        uint32_t count=word(aggregation+8u)->value;
        /* Volatile evaluation preserves FPSCR effects before early statuses. */
        volatile float average=0.0f;
        if (count) {
            int32_t sum=(int32_t)word(aggregation+20u)->value;
            average=(float)sum/(float)(int32_t)count;
        }
        union { float f; int32_t bits; } ratio;
        ratio.f=average;
        if (!(byte(previous+26u)&8u)) snapshot[29]=2;
        else if ((int32_t)span>43200) snapshot[29]=1;
        else {
            int32_t minutes=((const volatile struct refine_half *)(uintptr_t)(policy+2u))->value;
            if ((int32_t)gap>minutes*60) snapshot[29]=3;
            else if ((int32_t)count>=1800 && ratio.bits>INT32_C(0x3ea3d70a) && (int32_t)gap>1800) snapshot[29]=5;
            else {
                ((volatile struct refine_word *)snapshot)->value=previous_start;
                if ((int32_t)span>=10800) snapshot[26]|=16;
                snapshot[29]=0;
            }
        }
    }
    return (uint32_t)(uintptr_t)r1_native_memory_move((void *)output,(const void *)snapshot,32);
}
