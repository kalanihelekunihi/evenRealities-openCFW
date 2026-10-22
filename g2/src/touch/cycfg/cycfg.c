/* SPDX-License-Identifier: MIT
 * Touch (PSoC 4000T CY8C4046FNI-T412) device-configurator output
 * (cycfg.c / cycfg_system.c / cycfg_clocks.c / cycfg_peripherals.c /
 * cycfg_pins.c equivalents). The product's generated sources are not
 * public; this is reconstructed from official 2.2.6.10 firmware_touch.bin,
 * native 0x44A0..0x45A4 (code) and ROM 0xB38C..0xB41C (pin records).
 * PDL callees are the pinned mtb-pdl-cat2 2.21 functions; SRSS register
 * writes stand for the cy_sysclk.h inline helpers the generator emits.
 */
#include "cycfg.h"

#define SRSS_BASE        0x40030000u
#define SRSS_CLK_SELECT  (*(volatile uint32_t *)(SRSS_BASE + 0x28u)) /* HFCLK div bits 2..3, SYSCLK div bits 6..7 */
#define SRSS_CLK_ILO     (*(volatile uint32_t *)(SRSS_BASE + 0x2Cu)) /* bit31 ILO enable */
#define SRSS_CLK_IMO     (*(volatile uint32_t *)(SRSS_BASE + 0x30u)) /* bit31 IMO enable */

#define GPIO_PRT2        ((void *)0x40040200u)
#define GPIO_PRT3        ((void *)0x40040300u)
#define GPIO_PRT4        ((void *)0x40040400u)

extern void Cy_SysLib_SetWaitStates(uint32_t clkHfMHz);                         /* 0xA33C */
extern uint32_t Cy_SysClk_ImoSetFrequency(uint32_t freq);                        /* 0x9C80 */
extern uint32_t Cy_SysClk_ClkHfSetSource(uint32_t source);                       /* 0x9F44 */
extern uint32_t Cy_SysClk_ClkPumpSetSource(uint32_t source);                     /* 0xA188 */
extern uint32_t Cy_SysClk_PeriphSetDivider(uint32_t type, uint32_t num, uint32_t div);              /* 0x9FD4 */
extern uint32_t Cy_SysClk_PeriphSetFracDivider(uint32_t type, uint32_t num, uint32_t i, uint32_t f); /* 0xA01C */
extern uint32_t Cy_SysClk_PeriphAssignDivider(uint32_t ip, uint32_t type, uint32_t num);            /* 0xA0BC */
extern uint32_t Cy_SysClk_PeriphEnableDivider(uint32_t type, uint32_t num);      /* 0xA104 */
extern uint32_t Cy_SysClk_PeriphDisableDivider(uint32_t type, uint32_t num);     /* 0xA148 */
extern uint32_t Cy_GPIO_Pin_Init(void *base, uint32_t pinNum, const g2_touch_gpio_pin_config *config); /* 0x8EE4 */
extern void SystemCoreClockUpdate(void);                                         /* 0x4734 (BSP system_cat2.c) */

/* PDL divider types: 1 = 16-bit integer, 2 = 16.5 fractional, 3 = 24.5 fractional. */
enum { DIV_16_BIT = 1u, DIV_16_5_BIT = 2u, DIV_24_5_BIT = 3u };
/* PCLK index 1 = SCB1 clock (host I2C). */
enum { PCLK_SCB1_CLOCK = 1u };
/* Generated CY_CFG_SYSCLK_CLKHF_ERROR. */
enum { CYCFG_CLKHF_ERROR = 6u };

/* Pin records (outVal, driveMode, hsiom, intEdge, vtrip, slewRate). Drive
 * modes: 4 = open-drain drives low, 6 = strong, +8 = input buffer on. */
static const g2_touch_gpio_pin_config cycfg_p4_1_config = {1u, 12u, 0u, 0u, 0u, 0u};   /* ROM 0xB38C: open-drain, pulsed low by 0x3AFC (5-click host reset) */
static const g2_touch_gpio_pin_config cycfg_p4_0_config = {1u, 14u, 0u, 0u, 0u, 0u};   /* ROM 0xB3A4: host attention, active low */
static const g2_touch_gpio_pin_config cycfg_p3_3_config = {1u, 6u, 0u, 0u, 0u, 0u};    /* ROM 0xB3BC */
static const g2_touch_gpio_pin_config cycfg_p3_2_config = {1u, 6u, 0u, 0u, 0u, 0u};    /* ROM 0xB3D4 */
static const g2_touch_gpio_pin_config cycfg_p2_3_config = {1u, 4u, 14u, 0u, 0u, 0u};   /* ROM 0xB3EC: SCB1 I2C */
static const g2_touch_gpio_pin_config cycfg_p2_2_config = {1u, 4u, 14u, 0u, 0u, 0u};   /* ROM 0xB404: SCB1 I2C */

/* Stock 0x000045A6 (touch_runtime_12a6_fault) - cycfg_ClockStartupError */
void touch_runtime_12a6_fault(uint32_t error)
{
    (void)error;
    __asm volatile ("bkpt #1");
}

/* Stock 0x000045AC (touch_clock_12ac_validate) - Cy_SysClk_ClkHfInit:
 * HFCLK from IMO, then HFCLK divider 1. */
void touch_clock_12ac_validate(void)
{
    if (Cy_SysClk_ClkHfSetSource(0u) != 0u) {
        touch_runtime_12a6_fault(CYCFG_CLKHF_ERROR);
    }
    SRSS_CLK_SELECT &= ~0x0Cu;
}

/* Stock 0x000045D0 (touch_clock_12d0_transition) - init_cycfg_system:
 * bring the IMO up at 24 MHz first, then retarget to 48 MHz, with flash
 * wait states programmed for 48 MHz before and after. */
void touch_clock_12d0_transition(void)
{
    Cy_SysLib_SetWaitStates(48u);
    SRSS_CLK_IMO = 0x80000000u;
    (void)Cy_SysClk_ImoSetFrequency(24000000u);
    (void)Cy_SysClk_ClkHfSetSource(0u);
    SRSS_CLK_SELECT &= ~0x0Cu;
    SRSS_CLK_SELECT &= ~0xC0u;
    SystemCoreClockUpdate();
    (void)Cy_SysClk_ClkPumpSetSource(0u);
    SRSS_CLK_ILO |= 0x80000000u;
    (void)Cy_SysClk_ImoSetFrequency(48000000u);
    touch_clock_12ac_validate();
    SRSS_CLK_SELECT &= ~0xC0u;
    Cy_SysLib_SetWaitStates(48u);
    SystemCoreClockUpdate();
}

/* Stock 0x000044D0 (touch_startup_11d0_configure_dividers) - init_cycfg_clocks */
void touch_startup_11d0_configure_dividers(void)
{
    (void)Cy_SysClk_PeriphDisableDivider(DIV_16_BIT, 1u);
    (void)Cy_SysClk_PeriphSetDivider(DIV_16_BIT, 1u, 3u);
    (void)Cy_SysClk_PeriphEnableDivider(DIV_16_BIT, 1u);
    (void)Cy_SysClk_PeriphDisableDivider(DIV_16_5_BIT, 0u);
    (void)Cy_SysClk_PeriphSetFracDivider(DIV_16_5_BIT, 0u, 51u, 3u);
    (void)Cy_SysClk_PeriphEnableDivider(DIV_16_5_BIT, 0u);
    (void)Cy_SysClk_PeriphDisableDivider(DIV_24_5_BIT, 0u);
    (void)Cy_SysClk_PeriphSetFracDivider(DIV_24_5_BIT, 0u, 51u, 3u);
    (void)Cy_SysClk_PeriphEnableDivider(DIV_24_5_BIT, 0u);
}

/* Stock 0x00004526 (touch_leaf_1226_passthrough) - reserve_cycfg_clocks (no HAL) */
void touch_leaf_1226_passthrough(void)
{
}

/* Stock 0x00004528 (touch_startup_1228_assign_divider) - init_cycfg_peripherals */
void touch_startup_1228_assign_divider(void)
{
    (void)Cy_SysClk_PeriphAssignDivider(PCLK_SCB1_CLOCK, DIV_16_BIT, 1u);
}

/* Stock 0x00004536 (touch_leaf_1236_passthrough) - reserve_cycfg_peripherals (no HAL) */
void touch_leaf_1236_passthrough(void)
{
}

/* Stock 0x00004538 (touch_platform_1238_routes) - init_cycfg_pins */
void touch_platform_1238_routes(void)
{
    (void)Cy_GPIO_Pin_Init(GPIO_PRT2, 2u, &cycfg_p2_2_config);
    (void)Cy_GPIO_Pin_Init(GPIO_PRT2, 3u, &cycfg_p2_3_config);
    (void)Cy_GPIO_Pin_Init(GPIO_PRT3, 2u, &cycfg_p3_2_config);
    (void)Cy_GPIO_Pin_Init(GPIO_PRT3, 3u, &cycfg_p3_3_config);
    (void)Cy_GPIO_Pin_Init(GPIO_PRT4, 0u, &cycfg_p4_0_config);
    (void)Cy_GPIO_Pin_Init(GPIO_PRT4, 1u, &cycfg_p4_1_config);
}

/* Stock 0x000045A4 (touch_leaf_12a4_passthrough) - reserve_cycfg_pins (no HAL) */
void touch_leaf_12a4_passthrough(void)
{
}

/* Stock 0x000044A0 (touch_platform_11a0_sequence) - cycfg_config_init */
void touch_platform_11a0_sequence(void)
{
    touch_clock_12d0_transition();
    touch_startup_11d0_configure_dividers();
    touch_startup_1228_assign_divider();
    touch_platform_1238_routes();
}

/* Stock 0x000044B4 (touch_startup_11b4_passthrough_sequence) - cycfg_config_reservations */
void touch_startup_11b4_passthrough_sequence(void)
{
    touch_leaf_1226_passthrough();
    touch_leaf_1236_passthrough();
    touch_leaf_12a4_passthrough();
}

/* Stock 0x000044C4 (touch_platform_11c4_sequence) - init_cycfg_all */
void touch_platform_11c4_sequence(void)
{
    touch_platform_11a0_sequence();
    touch_startup_11b4_passthrough_sequence();
}

void init_cycfg_all(void) __attribute__((alias("touch_platform_11c4_sequence")));
