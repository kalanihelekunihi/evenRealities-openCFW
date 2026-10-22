/* SPDX-License-Identifier: MIT
 * Touch (PSoC 4000T) device-configurator output: system, clocks, peripheral
 * clock assignment and pins. Reconstructed from official 2.2.6.10
 * firmware_touch.bin, native 0x44A0..0x4634. Function symbols use the
 * g2/symbols/touch.tsv names; init_cycfg_all is also exported under its
 * ModusToolbox name for the BSP cybsp_init (0x4650).
 */
#ifndef G2_TOUCH_CYCFG_H
#define G2_TOUCH_CYCFG_H

#include <stdint.h>

/* cy_stc_gpio_pin_config_t layout (PDL 2.21 cy_gpio.h), 24 bytes. */
typedef struct {
    uint32_t outVal;
    uint32_t driveMode;
    uint32_t hsiom;
    uint32_t intEdge;
    uint32_t vtrip;
    uint32_t slewRate;
} g2_touch_gpio_pin_config;
_Static_assert(sizeof(g2_touch_gpio_pin_config) == 24, "pin config ABI");

void touch_platform_11c4_sequence(void);           /* init_cycfg_all */
void touch_platform_11a0_sequence(void);           /* cycfg_config_init */
void touch_startup_11b4_passthrough_sequence(void);/* cycfg_config_reservations */
void touch_clock_12d0_transition(void);            /* init_cycfg_system */
void touch_startup_11d0_configure_dividers(void);  /* init_cycfg_clocks */
void touch_startup_1228_assign_divider(void);      /* init_cycfg_peripherals */
void touch_platform_1238_routes(void);             /* init_cycfg_pins */
void touch_leaf_1226_passthrough(void);            /* reserve_cycfg_clocks */
void touch_leaf_1236_passthrough(void);            /* reserve_cycfg_peripherals */
void touch_leaf_12a4_passthrough(void);            /* reserve_cycfg_pins */
void touch_runtime_12a6_fault(uint32_t error);     /* cycfg_ClockStartupError */
void touch_clock_12ac_validate(void);              /* Cy_SysClk_ClkHfInit */
void init_cycfg_all(void);

#endif
