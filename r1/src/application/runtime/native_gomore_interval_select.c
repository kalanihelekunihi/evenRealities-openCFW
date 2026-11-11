/* Stock 0x72572: select the public 32-byte interval record. */
#include <stdint.h>
#include <stddef.h>

extern void __aeabi_memclr(void *, size_t);
extern void *r1_native_memory_move(void *, const void *, size_t);
extern uint32_t r1_gomore_set_second_word_native(volatile uint32_t *,uint32_t);
extern uint32_t r1_gomore_sleep_interval_compose_native(
    volatile void *,uint32_t,uint32_t,uint32_t,uint32_t,
    volatile void *,volatile void *,uint32_t,uint32_t);

void r1_gomore_sleep_interval_select_native(
    volatile void *output,uint32_t context,uint32_t current_word,uint32_t timezone)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)context;
    _Alignas(8) volatile uint8_t selected[32];
    __aeabi_memclr((void *)selected,sizeof selected);
    if (state[184]!=1u) {
        (void)r1_native_memory_move((void *)selected,
            (const void *)(state+272),sizeof selected);
        (void)r1_native_memory_move((void *)output,
            (const void *)selected,sizeof selected);
        return;
    }

    _Alignas(8) volatile uint8_t source[40];
    _Alignas(8) volatile uint32_t controls[2]={0,0};
    _Alignas(8) volatile uint8_t candidate[32];
    (void)r1_native_memory_move((void *)source,
        (const void *)(state+192),sizeof source);
    (void)r1_gomore_set_second_word_native((volatile uint32_t *)source,
        *(volatile uint32_t *)(uintptr_t)current_word);
    (void)r1_gomore_sleep_interval_compose_native(candidate,
        context,context+272u,timezone,1u,controls,source,
        context+232u,context+304u);
    (void)r1_native_memory_move((void *)selected,
        (const void *)candidate,sizeof selected);
    if ((selected[26]&8u)==0u)
        (void)r1_native_memory_move((void *)output,
            (const void *)(state+272),sizeof selected);
    else
        (void)r1_native_memory_move((void *)output,
            (const void *)selected,sizeof selected);
}
