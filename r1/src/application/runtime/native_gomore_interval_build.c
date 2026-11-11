#include <stdint.h>
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
extern void *r1_native_memory_move(void *,const void *,size_t);
extern uint32_t r1_gomore_epoch_to_civil_native(uint32_t,volatile void *);
struct __attribute__((packed,may_alias)) build_word { uint32_t value; };
struct __attribute__((packed,may_alias)) build_half { int16_t value; };
static volatile struct build_word *word(uint32_t a)
{ return (volatile struct build_word *)(uintptr_t)a; }
static uint8_t byte(uint32_t a)
{ return *(const volatile uint8_t *)(uintptr_t)a; }
/* GCC strict FP emits the native signaling VCMPE/VMRS comparison. */
__attribute__((noinline,noclone)) static uint32_t history_greater(uint32_t address,uint32_t bits)
{
    union { uint32_t bits;float f; } threshold;
    threshold.bits=bits;
    return *(const volatile float *)(uintptr_t)address > threshold.f;
}
uint32_t r1_gomore_sleep_interval_build_native(volatile void *output,
        uint32_t context,uint32_t mode,uint32_t stored,uint32_t timezone,
        volatile void *controls_pointer,volatile void *source_pointer,uint32_t unused_aggregation,uint32_t policy)
{
    (void)unused_aggregation;
    uint32_t controls=(uint32_t)(uintptr_t)controls_pointer;
    uint32_t source=(uint32_t)(uintptr_t)source_pointer;
    _Alignas(8) volatile uint8_t result[32];
    __aeabi_memclr((void *)result,32);
    result[26]=4;
    uint32_t preceding=byte(source+38u);
    uint32_t source_start=word(source)->value;
    uint32_t adjusted=source_start+preceding*60u;
    ((volatile struct build_word *)(result+8))->value=adjusted;
    uint32_t source_end=word(source+4u)->value;
    ((volatile struct build_word *)(result+12))->value=source_end;
    uint32_t start=adjusted;
    if (byte(source+37u)==2 && !byte(policy+4u)) start=word(source)->value;
    uint32_t clamp=word(context+172u)->value;
    if (clamp && clamp>start) start=clamp;
    ((volatile struct build_word *)result)->value=start;
    uint32_t end=source_end;
    if (mode!=1 && !byte(policy+4u)) {
        uint32_t shift=word(controls+4u)->value;
        if (shift) end+=shift*60u;
        else {
            uint32_t threshold=byte(context+182u)==1 ? UINT32_C(0x3f59999a) : UINT32_C(0x3f333333);
            uint32_t count=0;
            for (uint32_t i=0;i<15;i++) {
                uint32_t t=source_end-1u-i*60u;
                uint32_t minutes=t/60u;
                uint32_t slot=t%60u==59 ? minutes%15u : minutes%15u==0 ? 14u : minutes%15u-1u;
                if (history_greater(context+slot*4u,threshold)) break;
                count++;
            }
            end-=count*60u;
        }
    }
    if (end<start) end=start;
    clamp=word(context+164u)->value;
    if (clamp && clamp<end) end=clamp;
    ((volatile struct build_word *)(result+4))->value=end;
    ((volatile struct build_word *)(result+16))->value=word(stored+4u)->value;
    ((volatile struct build_word *)(result+20))->value=start;
    uint32_t duration=(end-start)/60u;
    int32_t minimum=((const volatile struct build_half *)(uintptr_t)policy)->value;
    int32_t zone=((const volatile struct build_half *)(uintptr_t)timezone)->value;
    _Alignas(4) volatile uint8_t civil[13];
    (void)r1_gomore_epoch_to_civil_native(start+(uint32_t)(zone*60),civil);
    uint32_t hour=civil[10];
    uint32_t limit=180;
    if (hour>=byte(policy+6u) || hour<byte(policy+7u)) limit=20;
    result[27]=byte(controls+2u);
    int32_t metric=(int32_t)word(source+28u)->value;
    if (metric>=INT32_C(0x42c80000)) result[28]=1;
    else {
        uint32_t excessive=0;
        if (duration>=900) {
            uint32_t count=word(source+8u)->value;
            union { float f; int32_t bits; } average;
            if (count) {
                int32_t sum=(int32_t)word(source+24u)->value;
                average.f=(float)sum/(float)(int32_t)count;
            } else average.f=0;
            excessive=average.bits>INT32_C(0x3e570a3d);
        }
        if (excessive) result[28]=2;
        else if (duration>=limit) { result[26]|=24;result[28]=0; }
        else if ((int32_t)duration>=minimum && hour<byte(policy+6u) && hour>=byte(policy+7u)) {
            result[26]|=8;result[28]=3;
        } else result[28]=4;
    }
    return (uint32_t)(uintptr_t)r1_native_memory_move((void *)output,(const void *)result,32);
}
