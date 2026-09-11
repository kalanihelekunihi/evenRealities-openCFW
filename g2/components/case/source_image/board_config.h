/* SPDX-License-Identifier: MIT */
/*
 * G2 charging-case (STM32G0B0/G0B1-class) board-routing configuration.
 *
 * The case source image links and packages cleanly (build_image.py), but
 * several choices needed to make it actually drive the board -- which
 * vector-table slots matter, which peripheral instances they belong to,
 * which flash bank is "active" during an OTA swap, and which flash windows
 * must never be overwritten -- were previously implicit: a single comment
 * in startup.c ("Board routing is evidence-locked; keep the source image
 * inert") and unexplained numeric literals in startup.c/linker.ld. This
 * header makes every one of those assumptions a named, documented default
 * instead.
 *
 * Provenance discipline for every value below:
 *   - Values marked CONFIRMED are read directly from
 *     docs/research/g2-box-stm32g0-platform-recovery.md, which derived them
 *     from literal/vector-table evidence in the authenticated stock image
 *     (blobs/official/g2-2.2.6.10/firmware_box.bin) plus the public ST
 *     STM32G0B1 CMSIS device header (stm32g0b1xx.h) and RM0454 reference
 *     manual -- citing part-family documentation is not the same as
 *     extracting vendor firmware bytes.
 *   - Values marked UNCONFIRMED are defaults this source image assumes so
 *     the build has *something* named to reason about; they are not backed
 *     by physical-board evidence and MUST NOT be treated as proven.
 *
 * None of this drives a live peripheral write: Reset_Handler in startup.c
 * still only zeroes .bss, copies .data, and enters a WFI loop. Wiring any
 * UNCONFIRMED binding into real hardware behavior is a follow-up gated on
 * evidence this build cannot manufacture (docs/hardware-validation-policy.md;
 * README.md in this directory: "must not be flashed").
 */
#ifndef OPEN_CFW_CASE_BOARD_CONFIG_H
#define OPEN_CFW_CASE_BOARD_CONFIG_H

#include <stdint.h>

#define OPEN_CFW_CASE_PART_FAMILY "STM32G0B0/G0B1 evidence class" /* CONFIRMED: medium confidence, G0B0 vs G0B1 not statically separable */

/* ---- Flash/SRAM geometry (CONFIRMED: vector table + linker.ld asserts) ---- */
#define OPEN_CFW_CASE_FLASH_BASE       UINT32_C(0x08000000)
#define OPEN_CFW_CASE_FLASH_BANK_BYTES UINT32_C(0x00040000) /* 256 KiB/bank, 512 KiB dual-bank total */
#define OPEN_CFW_CASE_SRAM_BASE        UINT32_C(0x20000000)
#define OPEN_CFW_CASE_SRAM_BYTES       UINT32_C(0x00024000) /* 144 KiB, STM32G0B1 nominal; exact RAM budget unresolved */
#define OPEN_CFW_CASE_STACK_TOP        UINT32_C(0x20002C88) /* CONFIRMED: recovered initial SP, deliberately below SRAM top */

/* ---- Dual-bank OTA swap (CONFIRMED: bank-2 base literals in OTA code +
 * EVENOTA manifest `case_application.alternate_target_addresses`) ----
 * Bank 1 is always the logical run address the vector table targets; bank 2
 * is the inactive staging alias, toggled by the FLASH_CR nSWAP_BANK option
 * byte after a verified OTA copy. Which bank is *physically* active at any
 * moment is runtime state this source image does not attempt to read. */
#define OPEN_CFW_CASE_BANK1_BASE (OPEN_CFW_CASE_FLASH_BASE)                                  /* 0x08000000 */
#define OPEN_CFW_CASE_BANK2_BASE (OPEN_CFW_CASE_FLASH_BASE + OPEN_CFW_CASE_FLASH_BANK_BYTES) /* 0x08040000 */

/* ---- Device-specific identity windows (CONFIRMED: OTA-code literal
 * references, "Device-specific serial/identity preservation" in the
 * platform-recovery audit; the exact same four windows are pinned in
 * tools/open_cfw.py REQUIRED_PROTECTED_REGIONS -- keep both lists in sync
 * if either changes). These live past the end of this source image and
 * must never be included in a flashable case payload. */
#define OPEN_CFW_CASE_IDENTITY_WINDOWS(X) \
    X(0x0803F000, 16) \
    X(0x0803F800, 8)  \
    X(0x0807F000, 16) \
    X(0x0807F800, 8)

/* Preserved-bank-1 cap already asserted in linker.ld (`__flash_load_end <=
 * 0x0803F000`); named here so the two literals cannot silently drift. */
#define OPEN_CFW_CASE_BANK1_IDENTITY_LIMIT UINT32_C(0x0803F000)

/* ---- Vector table (CONFIRMED shape; STM32G0B1 CMSIS map, stm32g0b1xx.h,
 * public ST device header) ----
 * 16 fixed Cortex-M0+ system vectors + 30 device IRQ slots = 46 words,
 * matching startup.c's open_cfw_case_vectors[46]. Every slot keeps its
 * Default_Handler body (see startup.c) except where the audit found a
 * populated, non-default stock handler -- those are CONFIRMED occupied but
 * this source image still does not reimplement their board behavior. */
#define OPEN_CFW_CASE_VECTOR_COUNT 46

#define OPEN_CFW_CASE_IRQ_PVD    1  /* CONFIRMED default (zero slot) in the stock image */
#define OPEN_CFW_CASE_IRQ_TIM2   15 /* CONFIRMED default (zero slot) in the stock image */
#define OPEN_CFW_CASE_IRQ_USART1 27 /* CONFIRMED populated: HAL_UART_IRQHandler, case<->glasses link */
#define OPEN_CFW_CASE_IRQ_CEC    30 /* CONFIRMED not populated; recovered table ends at IRQ29 */
/* ADC1_COMP and TIM17 also have populated, non-default handlers in the
 * stock image (ISR/IER worker; TIM SR/DIER capture-compare worker), but
 * the audit did not resolve their IRQ slot indices. Left UNCONFIRMED
 * rather than guessed -- do not add index macros for them without new
 * evidence. */

/* ---- Peripheral module presence (CONFIRMED by base-address literal
 * census in the stock image; RM0454 base addresses are public silicon
 * facts, not vendor-proprietary data) ----
 * Only USART3 and USART4 had their base-address literal directly quoted
 * by the audit; the rest are name-only entries -- asserting a specific
 * numeric base for them here without re-deriving it from evidence would
 * itself be an unverified claim, so this header does not. */
#define OPEN_CFW_CASE_USART3_BASE UINT32_C(0x40004800) /* CONFIRMED literal in stock image */
#define OPEN_CFW_CASE_USART4_BASE UINT32_C(0x40004C00) /* CONFIRMED literal in stock image */

#define OPEN_CFW_CASE_PRESENT_MODULES(X) \
    X(RCC) X(FLASH) X(PWR) X(RTC) X(ADC1) \
    X(TIM1) X(TIM3) X(TIM6) X(TIM14) X(TIM16) X(TIM17) \
    X(USART1) X(USART2) X(USART3) X(USART4) \
    X(GPIOA) X(GPIOB) X(GPIOC) X(GPIOD) X(SYSCFG_EXTI) X(SCS_SYSTICK)

/* Confirmed absent by the same census (no base-address literal anywhere
 * in the stock image) -- no placeholder binding is defined for these. */
#define OPEN_CFW_CASE_ABSENT_MODULES(X) \
    X(I2C1) X(I2C2) X(DMA1) X(DMA2) X(USB_DRD) X(FDCAN1) X(FDCAN2) \
    X(RNG) X(AES) X(LPUART1) X(LPUART2) X(UCPD1) X(UCPD2) \
    X(CRC) X(IWDG) X(WWDG) X(DBGMCU)

/* ---- UNCONFIRMED board-routing defaults ----
 * These are the specific assumptions the item asked to make explicit: the
 * case-to-glasses link runs over the one USART with a populated interrupt
 * vector (USART1, IRQ27 above), the GPIO ports actually referenced are
 * GPIOA..GPIOD (module presence above), and PWM/backlight-style timing
 * uses one of TIM1/3/6/14/16/17. Exact pin, alternate-function, and timer
 * *instance* selection is NOT resolved by any available evidence: there is
 * no schematic, no strap/option-byte dump, and no physical unit to probe
 * (docs/hardware-validation-policy.md). The names below are the default
 * this source image assumes if that evidence ever becomes available;
 * nothing in components/case reads them today. */
#define OPEN_CFW_CASE_LINK_UART_NAME "USART1" /* UNCONFIRMED instance selection; IRQ slot is CONFIRMED (see above) */
#define OPEN_CFW_CASE_LED_GPIO_PORT_DEFAULT "GPIOB" /* UNCONFIRMED: module presence only, no pin evidence */
#define OPEN_CFW_CASE_PMIC_GPIO_PORTS_DEFAULT "GPIOB,GPIOC,GPIOD" /* UNCONFIRMED: bit-banged PMIC/charger/watchdog per audit, exact pins unresolved */

#endif
