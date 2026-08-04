/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 MCU power-mode selector adaptation from AmbiqSuite
 * SDK 5.1.0. The reviewed stock function, sole caller, fixed registers,
 * and host behavioral evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_PWRCTRL_MCU_SELECT_PERFORMANCE_ADDRESS 0x40021000U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_VR_STATUS_ADDRESS 0x40021108U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_CURRENT_MODE_ADDRESS 0x20004538U

#define OPEN_CFW_PWRCTRL_MCU_SELECT_MODE_LOW_POWER 1U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_MODE_HIGH_PERFORMANCE 2U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_SIMOBUCK_STATUS_SHIFT 4U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_SIMOBUCK_STATUS_MASK 0x3U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_SIMOBUCK_ACTIVE 3U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_PERFORMANCE_STATUS_SHIFT 3U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_PERFORMANCE_STATUS_MASK 0x3U

#define OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_FAILURE 1U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_INVALID_ARGUMENT 6U
#define OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_INVALID_OPERATION 7U

#ifndef OPEN_CFW_PWRCTRL_MCU_SELECT_READ
#define OPEN_CFW_PWRCTRL_MCU_SELECT_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SELECT_CURRENT_MODE_READ
#define OPEN_CFW_PWRCTRL_MCU_SELECT_CURRENT_MODE_READ() \
    (*(const volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_MCU_SELECT_CURRENT_MODE_ADDRESS)
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SELECT_SWITCH
unsigned int open_cfw_pwrctrl_mcu_switch_sequence(
    unsigned int requested_mode
);
#define OPEN_CFW_PWRCTRL_MCU_SELECT_SWITCH(requested_mode) \
    open_cfw_pwrctrl_mcu_switch_sequence(requested_mode)
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_mcu_mode_select function at 0x0047F0A0...0x0047F107.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_mcu_mode_select(
    unsigned int requested_mode
)
{
    unsigned int power_mode = requested_mode & 0xFFU;
    unsigned int status;
    unsigned int register_value;

    if (
        power_mode != OPEN_CFW_PWRCTRL_MCU_SELECT_MODE_LOW_POWER
        && power_mode
            != OPEN_CFW_PWRCTRL_MCU_SELECT_MODE_HIGH_PERFORMANCE
    ) {
        return OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_INVALID_ARGUMENT;
    }

    if (
        power_mode
            == OPEN_CFW_PWRCTRL_MCU_SELECT_MODE_HIGH_PERFORMANCE
    ) {
        register_value = OPEN_CFW_PWRCTRL_MCU_SELECT_READ(
            OPEN_CFW_PWRCTRL_MCU_SELECT_VR_STATUS_ADDRESS
        );
        if (
            ((
                register_value
                >> OPEN_CFW_PWRCTRL_MCU_SELECT_SIMOBUCK_STATUS_SHIFT
            )
                & OPEN_CFW_PWRCTRL_MCU_SELECT_SIMOBUCK_STATUS_MASK)
            != OPEN_CFW_PWRCTRL_MCU_SELECT_SIMOBUCK_ACTIVE
        ) {
            return OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_INVALID_OPERATION;
        }
    }

    if (
        power_mode == OPEN_CFW_PWRCTRL_MCU_SELECT_CURRENT_MODE_READ()
    ) {
        return OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_SUCCESS;
    }

    status = OPEN_CFW_PWRCTRL_MCU_SELECT_SWITCH(power_mode);
    if (status != OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_SUCCESS) {
        return status;
    }

    register_value = OPEN_CFW_PWRCTRL_MCU_SELECT_READ(
        OPEN_CFW_PWRCTRL_MCU_SELECT_PERFORMANCE_ADDRESS
    );
    if (
        ((
            register_value
            >> OPEN_CFW_PWRCTRL_MCU_SELECT_PERFORMANCE_STATUS_SHIFT
        )
            & OPEN_CFW_PWRCTRL_MCU_SELECT_PERFORMANCE_STATUS_MASK)
        == power_mode
    ) {
        return OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_SUCCESS;
    }

    return OPEN_CFW_PWRCTRL_MCU_SELECT_STATUS_FAILURE;
}
