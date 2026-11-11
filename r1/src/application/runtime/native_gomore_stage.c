#include <stdint.h>
#include <stddef.h>
#include <string.h>
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_gomore_packed_sleep_consume_native(uint32_t,uint32_t,volatile void *,volatile uint32_t *,volatile void *);

/* Native 0x726c4 stages the entire 32-byte input and forwards all five
 * arguments without changing the consumer's return value. */
uint32_t r1_gomore_packed_sleep_output_native(uint32_t context,uint32_t state,
        volatile void *record,volatile uint32_t *count,volatile void *workspace)
{
    _Alignas(8) volatile uint8_t staged[32];
    __aeabi_memclr((void *)staged,32);
    memcpy((void *)staged,(const void *)record,32);
    return r1_gomore_packed_sleep_consume_native(context,state,staged,count,workspace);
}

/* Native 0x6476c stores a full word and preserves its incoming R0 value. */
uint32_t r1_gomore_set_second_word_native(volatile uint32_t *pair,uint32_t value)
{
    pair[1]=value;
    return (uint32_t)(uintptr_t)pair;
}
