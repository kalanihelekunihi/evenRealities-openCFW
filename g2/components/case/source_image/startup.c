/* SPDX-License-Identifier: MIT */
#include <stdint.h>

extern uint8_t __stack_top;
extern uint8_t __data_load;
extern uint8_t __data_start;
extern uint8_t __data_end;
extern uint8_t __bss_start;
extern uint8_t __bss_end;

void Reset_Handler(void);
void Default_Handler(void);
void HardFault_Handler(void);

typedef void (*open_cfw_case_vector)(void);

__attribute__((section(".vectors"), used))
open_cfw_case_vector const open_cfw_case_vectors[46] = {
    (open_cfw_case_vector)(void *)&__stack_top,
    Reset_Handler, Default_Handler, HardFault_Handler,
    0, 0, 0, 0, 0, 0, 0, Default_Handler, 0, 0,
    Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler,
};

static void wait_for_interrupt(void)
{
    __asm volatile("wfi");
}

void Reset_Handler(void)
{
    uint8_t *source = &__data_load;
    uint8_t *destination;
    for (destination = &__data_start; destination < &__data_end;)
        *destination++ = *source++;
    for (destination = &__bss_start; destination < &__bss_end;)
        *destination++ = 0U;

    /* Board routing is evidence-locked; keep the source image inert. */
    for (;;) wait_for_interrupt();
}

void Default_Handler(void)
{
    for (;;) wait_for_interrupt();
}

void HardFault_Handler(void)
{
    for (;;) {
        __asm volatile("cpsid i");
        wait_for_interrupt();
    }
}
