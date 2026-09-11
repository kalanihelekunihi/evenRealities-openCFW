/*
 * SPDX-License-Identifier: MIT
 *
 * Cortex-M0+ startup for the source-built CY8C4046FNI Touch image.
 *
 * The vector table below is built from the named, documented PSoC 4000T
 * NVIC configuration in psoc4000t_nvic.h: every populated slot states which
 * silicon IRQ it is by name instead of by unexplained array position. See
 * that header for why the slot *assignment* is public configuration, not a
 * hardware blocker. No board register is accessed by any handler here;
 * runtime peripheral MMIO behavior stays hardware-blocked pending physical
 * qualification (components/touch/source_image/README.md).
 */
#include <stdint.h>

#include "psoc4000t_nvic.h"

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
open_cfw_touch_vector const
open_cfw_touch_vectors[OPEN_CFW_TOUCH_VECTOR_TABLE_LENGTH] = {
    /* ARMv6-M fixed core exception vectors (indices 0-15). */
    [0] = (open_cfw_touch_vector)(void *)&__stack_top,
    [1] = Reset_Handler,
    [2] = Default_Handler,  /* NMI: not asserted by this part */
    [3] = HardFault_Handler,
    /* 4-10 reserved by the architecture, must read as zero */
    [11] = Default_Handler, /* SVCall: unused, no RTOS on this image */
    /* 12-13 reserved by the architecture, must read as zero */
    [14] = Default_Handler, /* PendSV: unused, no RTOS on this image */
    [15] = SysTick_Handler,

    /* PSoC 4000T external IRQs (see psoc4000t_nvic.h). Named slots not
     * listed here default to zero per the C initializer rule for indices
     * without a designator, which is the correct "unimplemented on this
     * silicon" value for this exact NVIC (none beyond IRQ12 exist). */
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_IOSS0)]    = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_IOSS1)]    = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_IOSS2)]    = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_IOSS3)]    = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_IOSS4)]    = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_SRSS_WDT)] = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_SCB0)]     = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_SCB1)]     = SCB1_IRQHandler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_MSCLP_LP)] = MSCLP_LP_IRQHandler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_SPCIF)]    = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_MSCLP)]    = MSCLP_IRQHandler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_TCPWM0)]   = Default_Handler,
    [OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_TCPWM1)]   = Default_Handler,
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
    /*
     * Vector assignment (PSoC 4000T IRQ7) is explicit, documented silicon
     * configuration -- see psoc4000t_nvic.h. Servicing the SCB1 I2C shift
     * register still requires a physical part and stays hardware-blocked.
     */
}

void MSCLP_LP_IRQHandler(void)
{
    /*
     * Vector assignment (PSoC 4000T IRQ8) is explicit, documented silicon
     * configuration -- see psoc4000t_nvic.h. Servicing MSCLP low-power wake
     * still requires a physical part and stays hardware-blocked.
     */
}

void MSCLP_IRQHandler(void)
{
    /*
     * Vector assignment (PSoC 4000T IRQ10) is explicit, documented silicon
     * configuration -- see psoc4000t_nvic.h. Draining an MSCLP CapSense
     * scan-complete result still requires a physical part and stays
     * hardware-blocked.
     */
}
