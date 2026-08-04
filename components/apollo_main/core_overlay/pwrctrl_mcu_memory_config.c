/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 MCU memory-power configuration adaptation from
 * AmbiqSuite SDK 5.1.0. The reviewed stock function, sole caller,
 * dependencies, fixed registers/cache, and host evidence are recorded in
 * EVIDENCE.md.
 */

#define OPEN_CFW_PWRCTRL_MEMORY_CURRENT_ROM_MODE_ADDRESS 0x20074F62U
#define OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS 0x40021014U
#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS 0x40021018U
#define OPEN_CFW_PWRCTRL_MEMORY_RETENTION_ADDRESS 0x4002101CU
#define OPEN_CFW_PWRCTRL_MEMORY_DEVICE_ENABLE_ADDRESS 0x40021004U
#define OPEN_CFW_PWRCTRL_MEMORY_DEVICE_STATUS_ADDRESS 0x40021008U
#define OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK_ADDRESS 0x40020284U

#define OPEN_CFW_PWRCTRL_MEMORY_CONFIG_ROM_OFFSET 0U
#define OPEN_CFW_PWRCTRL_MEMORY_CONFIG_TCM_OFFSET 1U
#define OPEN_CFW_PWRCTRL_MEMORY_CONFIG_RETAIN_TCM_OFFSET 2U
#define OPEN_CFW_PWRCTRL_MEMORY_CONFIG_NVM_OFFSET 3U
#define OPEN_CFW_PWRCTRL_MEMORY_CONFIG_KEEP_NVM_OFFSET 4U

#define OPEN_CFW_PWRCTRL_MEMORY_ROM_ALWAYS_ON 0U
#define OPEN_CFW_PWRCTRL_MEMORY_NVM0_ONLY 1U
#define OPEN_CFW_PWRCTRL_MEMORY_NVM0_AND_NVM1 3U
#define OPEN_CFW_PWRCTRL_MEMORY_TCM_RETAIN 0U
#define OPEN_CFW_PWRCTRL_MEMORY_TCM_NO_RETAIN 1U

#define OPEN_CFW_PWRCTRL_MEMORY_ENABLE_TCM_MASK 0x07U
#define OPEN_CFW_PWRCTRL_MEMORY_ENABLE_NVM0 0x08U
#define OPEN_CFW_PWRCTRL_MEMORY_ENABLE_NVM1 0x10U
#define OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ROM 0x20U
#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM0 0x08U
#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM1 0x40U
#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_ROM 0x80U
#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_MASK 0xCFU
#define OPEN_CFW_PWRCTRL_MEMORY_RETENTION_TCM 0x01U
#define OPEN_CFW_PWRCTRL_MEMORY_RETENTION_NVM 0x02U
#define OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK 0x01U
#define OPEN_CFW_PWRCTRL_MEMORY_DEVICE_OTP (1U << 27U)

#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_FAILURE 1U
#define OPEN_CFW_PWRCTRL_MEMORY_STATUS_OUT_OF_RANGE 5U
#define OPEN_CFW_PWRCTRL_MEMORY_MAXIMUM_WAIT_US 5U
#define OPEN_CFW_PWRCTRL_MEMORY_SPOT_MEMORY_STIMULUS 5U

#define OPEN_CFW_PWRCTRL_MEMORY_DELAY_STATUS_ENTRY 0x00480827U
#define OPEN_CFW_PWRCTRL_MEMORY_SPOT_UPDATE_ENTRY 0x00480313U

#ifndef OPEN_CFW_PWRCTRL_MEMORY_READ
#define OPEN_CFW_PWRCTRL_MEMORY_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_MEMORY_WRITE
#define OPEN_CFW_PWRCTRL_MEMORY_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_MEMORY_ROM_MODE_WRITE
#define OPEN_CFW_PWRCTRL_MEMORY_ROM_MODE_WRITE(value) \
    (*(volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_MEMORY_CURRENT_ROM_MODE_ADDRESS = \
            (unsigned char)(value))
#endif

#ifndef OPEN_CFW_PWRCTRL_MEMORY_DELAY_STATUS
typedef unsigned int (
    *open_cfw_pwrctrl_memory_delay_status_function
)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_MEMORY_DELAY_STATUS( \
    maximum_wait, address, mask, expected, wait_for_match \
) \
    (((open_cfw_pwrctrl_memory_delay_status_function) \
        OPEN_CFW_PWRCTRL_MEMORY_DELAY_STATUS_ENTRY)( \
            (maximum_wait), \
            (address), \
            (mask), \
            (expected), \
            (wait_for_match) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_MEMORY_SPOT_UPDATE
typedef unsigned int (
    *open_cfw_pwrctrl_memory_spot_update_function
)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_PWRCTRL_MEMORY_SPOT_UPDATE(stimulus, enabled, value) \
    (((open_cfw_pwrctrl_memory_spot_update_function) \
        OPEN_CFW_PWRCTRL_MEMORY_SPOT_UPDATE_ENTRY)( \
            (stimulus), \
            (enabled), \
            (value) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_mcu_memory_config function at
 * 0x0047F204...0x0047F3C5.
 *
 * The shipped ABI uses short enums, so the five configuration members are
 * consumed as bytes at offsets zero through four.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_mcu_memory_config(
    const void *configuration
)
{
    const unsigned char *config =
        (const unsigned char *)configuration;
    unsigned int desired_enable = 0U;
    unsigned int desired_status = 0U;
    unsigned int status_after_disables;
    unsigned int register_value;
    unsigned int result;
    unsigned char forced_axi_clock = 0U;
    unsigned char rom_mode = config[
        OPEN_CFW_PWRCTRL_MEMORY_CONFIG_ROM_OFFSET
    ];
    unsigned char tcm_config = config[
        OPEN_CFW_PWRCTRL_MEMORY_CONFIG_TCM_OFFSET
    ];
    unsigned char retain_tcm = config[
        OPEN_CFW_PWRCTRL_MEMORY_CONFIG_RETAIN_TCM_OFFSET
    ];
    unsigned char nvm_config = config[
        OPEN_CFW_PWRCTRL_MEMORY_CONFIG_NVM_OFFSET
    ];
    unsigned char keep_nvm = config[
        OPEN_CFW_PWRCTRL_MEMORY_CONFIG_KEEP_NVM_OFFSET
    ];

    OPEN_CFW_PWRCTRL_MEMORY_ROM_MODE_WRITE(rom_mode);

    if (rom_mode == OPEN_CFW_PWRCTRL_MEMORY_ROM_ALWAYS_ON) {
        desired_enable |= OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ROM;
        desired_status |= OPEN_CFW_PWRCTRL_MEMORY_STATUS_ROM;
    }

    tcm_config &= OPEN_CFW_PWRCTRL_MEMORY_ENABLE_TCM_MASK;
    desired_enable |= tcm_config;
    desired_status |= tcm_config;

    if (nvm_config == OPEN_CFW_PWRCTRL_MEMORY_NVM0_ONLY) {
        desired_enable |= OPEN_CFW_PWRCTRL_MEMORY_ENABLE_NVM0;
        desired_status |= OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM0;
    }
    else if (
        nvm_config == OPEN_CFW_PWRCTRL_MEMORY_NVM0_AND_NVM1
    ) {
        desired_enable |=
            OPEN_CFW_PWRCTRL_MEMORY_ENABLE_NVM0
            | OPEN_CFW_PWRCTRL_MEMORY_ENABLE_NVM1;
        desired_status |=
            OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM0
            | OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM1;
    }

    if (
        nvm_config == OPEN_CFW_PWRCTRL_MEMORY_NVM0_AND_NVM1
        && (
            OPEN_CFW_PWRCTRL_MEMORY_READ(
                OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
            ) & (
                OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM0
                | OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM1
            )
        ) == OPEN_CFW_PWRCTRL_MEMORY_STATUS_NVM0
    ) {
        register_value = OPEN_CFW_PWRCTRL_MEMORY_READ(
            OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK_ADDRESS
        );
        OPEN_CFW_PWRCTRL_MEMORY_WRITE(
            OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK_ADDRESS,
            register_value | OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK
        );
        forced_axi_clock = 1U;
    }

    if (
        desired_status != OPEN_CFW_PWRCTRL_MEMORY_READ(
            OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
        )
    ) {
        status_after_disables =
            OPEN_CFW_PWRCTRL_MEMORY_READ(
                OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
            ) & desired_status;

        register_value = OPEN_CFW_PWRCTRL_MEMORY_READ(
            OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS
        );
        OPEN_CFW_PWRCTRL_MEMORY_WRITE(
            OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS,
            register_value & desired_enable
        );

        result = OPEN_CFW_PWRCTRL_MEMORY_DELAY_STATUS(
            OPEN_CFW_PWRCTRL_MEMORY_MAXIMUM_WAIT_US,
            OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS,
            OPEN_CFW_PWRCTRL_MEMORY_STATUS_MASK,
            status_after_disables,
            1U
        );
        if (result != OPEN_CFW_PWRCTRL_MEMORY_STATUS_SUCCESS) {
            return result;
        }

        (void)OPEN_CFW_PWRCTRL_MEMORY_SPOT_UPDATE(
            OPEN_CFW_PWRCTRL_MEMORY_SPOT_MEMORY_STIMULUS,
            1U,
            &desired_status
        );

        OPEN_CFW_PWRCTRL_MEMORY_WRITE(
            OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS,
            desired_enable
        );

        result = OPEN_CFW_PWRCTRL_MEMORY_DELAY_STATUS(
            OPEN_CFW_PWRCTRL_MEMORY_MAXIMUM_WAIT_US,
            OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS,
            OPEN_CFW_PWRCTRL_MEMORY_STATUS_MASK,
            desired_status,
            1U
        );

        if (forced_axi_clock != 0U) {
            register_value = OPEN_CFW_PWRCTRL_MEMORY_READ(
                OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK_ADDRESS
            );
            OPEN_CFW_PWRCTRL_MEMORY_WRITE(
                OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK_ADDRESS,
                register_value
                    & ~OPEN_CFW_PWRCTRL_MEMORY_FORCE_AXI_CLOCK
            );
        }

        if (result != OPEN_CFW_PWRCTRL_MEMORY_STATUS_SUCCESS) {
            return result;
        }

        if (
            (
                OPEN_CFW_PWRCTRL_MEMORY_READ(
                    OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
                ) & OPEN_CFW_PWRCTRL_MEMORY_ENABLE_TCM_MASK
            ) != (
                OPEN_CFW_PWRCTRL_MEMORY_READ(
                    OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS
                ) & OPEN_CFW_PWRCTRL_MEMORY_ENABLE_TCM_MASK
            )
            || (
                (
                    OPEN_CFW_PWRCTRL_MEMORY_READ(
                        OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
                    ) >> 3U
                ) & 1U
            ) != (
                (
                    OPEN_CFW_PWRCTRL_MEMORY_READ(
                        OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS
                    ) >> 3U
                ) & 1U
            )
            || (
                (
                    (
                        OPEN_CFW_PWRCTRL_MEMORY_READ(
                            OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
                        ) >> 3U
                    ) & 1U
                ) & (
                    (
                        OPEN_CFW_PWRCTRL_MEMORY_READ(
                            OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
                        ) >> 6U
                    ) & 1U
                )
            ) != (
                (
                    OPEN_CFW_PWRCTRL_MEMORY_READ(
                        OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS
                    ) >> 4U
                ) & 1U
            )
            || (
                (
                    OPEN_CFW_PWRCTRL_MEMORY_READ(
                        OPEN_CFW_PWRCTRL_MEMORY_STATUS_ADDRESS
                    ) >> 7U
                ) & 1U
            ) != (
                (
                    OPEN_CFW_PWRCTRL_MEMORY_READ(
                        OPEN_CFW_PWRCTRL_MEMORY_ENABLE_ADDRESS
                    ) >> 5U
                ) & 1U
            )
            || (
                OPEN_CFW_PWRCTRL_MEMORY_READ(
                    OPEN_CFW_PWRCTRL_MEMORY_DEVICE_STATUS_ADDRESS
                ) & OPEN_CFW_PWRCTRL_MEMORY_DEVICE_OTP
            ) != (
                OPEN_CFW_PWRCTRL_MEMORY_READ(
                    OPEN_CFW_PWRCTRL_MEMORY_DEVICE_ENABLE_ADDRESS
                ) & OPEN_CFW_PWRCTRL_MEMORY_DEVICE_OTP
            )
        ) {
            return OPEN_CFW_PWRCTRL_MEMORY_STATUS_FAILURE;
        }
    }

    register_value = OPEN_CFW_PWRCTRL_MEMORY_READ(
        OPEN_CFW_PWRCTRL_MEMORY_RETENTION_ADDRESS
    );
    if (keep_nvm != 0U) {
        register_value &= ~OPEN_CFW_PWRCTRL_MEMORY_RETENTION_NVM;
    }
    else {
        register_value |= OPEN_CFW_PWRCTRL_MEMORY_RETENTION_NVM;
    }
    OPEN_CFW_PWRCTRL_MEMORY_WRITE(
        OPEN_CFW_PWRCTRL_MEMORY_RETENTION_ADDRESS,
        register_value
    );

    if (retain_tcm == OPEN_CFW_PWRCTRL_MEMORY_TCM_NO_RETAIN) {
        register_value = OPEN_CFW_PWRCTRL_MEMORY_READ(
            OPEN_CFW_PWRCTRL_MEMORY_RETENTION_ADDRESS
        );
        OPEN_CFW_PWRCTRL_MEMORY_WRITE(
            OPEN_CFW_PWRCTRL_MEMORY_RETENTION_ADDRESS,
            register_value | OPEN_CFW_PWRCTRL_MEMORY_RETENTION_TCM
        );
    }
    else if (retain_tcm == OPEN_CFW_PWRCTRL_MEMORY_TCM_RETAIN) {
        register_value = OPEN_CFW_PWRCTRL_MEMORY_READ(
            OPEN_CFW_PWRCTRL_MEMORY_RETENTION_ADDRESS
        );
        OPEN_CFW_PWRCTRL_MEMORY_WRITE(
            OPEN_CFW_PWRCTRL_MEMORY_RETENTION_ADDRESS,
            register_value & ~OPEN_CFW_PWRCTRL_MEMORY_RETENTION_TCM
        );
    }
    else {
        return OPEN_CFW_PWRCTRL_MEMORY_STATUS_OUT_OF_RANGE;
    }

    return OPEN_CFW_PWRCTRL_MEMORY_STATUS_SUCCESS;
}
