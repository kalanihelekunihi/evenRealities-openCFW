/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 ROM power-domain disable adaptation from AmbiqSuite SDK
 * 5.1.0. The reviewed stock function, caller, fixed registers/cache, and host
 * evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_PWRCTRL_ROM_DISABLE_CURRENT_MODE_ADDRESS 0x20074F62U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_MEMORY_ENABLE_ADDRESS 0x40021014U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_MEMORY_STATUS_ADDRESS 0x40021018U

#define OPEN_CFW_PWRCTRL_ROM_DISABLE_AUTO_MODE 1U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_ENABLE_BIT 0x20U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_STATUS_BIT 0x80U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_MAXIMUM_POLLS 10000U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_SPOT_MEMORY_STIMULUS 5U

#define OPEN_CFW_PWRCTRL_ROM_DISABLE_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_TIMEOUT 4U
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_SPOT_UPDATE_ENTRY 0x00480313U

#ifndef OPEN_CFW_PWRCTRL_ROM_DISABLE_MODE_READ
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_MODE_READ() \
    (*(const volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_ROM_DISABLE_CURRENT_MODE_ADDRESS)
#endif

#ifndef OPEN_CFW_PWRCTRL_ROM_DISABLE_READ
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_ROM_DISABLE_WRITE
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_ROM_DISABLE_SPOT_UPDATE
typedef unsigned int (
    *open_cfw_pwrctrl_rom_disable_spot_update_function
)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_PWRCTRL_ROM_DISABLE_SPOT_UPDATE( \
    stimulus, enabled, value \
) \
    (((open_cfw_pwrctrl_rom_disable_spot_update_function) \
        OPEN_CFW_PWRCTRL_ROM_DISABLE_SPOT_UPDATE_ENTRY)( \
            (stimulus), \
            (enabled), \
            (value) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_rom_disable function at 0x0047F418...0x0047F469.
 *
 * The shipped function only notifies the SPOT manager after the hardware
 * reports that ROM power is off, and deliberately ignores that call's result.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_rom_disable(void)
{
    unsigned int count;
    unsigned int memory_status;
    unsigned int register_value;

    if (
        OPEN_CFW_PWRCTRL_ROM_DISABLE_MODE_READ()
        != OPEN_CFW_PWRCTRL_ROM_DISABLE_AUTO_MODE
    ) {
        return OPEN_CFW_PWRCTRL_ROM_DISABLE_SUCCESS;
    }

    register_value = OPEN_CFW_PWRCTRL_ROM_DISABLE_READ(
        OPEN_CFW_PWRCTRL_ROM_DISABLE_MEMORY_ENABLE_ADDRESS
    );
    OPEN_CFW_PWRCTRL_ROM_DISABLE_WRITE(
        OPEN_CFW_PWRCTRL_ROM_DISABLE_MEMORY_ENABLE_ADDRESS,
        register_value & ~OPEN_CFW_PWRCTRL_ROM_DISABLE_ENABLE_BIT
    );

#pragma clang loop unroll(disable)
    for (
        count = 0U;
        count < OPEN_CFW_PWRCTRL_ROM_DISABLE_MAXIMUM_POLLS;
        ++count
    ) {
        if (
            (
                OPEN_CFW_PWRCTRL_ROM_DISABLE_READ(
                    OPEN_CFW_PWRCTRL_ROM_DISABLE_MEMORY_STATUS_ADDRESS
                ) & OPEN_CFW_PWRCTRL_ROM_DISABLE_STATUS_BIT
            ) == 0U
        ) {
            break;
        }
    }

    if (count == OPEN_CFW_PWRCTRL_ROM_DISABLE_MAXIMUM_POLLS) {
        return OPEN_CFW_PWRCTRL_ROM_DISABLE_TIMEOUT;
    }

    memory_status = OPEN_CFW_PWRCTRL_ROM_DISABLE_READ(
        OPEN_CFW_PWRCTRL_ROM_DISABLE_MEMORY_STATUS_ADDRESS
    );
    (void)OPEN_CFW_PWRCTRL_ROM_DISABLE_SPOT_UPDATE(
        OPEN_CFW_PWRCTRL_ROM_DISABLE_SPOT_MEMORY_STIMULUS,
        0U,
        &memory_status
    );

    return OPEN_CFW_PWRCTRL_ROM_DISABLE_SUCCESS;
}
