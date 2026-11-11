/* R1 2.2.6.0009 application vectors, indexed from flash 0x27000.
 * Reserved words are zero. Stock default IRQs share one terminal handler.
 * Fault adapters remain explicit providers until reconstructed. */
#include <stdint.h>

typedef void (*r1_vector_handler)(void);

void Reset_Handler(void);
void NMI_Handler(void);
void HardFault_Handler(void);
void MemoryManagement_Handler(void);
void BusFault_Handler(void);
void UsageFault_Handler(void);
void SVC_Handler(void);
void PendSV_Handler(void);
void SysTick_Handler(void);
void POWER_CLOCK_IRQHandler(void);
void nrfx_prs_box_4_irq_handler(void);
void SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0_IRQHandler(void);
void SPIM1_SPIS1_TWIM1_TWIS1_SPI1_TWI1_IRQHandler(void);
void NFCT_IRQHandler(void);
void GPIOTE_IRQHandler(void);
void SAADC_IRQHandler(void);
void TIMER2_IRQHandler(void);
void WDT_IRQHandler(void);
void RTC1_IRQHandler(void);
void r1_task_flag_set_1(void);
void TIMER4_IRQHandler(void);
void PWM0_IRQHandler(void);
void PDM_IRQHandler(void);
void PWM1_IRQHandler(void);
void PWM2_IRQHandler(void);
void SPIM2_SPIS2_SPI2_IRQHandler(void);
void RTC2_IRQHandler(void);
extern uint32_t __StackTop;

/* Reserve the interrupt/startup MSP stack separately from linked data. The
 * Nordic linker places .stack in .stack_dummy and checks its lower limit
 * against the end of .bss/.heap. */
__attribute__((used, section(".stack"), aligned(8)))
static uint8_t r1_msp_stack_reservation[8192];

__attribute__((noreturn, noinline))
static void r1_debugmon_handler(void)
{
    for (;;) { }
}

__attribute__((noreturn, noinline))
static void r1_default_irq_handler(void)
{
    for (;;) { }
}

/* Cortex-M treats word zero as the initial MSP, not as a callable address.
 * Use the source linker's RAM top: the source-built .bss is larger than the
 * stock scatter region and must never overlap the initial MSP stack. */
const r1_vector_handler r1_application_vectors[128]
    __attribute__((section(".isr_vector"), aligned(4), used)) = {
    [0] = (r1_vector_handler)(uintptr_t)&__StackTop,
    [1] = Reset_Handler,
    [2] = NMI_Handler,
    [3] = HardFault_Handler,
    [4] = MemoryManagement_Handler,
    [5] = BusFault_Handler,
    [6] = UsageFault_Handler,
    [11] = SVC_Handler,
    [12] = r1_debugmon_handler,
    [14] = PendSV_Handler,
    [15] = SysTick_Handler,
    [16] = POWER_CLOCK_IRQHandler,
    [17] = r1_default_irq_handler,
    [18] = nrfx_prs_box_4_irq_handler,
    [19] = SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0_IRQHandler,
    [20] = SPIM1_SPIS1_TWIM1_TWIS1_SPI1_TWI1_IRQHandler,
    [21] = NFCT_IRQHandler,
    [22] = GPIOTE_IRQHandler,
    [23] = SAADC_IRQHandler,
    [24] = r1_default_irq_handler,
    [25] = r1_default_irq_handler,
    [26] = TIMER2_IRQHandler,
    [27] = r1_default_irq_handler,
    [28] = r1_default_irq_handler,
    [29] = r1_default_irq_handler,
    [30] = r1_default_irq_handler,
    [31] = r1_default_irq_handler,
    [32] = WDT_IRQHandler,
    [33] = RTC1_IRQHandler,
    [34] = r1_default_irq_handler,
    [35] = r1_default_irq_handler,
    [36] = r1_default_irq_handler,
    [37] = r1_default_irq_handler,
    [38] = r1_task_flag_set_1,
    [39] = r1_default_irq_handler,
    [40] = r1_default_irq_handler,
    [41] = r1_default_irq_handler,
    [42] = r1_default_irq_handler,
    [43] = TIMER4_IRQHandler,
    [44] = PWM0_IRQHandler,
    [45] = PDM_IRQHandler,
    [48] = r1_default_irq_handler,
    [49] = PWM1_IRQHandler,
    [50] = PWM2_IRQHandler,
    [51] = SPIM2_SPIS2_SPI2_IRQHandler,
    [52] = RTC2_IRQHandler,
    [53] = r1_default_irq_handler,
    [54] = r1_default_irq_handler,
    [55] = r1_default_irq_handler,
    [56] = r1_default_irq_handler,
    [57] = r1_default_irq_handler,
    [58] = r1_default_irq_handler,
    [61] = r1_default_irq_handler,
    [63] = r1_default_irq_handler,
};

_Static_assert(sizeof(r1_application_vectors) == 128u * sizeof(uint32_t),
               "R1 nRF52840 application vector table is 128 words");
