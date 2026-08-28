/*
 * SPDX-License-Identifier: MIT
 *
 * Cortex-M0+ startup for the source-built CY8C4046FNI Touch image. No board
 * register is accessed before the evidence-locked application boundary.
 */
#include <stdint.h>

extern uint8_t __stack_top;
extern uint8_t __data_load;
extern uint8_t __data_start;
extern uint8_t __data_end;
extern uint8_t __bss_start;
extern uint8_t __bss_end;

int open_cfw_touch_firmware_main(void);

void Reset_Handler(void);
void Default_Handler(void);
void HardFault_Handler(void);
void SysTick_Handler(void);
void SCB1_IRQHandler(void);
void MSCLP_LP_IRQHandler(void);
void MSCLP_IRQHandler(void);

volatile uint32_t open_cfw_touch_hardfault_count;
volatile uint32_t open_cfw_touch_systick_count;

typedef void (*open_cfw_touch_vector)(void);

__attribute__((section(".vectors"), used))
open_cfw_touch_vector const open_cfw_touch_vectors[48] = {
    (open_cfw_touch_vector)(void *)&__stack_top,
    Reset_Handler,
    Default_Handler,
    HardFault_Handler,
    0, 0, 0, 0, 0, 0, 0,
    Default_Handler,
    0, 0,
    Default_Handler,
    SysTick_Handler,
    Default_Handler, Default_Handler, Default_Handler, Default_Handler,
    Default_Handler, Default_Handler, Default_Handler, SCB1_IRQHandler,
    MSCLP_LP_IRQHandler, Default_Handler, MSCLP_IRQHandler,
    Default_Handler, Default_Handler,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
};

static void open_cfw_touch_wait_for_interrupt(void)
{
    __asm volatile("wfi");
}

void Reset_Handler(void)
{
    uint8_t *source = &__data_load;
    uint8_t *destination;

    for (destination = &__data_start; destination < &__data_end;) {
        *destination++ = *source++;
    }
    for (destination = &__bss_start; destination < &__bss_end;) {
        *destination++ = 0U;
    }
    (void)open_cfw_touch_firmware_main();
    for (;;) {
        open_cfw_touch_wait_for_interrupt();
    }
}

void Default_Handler(void)
{
    for (;;) {
        open_cfw_touch_wait_for_interrupt();
    }
}

void HardFault_Handler(void)
{
    ++open_cfw_touch_hardfault_count;
    for (;;) {
        __asm volatile("cpsid i");
        open_cfw_touch_wait_for_interrupt();
    }
}

void SysTick_Handler(void)
{
    ++open_cfw_touch_systick_count;
}

void SCB1_IRQHandler(void)
{
    /* Physical SCB1 routing is deliberately locked pending board evidence. */
}

void MSCLP_LP_IRQHandler(void)
{
    /* Physical MSCLP routing is deliberately locked pending board evidence. */
}

void MSCLP_IRQHandler(void)
{
    /* Physical MSCLP routing is deliberately locked pending board evidence. */
}
