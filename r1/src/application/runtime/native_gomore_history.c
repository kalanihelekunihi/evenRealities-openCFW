#include <stdint.h>
#include <stddef.h>

struct __attribute__((packed,may_alias)) history_word { uint32_t value; };
static uint32_t load(const volatile void *p)
{ return ((const volatile struct history_word *)p)->value; }
static void store(volatile void *p,uint32_t v)
{ ((volatile struct history_word *)p)->value=v; }

uint32_t r1_gomore_mark_history_prefix_native(volatile int8_t *data,int32_t length)
{
    uint32_t marked=0;
    for (int32_t i=0;i<length;i++) {
        int32_t value=data[i];
        if (value==2 || marked>20u) break;
        if (value!=0) { data[i]=2;marked++; }
    }
    return (uint32_t)(uintptr_t)data;
}

uint32_t r1_gomore_shift_marked_history_native(volatile void *output,int32_t shift)
{
    volatile uint8_t *work=output;
    if (shift<=0) return (uint32_t)(uintptr_t)output;
    uint32_t amount=(uint32_t)shift;
    uint32_t index=load(work+16)+amount-1u;
    while ((int32_t)index>=shift) {
        volatile uint8_t *data=(volatile uint8_t *)(uintptr_t)load(work+8);
        uint8_t value=data[index-amount];
        data[index]=value;
        index--;
    }
    for (uint32_t i=0;(int32_t)i<shift;i++) {
        volatile uint8_t *data=(volatile uint8_t *)(uintptr_t)load(work+8);
        data[i]=0;
    }
    uint32_t length=load(work+16)+amount;
    store(work+16,length);
    volatile int8_t *data=(volatile int8_t *)(uintptr_t)load(work+8);
    return r1_gomore_mark_history_prefix_native(data,(int32_t)length);
}
