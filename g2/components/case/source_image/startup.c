/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "board_config.h"

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

/*
 * 16 fixed Cortex-M0+ system vectors (indices 0-15) followed by 30 device
 * IRQ slots (indices 16-45, IRQ0..IRQ29) -- see board_config.h for the
 * evidence behind this shape and behind the individual slots called out
 * below. Every handler here stays Default_Handler/inert: board routing
 * (which physical peripheral instance drives what) is not confirmed by
 * available evidence, so this image must not act as if it were.
 *   index 17 = IRQ1  = PVD    (OPEN_CFW_CASE_IRQ_PVD,    confirmed default upstream)
 *   index 31 = IRQ15 = TIM2   (OPEN_CFW_CASE_IRQ_TIM2,   confirmed default upstream)
 *   index 43 = IRQ27 = USART1 (OPEN_CFW_CASE_IRQ_USART1, confirmed populated upstream)
 */
__attribute__((section(".vectors"), used))
open_cfw_case_vector const open_cfw_case_vectors[OPEN_CFW_CASE_VECTOR_COUNT] = {
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

    /*
     * Board routing is evidence-locked; keep the source image inert.
     * board_config.h names every routing assumption this build makes
     * (vector slots, flash banks, identity windows, assumed peripheral
     * bindings) and marks each CONFIRMED or UNCONFIRMED against
     * docs/research/g2-box-stm32g0-platform-recovery.md. Nothing marked
     * UNCONFIRMED is exercised here.
     */
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
