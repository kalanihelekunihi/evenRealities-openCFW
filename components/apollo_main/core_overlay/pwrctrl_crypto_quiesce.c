/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 crypto power-down quiesce adaptation from AmbiqSuite SDK
 * 5.1.0. The reviewed stock function, sole caller, registers, and host
 * evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_MRAM_CONTROL_ADDRESS 0x40020180U
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_IDLE_ADDRESS 0x400C0A7CU
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_POWERDOWN_ADDRESS 0x400C0A80U

#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READY_MASK 0x00000100U
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_IDLE_MASK 0x00000001U
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_POWERDOWN_MASK 0x00000001U
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WAIT_US 100U
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_SUCCESS 0U

#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE_ENTRY 0x004807FDU

#ifndef OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READ
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WRITE
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE
typedef unsigned int (
    *open_cfw_pwrctrl_crypto_quiesce_status_change_function
)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE( \
    maximum_wait_us, address, mask, expected \
) \
    (((open_cfw_pwrctrl_crypto_quiesce_status_change_function) \
        OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE_ENTRY)( \
            (maximum_wait_us), \
            (address), \
            (mask), \
            (expected) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's private crypto_quiesce
 * helper at 0x0047F56E...0x0047F5B7.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_crypto_quiesce(void)
{
    unsigned int register_value;
    unsigned int result;

    result = OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE(
        OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WAIT_US,
        OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_MRAM_CONTROL_ADDRESS,
        OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READY_MASK,
        OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READY_MASK
    );
    if (result != OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_SUCCESS) {
        result = OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE(
            OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WAIT_US,
            OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_IDLE_ADDRESS,
            OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_IDLE_MASK,
            OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_IDLE_MASK
        );
        if (result == OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_SUCCESS) {
            register_value = OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READ(
                OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_POWERDOWN_ADDRESS
            );
            OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WRITE(
                OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_POWERDOWN_ADDRESS,
                register_value
                | OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_POWERDOWN_MASK
            );
            result = OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE(
                OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WAIT_US,
                OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_MRAM_CONTROL_ADDRESS,
                OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READY_MASK,
                OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READY_MASK
            );
        }
    }

    return result;
}
