/* SPDX-License-Identifier: MIT. Source reconstruction of platform mode
 * control entry 0x41f8ba. 0x41ba80, 0x41c990 and 0x41cd60 are upstream
 * am_hal_pwrctrl_mcu_mode_select, am_hal_pwrctrl_settings_restore and
 * am_hal_spotmgr_default_reset (SDK 5.0.0).
 */
#include "runtime.h"
#include <stddef.h>

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern uint32_t opencfw_bl_power_register_update(uint32_t register_id,
                                                  uint32_t value);

extern const uint32_t opencfw_boot_mode_values[2];

uint32_t opencfw_boot_control_mode_one(uint32_t mode)
{
    uint8_t selected = (uint8_t)mode;
    if (selected >= 4u)
        return 1u;

    uint8_t *const record = (uint8_t *)(uintptr_t)(
        0x20000454u + (uint32_t)selected * 0x1cu);
    record[0x18] = 0u;

    uint32_t *const register_ids = *(uint32_t **)(void *)(record + 8);
    (void)opencfw_bl_power_register_update(register_ids[1],
                                             opencfw_boot_mode_values[0]);
    (void)opencfw_bl_power_register_update(register_ids[0],
                                             opencfw_boot_mode_values[1]);

    uint32_t *const object = *(uint32_t **)(void *)(record + 4);
    return am_hal_uart_power_control(object, 2u, 1u);
}

/* Stock entry names that branch straight to the provider above. */
__typeof__(opencfw_boot_control_mode_one) opencfw_bl_post_record_initialized __attribute__((alias("opencfw_boot_control_mode_one")));
