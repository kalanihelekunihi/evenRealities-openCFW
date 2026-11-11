/* SPDX-License-Identifier: MIT
 * Calls from bootloader hand code into the upstream AmbiqSuite SDK 5.0.0
 * am_hal_pwrctrl.c (third-party/upstream/ambiqhal-apollo510-sdk5.0.0), which
 * provides stock 0x41b8f8..0x41cae8. Raw prototypes: these callers build
 * without the HAL include path. Peripheral and control selectors are the
 * am_hal_pwrctrl_periph_e / am_hal_pwrctrl_control_e values. */
#ifndef OPENCFW_BOOT_AM_HAL_PWRCTRL_API_H
#define OPENCFW_BOOT_AM_HAL_PWRCTRL_API_H
#include <stdbool.h>
#include <stdint.h>
uint32_t am_hal_pwrctrl_periph_enable(uint32_t ePeripheral);
uint32_t am_hal_pwrctrl_periph_disable(uint32_t ePeripheral);
uint32_t am_hal_pwrctrl_periph_enabled(uint32_t ePeripheral, bool *bEnabled);
uint32_t am_hal_pwrctrl_mcu_mode_select(uint32_t ePowerMode);
uint32_t am_hal_pwrctrl_rom_enable(void);
uint32_t am_hal_pwrctrl_rom_disable(void);
uint32_t am_hal_pwrctrl_low_power_init(void);
uint32_t am_hal_pwrctrl_control(uint32_t eControl, void *pArgs);
uint32_t am_hal_pwrctrl_settings_restore(void);
/* Hard-float like stock 0x41ca2c (fCurTemp in s0); see the generated am_hal_pwrctrl.h. */
__attribute__((pcs("aapcs-vfp"))) uint32_t am_hal_pwrctrl_temp_update(float fCurTemp, void *psTempThresh);
uint32_t am_hal_pwrctrl_syspll_enable(void);
uint32_t am_hal_pwrctrl_syspll_disable(void);
void buck_ldo_update_override(bool bEnable);
#endif
