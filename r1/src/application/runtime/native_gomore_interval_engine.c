#include <stdint.h>
#include <stddef.h>
#include <string.h>
extern uint32_t r1_gomore_set_second_word_native(volatile uint32_t *,uint32_t);
extern uint32_t r1_gomore_sleep_interval_compose_native(volatile void *,uint32_t,uint32_t,uint32_t,uint32_t,volatile void *,volatile void *,uint32_t,uint32_t);
extern uint32_t r1_gomore_interval_descriptor_merge_native(uint32_t,uint32_t,int32_t,uint32_t,uint32_t,volatile void *,int32_t);
struct __attribute__((packed,may_alias)) engine_word { uint32_t value; };
struct __attribute__((packed,may_alias)) engine_half { int16_t value; };
static volatile struct engine_word *word(uint32_t address)
{ return (volatile struct engine_word *)(uintptr_t)address; }
static volatile uint8_t *byte(uint32_t address)
{ return (volatile uint8_t *)(uintptr_t)address; }

uint32_t r1_gomore_sleep_interval_run_native(uint32_t context,uint32_t now,
        uint32_t timezone,uint32_t mode,volatile void *output)
{
    *byte((uint32_t)(uintptr_t)output+26u)=0;
    if (!*byte(context+184u)) return 64;
    _Alignas(8) volatile uint8_t controls[8]={0,3,5,0,0,0,0,0};
    _Alignas(8) volatile uint8_t source[40];
    _Alignas(8) volatile uint8_t candidate[32];
    (void)r1_gomore_set_second_word_native((volatile uint32_t *)(uintptr_t)(context+192u),word(now)->value);
    memcpy((void *)source,(const void *)(uintptr_t)(context+192u),40);
    (void)r1_gomore_sleep_interval_compose_native(candidate,context,context+272u,timezone,mode,controls,source,context+232u,context+304u);
    uint32_t minimum=word(context+172u)->value;
    uint32_t start=((volatile struct engine_word *)candidate)->value;
    uint32_t difference=minimum-start;
    /* Native BGE compares the wrapped difference as signed. */
    if (minimum>start && (difference>=UINT32_C(0x80000000) || difference<900u)) {
        ((volatile struct engine_word *)candidate)->value=minimum;
        uint32_t end=((volatile struct engine_word *)(candidate+4))->value;
        ((volatile struct engine_word *)(candidate+4))->value=minimum+((end-minimum)/30u)*30u;
    }
    if (candidate[26]&8u)
        memcpy((void *)(uintptr_t)(context+272u),(const void *)candidate,32);
    int32_t auxiliary=(int8_t)controls[1];
    uint32_t flags=candidate[26]&8u;
    int32_t zone=((volatile struct engine_half *)(uintptr_t)timezone)->value;
    uint32_t current=word(now)->value;
    (void)r1_gomore_interval_descriptor_merge_native(context+192u,current,zone,flags,context+232u,source,auxiliary);
    memcpy((void *)output,(const void *)candidate,32);
    uint32_t policy=word(context+312u)->value;
    uint32_t first=word(policy+2u)->value;
    word(context+304u)->value=first;
    uint32_t second=word(policy+6u)->value;
    word(context+308u)->value=second;
    controls[0]=0;
    uint32_t low=((volatile struct engine_word *)controls)->value;
    uint32_t high=((volatile struct engine_word *)(controls+4))->value;
    word(context+184u)->value=low;
    word(context+188u)->value=high;
    return 0;
}
