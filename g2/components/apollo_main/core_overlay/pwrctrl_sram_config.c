/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 shared-SRAM power configuration adaptation from
 * AmbiqSuite SDK 5.1.0. The reviewed stock function, caller, registers, and
 * host evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_ENABLE_ADDRESS 0x40021024U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_STATUS_ADDRESS 0x40021028U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS 0x4002102CU
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_ADDRESS 0x40021040U

#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_BANK_MASK 0x00000007U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_ACTIVE_MCU_MASK 0x00000038U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_ACTIVE_GFX_MASK 0x00000E00U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_ACTIVE_DISPLAY_MASK 0x00007000U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_GFX_MASK 0x00003800U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_DISPLAY_MASK 0x00000700U

#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_MAXIMUM_WAIT_US 5U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_STIMULUS 6U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_FAILURE 1U

#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_UPDATE_ENTRY 0x00480313U
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_STATUS_CHECK_ENTRY 0x00480827U

#ifndef OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_UPDATE
typedef unsigned int (
    *open_cfw_pwrctrl_sram_config_spot_update_function
)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_UPDATE( \
    stimulus, enabled, value \
) \
    (((open_cfw_pwrctrl_sram_config_spot_update_function) \
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_UPDATE_ENTRY)( \
            (stimulus), \
            (enabled), \
            (value) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_SRAM_CONFIG_STATUS_CHECK
typedef unsigned int (
    *open_cfw_pwrctrl_sram_config_status_check_function
)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_STATUS_CHECK( \
    maximum_wait_us, address, mask, expected, equal \
) \
    (((open_cfw_pwrctrl_sram_config_status_check_function) \
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_STATUS_CHECK_ENTRY)( \
            (maximum_wait_us), \
            (address), \
            (mask), \
            (expected), \
            (equal) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_sram_config function at 0x0047F46A...0x0047F56D.
 *
 * The shipped image uses its short-enum ABI as five consecutive bytes and
 * deliberately ignores both SPOT manager return values.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_sram_config(const void *configuration)
{
    const unsigned char *config =
        (const unsigned char *)configuration;
    unsigned int current_banks;
    unsigned int enable_value;
    unsigned int register_value;
    unsigned int result;
    unsigned int target_banks;
    unsigned int update_later = 0U;

    target_banks = config[0];
    current_banks = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_STATUS_ADDRESS
    ) & OPEN_CFW_PWRCTRL_SRAM_CONFIG_BANK_MASK;

    if (target_banks != current_banks) {
        if (target_banks > current_banks) {
            (void)OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_UPDATE(
                OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_STIMULUS,
                1U,
                config
            );
        } else {
            update_later = 1U;
        }

        enable_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_ENABLE_ADDRESS
        );
        enable_value =
            (enable_value & ~OPEN_CFW_PWRCTRL_SRAM_CONFIG_BANK_MASK)
            | (target_banks & OPEN_CFW_PWRCTRL_SRAM_CONFIG_BANK_MASK);
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_ENABLE_ADDRESS,
            enable_value
        );

        result = OPEN_CFW_PWRCTRL_SRAM_CONFIG_STATUS_CHECK(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_MAXIMUM_WAIT_US,
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_STATUS_ADDRESS,
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_BANK_MASK,
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
                OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_ENABLE_ADDRESS
            ),
            1U
        );
        if (result != OPEN_CFW_PWRCTRL_SRAM_CONFIG_SUCCESS) {
            return result;
        }

        if (
            (
                OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
                    OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_STATUS_ADDRESS
                ) & OPEN_CFW_PWRCTRL_SRAM_CONFIG_BANK_MASK
            ) != (
                OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
                    OPEN_CFW_PWRCTRL_SRAM_CONFIG_POWER_ENABLE_ADDRESS
                ) & OPEN_CFW_PWRCTRL_SRAM_CONFIG_BANK_MASK
            )
        ) {
            return OPEN_CFW_PWRCTRL_SRAM_CONFIG_FAILURE;
        }

        if (update_later != 0U) {
            (void)OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_UPDATE(
                OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_STIMULUS,
                0U,
                (const void *)0
            );
        }
    }

    register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS
    );
    register_value =
        (register_value & ~OPEN_CFW_PWRCTRL_SRAM_CONFIG_ACTIVE_MCU_MASK)
        | (((unsigned int)config[1] & 7U) << 3);
    OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS,
        register_value
    );

    register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS
    );
    register_value =
        (register_value & ~OPEN_CFW_PWRCTRL_SRAM_CONFIG_ACTIVE_GFX_MASK)
        | (((unsigned int)config[2] & 7U) << 9);
    OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS,
        register_value
    );

    register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS
    );
    register_value =
        (
            register_value
            & ~OPEN_CFW_PWRCTRL_SRAM_CONFIG_ACTIVE_DISPLAY_MASK
        ) | (((unsigned int)config[3] & 7U) << 12);
    OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS,
        register_value
    );

    if (config[4] == 0U) {
        register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS
        ) | 7U;
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS,
            register_value
        );
    } else if (config[4] == 1U) {
        register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS
        );
        register_value = (register_value & ~7U) | 6U;
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS,
            register_value
        );
    } else if (config[4] == 3U) {
        register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS
        );
        register_value = (register_value & ~7U) | 4U;
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS,
            register_value
        );
    } else if (config[4] == 7U) {
        register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS
        ) & ~7U;
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
            OPEN_CFW_PWRCTRL_SRAM_CONFIG_RETENTION_ADDRESS,
            register_value
        );
    }

    register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_ADDRESS
    ) & ~OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_GFX_MASK;
    OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_ADDRESS,
        register_value
    );

    register_value = OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_ADDRESS
    ) & ~OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_DISPLAY_MASK;
    OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(
        OPEN_CFW_PWRCTRL_SRAM_CONFIG_OVERRIDE_ADDRESS,
        register_value
    );

    return OPEN_CFW_PWRCTRL_SRAM_CONFIG_SUCCESS;
}
