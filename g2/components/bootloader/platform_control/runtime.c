/* SPDX-License-Identifier: MIT. Source reconstruction of platform mode
 * control entries 0x41f8ba, 0x41ba80 and cleanup 0x41c990. The downstream
 * power-apply, transition, query and cleanup callbacks stay explicit ABI cuts.
 */
#include "runtime.h"
#include <stddef.h>

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern uint32_t opencfw_bl_power_register_update(uint32_t register_id,
                                                  uint32_t value);
extern uint32_t opencfw_boot_control_power_apply_configure(
    uint32_t *object, uint32_t operation, uint8_t enable);
extern uint32_t opencfw_boot_control_query(uint32_t selector,
                                            uint8_t *result);

#define BOOT_CONTROL_HOOKS 0x20026e38u

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
                                             WORD(0x434158u));
    (void)opencfw_bl_power_register_update(register_ids[0],
                                             WORD(0x43415cu));

    uint32_t *const object = *(uint32_t **)(void *)(record + 4);
    return opencfw_boot_control_power_apply(object, 2u, 1u);
}

/* Recovered entry guard for stock 0x422ba8. The accepted object continues
 * into hardware/resource setup which remains an explicit provider boundary. */
__attribute__((noinline))
uint32_t opencfw_boot_control_power_apply(uint32_t *object,
                                          uint32_t operation,
                                          uint32_t enable)
{
    if (object == NULL ||
        (object[0] & 0x01ffffffu) != 0x01ea9e06u)
        return 2u;
    if (operation != 0u && operation > 2u)
        return 6u;
    return opencfw_boot_control_power_apply_configure(
        object, operation, (uint8_t)enable);
}

uint32_t opencfw_boot_control_mode_two(uint32_t mode)
{
    uint8_t selected = (uint8_t)mode;
    if (selected != 1u && selected != 2u)
        return 6u;
    if (selected == 2u && ((WORD(0x40021108u) >> 4) & 3u) != 3u)
        return 7u;
    if (selected == *(volatile uint8_t *)(uintptr_t)0x20000552u)
        return 0u;

    uint32_t status = opencfw_boot_control_transition(selected);
    if (status != 0u)
        return status;
    return (((WORD(0x40021000u) >> 3) & 3u) == selected) ? 0u : 1u;
}

uint32_t opencfw_boot_control_cleanup(void)
{
    if (((WORD(0x40021000u) >> 3) & 3u) == 2u)
        return 1u;

    uint8_t result = 0u;
    if (opencfw_boot_control_query(0x14u, &result) != 0u)
        return 1u;
    if (result != 0u)
        return 1u;
    return opencfw_boot_control_finish();
}

/* Stock 0x41cd60: the third word in the hook table is optional. */
uint32_t opencfw_boot_control_finish(void)
{
    typedef uint32_t (*finish_callback_t)(void);
    finish_callback_t callback = (finish_callback_t)(uintptr_t)
        *(volatile uint32_t *)(uintptr_t)(BOOT_CONTROL_HOOKS + 8u);
    return callback != NULL ? callback() : 0u;
}
