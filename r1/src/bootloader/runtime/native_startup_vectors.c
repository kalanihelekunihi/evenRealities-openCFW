/* Copyright (c) 2009-2020 ARM Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 * Original startup modified by Nordic Semiconductor ASA.
 * C translation of the pinned Nordic nRF52840 GCC startup vector and
 * default-handler declarations (SDK 17.1.0). The bootloader reset sequence
 * lives in reset.c. */
#include <stdint.h>

extern uint32_t __StackTop;
extern void Reset_Handler(void);
#if defined(SVCALL_AS_NORMAL_FUNCTION)
extern void r1_bootloader_cordio_irq_forward(void);
#define R1_CORDIO_IRQ(name) r1_bootloader_cordio_irq_forward
#else
#define R1_CORDIO_IRQ(name) name
#endif

/* Match the pinned GCC startup's default 16 KiB stack and 16 KiB heap.
 * nrf_common.ld places these sections and computes __StackLimit/Top. */
uint8_t r1_bootloader_stack[16384]
    __attribute__((section(".stack"), aligned(8), used));
uint8_t r1_bootloader_heap[16384]
    __attribute__((section(".heap"), aligned(8), used));

__attribute__((noreturn)) void Default_Handler(void)
{
    for (;;) { }
}

#define R1_WEAK_HANDLER(name) \
    void name(void) __attribute__((weak, alias("Default_Handler")))

R1_WEAK_HANDLER(NMI_Handler);
R1_WEAK_HANDLER(HardFault_Handler);
R1_WEAK_HANDLER(MemoryManagement_Handler);
R1_WEAK_HANDLER(BusFault_Handler);
R1_WEAK_HANDLER(UsageFault_Handler);
R1_WEAK_HANDLER(SVC_Handler);
R1_WEAK_HANDLER(DebugMon_Handler);
R1_WEAK_HANDLER(PendSV_Handler);
R1_WEAK_HANDLER(SysTick_Handler);
R1_WEAK_HANDLER(POWER_CLOCK_IRQHandler);
R1_WEAK_HANDLER(RADIO_IRQHandler);
R1_WEAK_HANDLER(UARTE0_UART0_IRQHandler);
R1_WEAK_HANDLER(SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0_IRQHandler);
R1_WEAK_HANDLER(SPIM1_SPIS1_TWIM1_TWIS1_SPI1_TWI1_IRQHandler);
R1_WEAK_HANDLER(NFCT_IRQHandler);
R1_WEAK_HANDLER(GPIOTE_IRQHandler);
R1_WEAK_HANDLER(SAADC_IRQHandler);
R1_WEAK_HANDLER(TIMER0_IRQHandler);
R1_WEAK_HANDLER(TIMER1_IRQHandler);
R1_WEAK_HANDLER(TIMER2_IRQHandler);
R1_WEAK_HANDLER(RTC0_IRQHandler);
R1_WEAK_HANDLER(TEMP_IRQHandler);
R1_WEAK_HANDLER(RNG_IRQHandler);
R1_WEAK_HANDLER(ECB_IRQHandler);
R1_WEAK_HANDLER(CCM_AAR_IRQHandler);
R1_WEAK_HANDLER(WDT_IRQHandler);
R1_WEAK_HANDLER(RTC1_IRQHandler);
R1_WEAK_HANDLER(QDEC_IRQHandler);
R1_WEAK_HANDLER(COMP_LPCOMP_IRQHandler);
R1_WEAK_HANDLER(SWI0_EGU0_IRQHandler);
R1_WEAK_HANDLER(SWI1_EGU1_IRQHandler);
R1_WEAK_HANDLER(SWI2_EGU2_IRQHandler);
R1_WEAK_HANDLER(SWI3_EGU3_IRQHandler);
R1_WEAK_HANDLER(SWI4_EGU4_IRQHandler);
R1_WEAK_HANDLER(SWI5_EGU5_IRQHandler);
R1_WEAK_HANDLER(TIMER3_IRQHandler);
R1_WEAK_HANDLER(TIMER4_IRQHandler);
R1_WEAK_HANDLER(PWM0_IRQHandler);
R1_WEAK_HANDLER(PDM_IRQHandler);
R1_WEAK_HANDLER(MWU_IRQHandler);
R1_WEAK_HANDLER(PWM1_IRQHandler);
R1_WEAK_HANDLER(PWM2_IRQHandler);
R1_WEAK_HANDLER(SPIM2_SPIS2_SPI2_IRQHandler);
R1_WEAK_HANDLER(RTC2_IRQHandler);
R1_WEAK_HANDLER(I2S_IRQHandler);
R1_WEAK_HANDLER(FPU_IRQHandler);
R1_WEAK_HANDLER(USBD_IRQHandler);
R1_WEAK_HANDLER(UARTE1_IRQHandler);
R1_WEAK_HANDLER(QSPI_IRQHandler);
R1_WEAK_HANDLER(CRYPTOCELL_IRQHandler);
R1_WEAK_HANDLER(PWM3_IRQHandler);
R1_WEAK_HANDLER(SPIM3_IRQHandler);

#define VECTOR(name) ((uintptr_t)(name))
const uintptr_t __isr_vector[128]
    __attribute__((section(".isr_vector"), aligned(4), used)) = {
    [0] = (uintptr_t)&__StackTop,
    [1] = VECTOR(Reset_Handler),
    [2] = VECTOR(NMI_Handler),
    [3] = VECTOR(HardFault_Handler),
    [4] = VECTOR(MemoryManagement_Handler),
    [5] = VECTOR(BusFault_Handler),
    [6] = VECTOR(UsageFault_Handler),
    [11] = VECTOR(SVC_Handler),
    [12] = VECTOR(DebugMon_Handler),
    [14] = VECTOR(PendSV_Handler),
    [15] = VECTOR(SysTick_Handler),
    [16] = VECTOR(R1_CORDIO_IRQ(POWER_CLOCK_IRQHandler)),
    [17] = VECTOR(R1_CORDIO_IRQ(RADIO_IRQHandler)),
    [18] = VECTOR(UARTE0_UART0_IRQHandler),
    [19] = VECTOR(SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0_IRQHandler),
    [20] = VECTOR(SPIM1_SPIS1_TWIM1_TWIS1_SPI1_TWI1_IRQHandler),
    [21] = VECTOR(NFCT_IRQHandler),
    [22] = VECTOR(GPIOTE_IRQHandler),
    [23] = VECTOR(SAADC_IRQHandler),
    [24] = VECTOR(R1_CORDIO_IRQ(TIMER0_IRQHandler)),
    [25] = VECTOR(R1_CORDIO_IRQ(TIMER1_IRQHandler)),
    [26] = VECTOR(TIMER2_IRQHandler),
    [27] = VECTOR(RTC0_IRQHandler),
    [28] = VECTOR(TEMP_IRQHandler),
    [29] = VECTOR(RNG_IRQHandler),
    [30] = VECTOR(ECB_IRQHandler),
    [31] = VECTOR(R1_CORDIO_IRQ(CCM_AAR_IRQHandler)),
    [32] = VECTOR(WDT_IRQHandler),
    [33] = VECTOR(R1_CORDIO_IRQ(RTC1_IRQHandler)),
    [34] = VECTOR(QDEC_IRQHandler),
    [35] = VECTOR(COMP_LPCOMP_IRQHandler),
    [36] = VECTOR(SWI0_EGU0_IRQHandler),
    [37] = VECTOR(SWI1_EGU1_IRQHandler),
    [38] = VECTOR(SWI2_EGU2_IRQHandler),
    [39] = VECTOR(SWI3_EGU3_IRQHandler),
    [40] = VECTOR(SWI4_EGU4_IRQHandler),
    [41] = VECTOR(SWI5_EGU5_IRQHandler),
    [42] = VECTOR(TIMER3_IRQHandler),
    [43] = VECTOR(TIMER4_IRQHandler),
    [44] = VECTOR(PWM0_IRQHandler),
    [45] = VECTOR(PDM_IRQHandler),
    [48] = VECTOR(MWU_IRQHandler),
    [49] = VECTOR(PWM1_IRQHandler),
    [50] = VECTOR(PWM2_IRQHandler),
    [51] = VECTOR(SPIM2_SPIS2_SPI2_IRQHandler),
    [52] = VECTOR(RTC2_IRQHandler),
    [53] = VECTOR(I2S_IRQHandler),
    [54] = VECTOR(FPU_IRQHandler),
    [55] = VECTOR(USBD_IRQHandler),
    [56] = VECTOR(UARTE1_IRQHandler),
    [57] = VECTOR(QSPI_IRQHandler),
    [58] = VECTOR(CRYPTOCELL_IRQHandler),
    [61] = VECTOR(PWM3_IRQHandler),
    [63] = VECTOR(SPIM3_IRQHandler),
};

_Static_assert(sizeof(__isr_vector) == 512u, "nRF52840 vector table size");
