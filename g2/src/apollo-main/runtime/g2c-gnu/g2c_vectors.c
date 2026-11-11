// SPDX-License-Identifier: Apache-2.0
/*
 * GNU-link vector table for the Apollo510 main image (g2c wave 2).
 * Generated from the stock table at ROM 0x438000 (151 words: initial MSP
 * 0x2007FB00, 15 system exceptions, 135 IRQ slots). Each slot names the g2/src
 * function whose address suffix matches the stock handler.
 *
 * Wave 21: every slot now has a body. The ten handlers that wave 2 left on
 * spin aliases were verified against the stock image disassembly
 * (/tmp/apm.bin, base 0x438000, objdump force-thumb) and the Ghidra corpus
 * apollo-main/ghidra/open-2026-09-29/decomp/<addr>.c, and resolved as follows:
 *   slot 3  0x5b0114 -> HardFault_Handler (verified: stock mov r0,lr; mov r1,sp;
 *           bl 0x5944bc; bl . == CmBacktrace cmb_fault.S as linked at 0x5032fc)
 *   slot 11 0x5fa120 -> SVC_Handler (verified: tst lr,#4; mrs MSP/PSP; b.w 0x442134
 *           == FreeRTOS ARM_CM55 portasm.c SVC_Handler -> vPortSVCHandler_C)
 *   slot 14 0x5fa0c8 -> PendSV_Handler (verified: PSP/PSPLIM save, BASEPRI 0x30,
 *           bl 0x4551b4 vTaskSwitchContext == FreeRTOS ARM_CM55 portasm.c)
 *   slot 15 0x442114 -> SysTick_Handler (verified: ulSetInterruptMask, bl 0x45504c
 *           xTaskIncrementTick, ICSR=0x10000000, vClearInterruptMask == port.c)
 *   IRQ10 0x504488 -> hal_i2c_irq_handler (verified: IOM status/clear/service
 *           0x55c4d0/0x55c518/0x55c558 on [tbl+0x44] == hal_i2c.c)
 *   IRQ20 0x4c9d44 -> uled_mspi_term (verified: Ghidra decomp names it; driver
 *           ->term or log line 0x4b == uled_manager.c)
 *   IRQ44 0x57a4d8 -> gx8002_i2s_isr (verified: 0x590848/0x590818/0x5908a0, bit 4)
 *   IRQ48 0x57b940 -> PDM0_IRQHandler (verified: productModeGet 0x4abe60 branch,
 *           0x5925e0/0x5925b4/0x592484, bit 3)
 *   IRQ59 0x4b80be and IRQ82 0x4d58a6: bodies below, transcribed from stock.
 * g2c_unhandled_isr stays only as the target for any future unbound slot.
 */
#include <stdint.h>
typedef void (*g2c_vector_t)(void);
/* Initial MSP = CSTACK top, stock 0x2007fb00 (link/g2-apollo-main.ld: _estack). */
extern uint32_t _estack[];

/* Local spin target for the weak aliases (clang needs an alias target defined
 * in this TU); behaves like stock am_default_isr_5e4250 (b .). */
void g2c_unhandled_isr(void) { for (;;) { } }

extern void nmi_handler_4397a6(void);
extern void SysTick_Handler(void);
extern void am_timer00_isr_44466c(void);
extern void port_stimer_isr_456426(void);
extern void am_mspi1_isr_46f4ea(void);
void am_gpio0_607f_isr_4b80be(void);
extern void uled_mspi_term(void);
void am_irq82_isr_4d58a6(void);
extern void hal_i2c_irq_handler(void);
extern void gpu_irq_handler_513f92(void);
extern void am_gpio0_001f_isr_53a5e0(void);
extern void am_gpio0_203f_isr_53a606(void);
extern void am_gpio0_405f_isr_53a62c(void);
extern void uart_channel1_isr_55e346(void);
extern void uart_channel2_isr_55e35c(void);
extern void uart_channel3_isr_55e372(void);
extern void gx8002_i2s_isr(void);
extern void PDM0_IRQHandler(void);
extern void uart_sync_irq_handler_584a7c(void);
extern void HardFault_Handler(void);
extern void reset_handler_5e4232(void);
extern void am_default_isr_5e4250(void);
extern void PendSV_Handler(void);
extern void SVC_Handler(void);
void am_default_isr_5e4250(void);

#include <stdbool.h>
extern uint32_t am_hal_gpio_interrupt_status_get_4812f6(uint32_t channel, bool enabled_only,
                                                        uint32_t *mask);
extern uint32_t am_hal_gpio_interrupt_irq_status_get_481574(uint32_t irq, bool enabled_only,
                                                            uint32_t *status);
extern uint32_t am_hal_gpio_interrupt_irq_clear_4815f2(uint32_t irq, uint32_t mask);
extern uint32_t am_hal_gpio_interrupt_service_4816c6(uint32_t irq, uint32_t mask);
extern void am_hal_spotmgr_boost_timer_interrupt_service_48039a(void);

/* 0x4b80be GPIO0_607F (IRQ 59), verified against stock disasm 0x4b80be..0x4b80e8
 * and Ghidra decomp/004b80be.c (GPIO0_607F_IRQHandler): stock first reads the
 * channel-0 mask into a 0x1c-byte stack buffer (bl 0x4812f6 r0=0 r1=0) and
 * discards it, then status_get/clear/service with immediate r0=#59. */
void am_gpio0_607f_isr_4b80be(void)
{
    uint32_t mask[7];
    uint32_t status;

    (void)am_hal_gpio_interrupt_status_get_4812f6(0u, false, mask);
    (void)am_hal_gpio_interrupt_irq_status_get_481574(59u, false, &status);
    (void)am_hal_gpio_interrupt_irq_clear_4815f2(59u, status);
    (void)am_hal_gpio_interrupt_service_4816c6(59u, status);
}

/* 0x4d58a6 (IRQ 82, vector slot 98), verified against stock disasm
 * 0x4d58a6..0x4d58ac: push {r7,lr}; bl 0x48039a; pop {r0,pc}. */
void am_irq82_isr_4d58a6(void)
{
    am_hal_spotmgr_boost_timer_interrupt_service_48039a();
}

__attribute__((section(".isr_vector"), used))
const g2c_vector_t g2c_main_vectors[151] = {
    (g2c_vector_t)(uintptr_t)_estack, /* initial MSP, stock 0x2007fb00 */
    reset_handler_5e4232, /* 1 */
    nmi_handler_4397a6, /* 2 */
    HardFault_Handler, /* 3 */
    0, /* 4 reserved */
    0, /* 5 reserved */
    0, /* 6 reserved */
    0, /* 7 reserved */
    0, /* 8 reserved */
    0, /* 9 reserved */
    0, /* 10 reserved */
    SVC_Handler, /* 11 */
    am_default_isr_5e4250, /* 12 */
    0, /* 13 reserved */
    PendSV_Handler, /* 14 */
    SysTick_Handler, /* 15 */
    am_default_isr_5e4250, /* 16 IRQ0 */
    am_default_isr_5e4250, /* 17 IRQ1 */
    am_default_isr_5e4250, /* 18 IRQ2 */
    am_default_isr_5e4250, /* 19 IRQ3 */
    am_default_isr_5e4250, /* 20 IRQ4 */
    am_default_isr_5e4250, /* 21 IRQ5 */
    am_default_isr_5e4250, /* 22 IRQ6 */
    am_default_isr_5e4250, /* 23 IRQ7 */
    am_default_isr_5e4250, /* 24 IRQ8 */
    am_default_isr_5e4250, /* 25 IRQ9 */
    hal_i2c_irq_handler, /* 26 IRQ10 */
    am_default_isr_5e4250, /* 27 IRQ11 */
    am_default_isr_5e4250, /* 28 IRQ12 */
    am_default_isr_5e4250, /* 29 IRQ13 */
    am_default_isr_5e4250, /* 30 IRQ14 */
    uart_sync_irq_handler_584a7c, /* 31 IRQ15 */
    uart_channel1_isr_55e346, /* 32 IRQ16 */
    uart_channel2_isr_55e35c, /* 33 IRQ17 */
    uart_channel3_isr_55e372, /* 34 IRQ18 */
    am_default_isr_5e4250, /* 35 IRQ19 */
    uled_mspi_term, /* 36 IRQ20 */
    am_mspi1_isr_46f4ea, /* 37 IRQ21 */
    am_default_isr_5e4250, /* 38 IRQ22 */
    am_default_isr_5e4250, /* 39 IRQ23 */
    am_default_isr_5e4250, /* 40 IRQ24 */
    am_default_isr_5e4250, /* 41 IRQ25 */
    am_default_isr_5e4250, /* 42 IRQ26 */
    am_default_isr_5e4250, /* 43 IRQ27 */
    gpu_irq_handler_513f92, /* 44 IRQ28 */
    am_default_isr_5e4250, /* 45 IRQ29 */
    am_default_isr_5e4250, /* 46 IRQ30 */
    am_default_isr_5e4250, /* 47 IRQ31 */
    port_stimer_isr_456426, /* 48 IRQ32 */
    am_default_isr_5e4250, /* 49 IRQ33 */
    am_default_isr_5e4250, /* 50 IRQ34 */
    am_default_isr_5e4250, /* 51 IRQ35 */
    am_default_isr_5e4250, /* 52 IRQ36 */
    am_default_isr_5e4250, /* 53 IRQ37 */
    am_default_isr_5e4250, /* 54 IRQ38 */
    am_default_isr_5e4250, /* 55 IRQ39 */
    am_default_isr_5e4250, /* 56 IRQ40 */
    am_default_isr_5e4250, /* 57 IRQ41 */
    am_default_isr_5e4250, /* 58 IRQ42 */
    am_default_isr_5e4250, /* 59 IRQ43 */
    gx8002_i2s_isr, /* 60 IRQ44 */
    am_default_isr_5e4250, /* 61 IRQ45 */
    am_default_isr_5e4250, /* 62 IRQ46 */
    am_default_isr_5e4250, /* 63 IRQ47 */
    PDM0_IRQHandler, /* 64 IRQ48 */
    am_default_isr_5e4250, /* 65 IRQ49 */
    am_default_isr_5e4250, /* 66 IRQ50 */
    am_default_isr_5e4250, /* 67 IRQ51 */
    am_default_isr_5e4250, /* 68 IRQ52 */
    am_default_isr_5e4250, /* 69 IRQ53 */
    am_default_isr_5e4250, /* 70 IRQ54 */
    am_default_isr_5e4250, /* 71 IRQ55 */
    am_gpio0_001f_isr_53a5e0, /* 72 IRQ56 */
    am_gpio0_203f_isr_53a606, /* 73 IRQ57 */
    am_gpio0_405f_isr_53a62c, /* 74 IRQ58 */
    am_gpio0_607f_isr_4b80be, /* 75 IRQ59 */
    am_default_isr_5e4250, /* 76 IRQ60 */
    am_default_isr_5e4250, /* 77 IRQ61 */
    am_default_isr_5e4250, /* 78 IRQ62 */
    am_default_isr_5e4250, /* 79 IRQ63 */
    am_default_isr_5e4250, /* 80 IRQ64 */
    am_default_isr_5e4250, /* 81 IRQ65 */
    am_default_isr_5e4250, /* 82 IRQ66 */
    am_timer00_isr_44466c, /* 83 IRQ67 */
    am_default_isr_5e4250, /* 84 IRQ68 */
    am_default_isr_5e4250, /* 85 IRQ69 */
    am_default_isr_5e4250, /* 86 IRQ70 */
    am_default_isr_5e4250, /* 87 IRQ71 */
    am_default_isr_5e4250, /* 88 IRQ72 */
    am_default_isr_5e4250, /* 89 IRQ73 */
    am_default_isr_5e4250, /* 90 IRQ74 */
    am_default_isr_5e4250, /* 91 IRQ75 */
    am_default_isr_5e4250, /* 92 IRQ76 */
    am_default_isr_5e4250, /* 93 IRQ77 */
    am_default_isr_5e4250, /* 94 IRQ78 */
    am_default_isr_5e4250, /* 95 IRQ79 */
    am_default_isr_5e4250, /* 96 IRQ80 */
    am_default_isr_5e4250, /* 97 IRQ81 */
    am_irq82_isr_4d58a6, /* 98 IRQ82 */
    am_default_isr_5e4250, /* 99 IRQ83 */
    am_default_isr_5e4250, /* 100 IRQ84 */
    am_default_isr_5e4250, /* 101 IRQ85 */
    am_default_isr_5e4250, /* 102 IRQ86 */
    am_default_isr_5e4250, /* 103 IRQ87 */
    am_default_isr_5e4250, /* 104 IRQ88 */
    am_default_isr_5e4250, /* 105 IRQ89 */
    am_default_isr_5e4250, /* 106 IRQ90 */
    am_default_isr_5e4250, /* 107 IRQ91 */
    am_default_isr_5e4250, /* 108 IRQ92 */
    am_default_isr_5e4250, /* 109 IRQ93 */
    am_default_isr_5e4250, /* 110 IRQ94 */
    am_default_isr_5e4250, /* 111 IRQ95 */
    am_default_isr_5e4250, /* 112 IRQ96 */
    am_default_isr_5e4250, /* 113 IRQ97 */
    am_default_isr_5e4250, /* 114 IRQ98 */
    am_default_isr_5e4250, /* 115 IRQ99 */
    am_default_isr_5e4250, /* 116 IRQ100 */
    am_default_isr_5e4250, /* 117 IRQ101 */
    am_default_isr_5e4250, /* 118 IRQ102 */
    am_default_isr_5e4250, /* 119 IRQ103 */
    am_default_isr_5e4250, /* 120 IRQ104 */
    am_default_isr_5e4250, /* 121 IRQ105 */
    am_default_isr_5e4250, /* 122 IRQ106 */
    am_default_isr_5e4250, /* 123 IRQ107 */
    am_default_isr_5e4250, /* 124 IRQ108 */
    am_default_isr_5e4250, /* 125 IRQ109 */
    am_default_isr_5e4250, /* 126 IRQ110 */
    am_default_isr_5e4250, /* 127 IRQ111 */
    am_default_isr_5e4250, /* 128 IRQ112 */
    am_default_isr_5e4250, /* 129 IRQ113 */
    am_default_isr_5e4250, /* 130 IRQ114 */
    am_default_isr_5e4250, /* 131 IRQ115 */
    am_default_isr_5e4250, /* 132 IRQ116 */
    am_default_isr_5e4250, /* 133 IRQ117 */
    am_default_isr_5e4250, /* 134 IRQ118 */
    am_default_isr_5e4250, /* 135 IRQ119 */
    am_default_isr_5e4250, /* 136 IRQ120 */
    am_default_isr_5e4250, /* 137 IRQ121 */
    am_default_isr_5e4250, /* 138 IRQ122 */
    am_default_isr_5e4250, /* 139 IRQ123 */
    am_default_isr_5e4250, /* 140 IRQ124 */
    am_default_isr_5e4250, /* 141 IRQ125 */
    am_default_isr_5e4250, /* 142 IRQ126 */
    am_default_isr_5e4250, /* 143 IRQ127 */
    am_default_isr_5e4250, /* 144 IRQ128 */
    am_default_isr_5e4250, /* 145 IRQ129 */
    am_default_isr_5e4250, /* 146 IRQ130 */
    am_default_isr_5e4250, /* 147 IRQ131 */
    am_default_isr_5e4250, /* 148 IRQ132 */
    am_default_isr_5e4250, /* 149 IRQ133 */
    am_default_isr_5e4250, /* 150 IRQ134 */
};
