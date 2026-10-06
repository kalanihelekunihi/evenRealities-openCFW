/* SPDX-License-Identifier: MIT
 * Bounded source reconstruction of stock 0x41f846.
 *
 * This routine consumes the four-row structure initialized by the locked
 * image's scatter output. It does not allocate or initialize that table.
 */
#include "platform_startup.h"

#include <stdint.h>

#define PLATFORM_ROWS ((volatile uint8_t *)(uintptr_t)0x20000454u)
#define PLATFORM_ROW_SIZE 0x1cu

/* Scalar tables referenced by the scatter-initialized rows at +8. */
__attribute__((section(".boot_platform_config"), used))
const uint32_t opencfw_boot_platform_config_table[12] = {
    12u, 14u, 5u, 5u,
    42u, 44u, 4u, 4u,
    73u, 69u, 5u, 5u,
};

extern uint32_t opencfw_boot_control_power_apply(uint32_t *object,
                                                 uint32_t operation,
                                                 uint32_t enable);
extern uint32_t opencfw_bl_power_register_update(uint32_t register_id,
                                                  uint32_t value);

uint32_t opencfw_boot_platform_configure(uint32_t selector)
{
    const uint8_t row_index = (uint8_t)selector;
    if (row_index >= 4u)
        return 1u;

    volatile uint8_t *const row =
        PLATFORM_ROWS + (uint32_t)row_index * PLATFORM_ROW_SIZE;
    uint32_t power_status = opencfw_boot_control_power_apply(
        (uint32_t *)(uintptr_t)*(volatile uint32_t *)(void *)(row + 4u),
        0u, 1u);

    volatile uint32_t *const config = (volatile uint32_t *)(uintptr_t)
        *(volatile uint32_t *)(void *)(row + 8u);
    (void)opencfw_bl_power_register_update(config[1], config[3]);
    (void)opencfw_bl_power_register_update(config[0], config[2]);

    row[0x18] = 1u;
    return power_status;
}
