/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 miscellaneous power-control dispatcher adaptation from
 * AmbiqSuite SDK 5.1.0. Reviewed stock and SDK evidence is recorded in
 * EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_control_uintptr;

#define OPEN_CFW_PWRCTRL_CONTROL_VRSTATUS_ADDRESS 0x40021108U
#define OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK15_ADDRESS 0x40020378U
#define OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK0_ADDRESS 0x4002033CU
#define OPEN_CFW_PWRCTRL_CONTROL_VRCTRL_ADDRESS 0x40021100U
#define OPEN_CFW_PWRCTRL_CONTROL_XTALGENCTRL_ADDRESS 0x40020124U
#define OPEN_CFW_PWRCTRL_CONTROL_XTALCTRL_ADDRESS 0x40020120U
#define OPEN_CFW_PWRCTRL_CONTROL_DEMCR_ADDRESS 0xE000EDFCU
#define OPEN_CFW_PWRCTRL_CONTROL_DBGCTRL_ADDRESS 0x40020250U
#define OPEN_CFW_PWRCTRL_CONTROL_DEVPWREN_ADDRESS 0x40021004U
#define OPEN_CFW_PWRCTRL_CONTROL_AUDSSPWREN_ADDRESS 0x4002100CU

#define OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_STATE_MASK 0x00000030U
#define OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_STATE_ACTIVE 0x00000030U
#define OPEN_CFW_PWRCTRL_CONTROL_TRIM_LATCH_OVERRIDE 0x80000000U
#define OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_COMPENSATIONS 0x0000000FU
#define OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_ENABLE 0x00000001U
#define OPEN_CFW_PWRCTRL_CONTROL_XTAL_BIAS_MASK 0x000000FCU
#define OPEN_CFW_PWRCTRL_CONTROL_XTAL_BIAS_POWERDOWN 0x00000080U
#define OPEN_CFW_PWRCTRL_CONTROL_XTAL_POWERDOWN 0x00000001U
#define OPEN_CFW_PWRCTRL_CONTROL_TRACE_ENABLE 0x01000000U
#define OPEN_CFW_PWRCTRL_CONTROL_TPIU_TRACE_ENABLE 0x00000001U
#define OPEN_CFW_PWRCTRL_CONTROL_TPIU_CLOCK_SELECT 0x0000000EU

#define OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_INIT 0U
#define OPEN_CFW_PWRCTRL_CONTROL_CRYPTO_POWERDOWN 1U
#define OPEN_CFW_PWRCTRL_CONTROL_XTAL_POWERDOWN_DEEPSLEEP 2U
#define OPEN_CFW_PWRCTRL_CONTROL_DISABLE_ALL_PERIPHERALS 3U

#define OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_CONTROL_STATUS_INVALID_ARGUMENT 6U
#define OPEN_CFW_PWRCTRL_CONTROL_PERIPH_CRYPTO 0x17U
#define OPEN_CFW_PWRCTRL_CONTROL_MAX_WAIT_US 5U
#define OPEN_CFW_PWRCTRL_CONTROL_DEVPWR_ALL_MASK 0x3FFFFFFFU
#define OPEN_CFW_PWRCTRL_CONTROL_AUDSSPWR_ALL_MASK 0x000004C4U
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_DEVPWR_STIMULUS 3U
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_AUDSSPWR_STIMULUS 4U

#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE_ENTRY 0x00480359U
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE_ENTRY 0x0048036FU
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE_ENTRY 0x00480385U
#define OPEN_CFW_PWRCTRL_CONTROL_STATUS_CHECK_ENTRY 0x00480827U
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_UPDATE_ENTRY 0x00480313U

#ifndef OPEN_CFW_PWRCTRL_CONTROL_READ32
#define OPEN_CFW_PWRCTRL_CONTROL_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_control_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_WRITE32
#define OPEN_CFW_PWRCTRL_CONTROL_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_pwrctrl_control_uintptr)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE
typedef void (*open_cfw_pwrctrl_control_void_function)(void);
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE() \
    (((open_cfw_pwrctrl_control_void_function) \
        OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_BUCK_LDO_OVERRIDE_INIT
void open_cfw_pwrctrl_buck_ldo_override_init(void);
#define OPEN_CFW_PWRCTRL_CONTROL_BUCK_LDO_OVERRIDE_INIT() \
    open_cfw_pwrctrl_buck_ldo_override_init()
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE() \
    (((open_cfw_pwrctrl_control_void_function) \
        OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE() \
    (((open_cfw_pwrctrl_control_void_function) \
        OPEN_CFW_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_PERIPH_ENABLED
unsigned int open_cfw_pwrctrl_periph_enabled(
    unsigned int,
    unsigned char *
);
#define OPEN_CFW_PWRCTRL_CONTROL_PERIPH_ENABLED(peripheral, enabled) \
    open_cfw_pwrctrl_periph_enabled((peripheral), (enabled))
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_CRYPTO_QUIESCE
unsigned int open_cfw_pwrctrl_crypto_quiesce(void);
#define OPEN_CFW_PWRCTRL_CONTROL_CRYPTO_QUIESCE() \
    open_cfw_pwrctrl_crypto_quiesce()
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_PERIPH_DISABLE
unsigned int open_cfw_pwrctrl_periph_disable(unsigned int);
#define OPEN_CFW_PWRCTRL_CONTROL_PERIPH_DISABLE(peripheral) \
    open_cfw_pwrctrl_periph_disable(peripheral)
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_STATUS_CHECK
typedef unsigned int (*open_cfw_pwrctrl_control_status_check_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_CONTROL_STATUS_CHECK( \
    maximum_wait, address, mask, expected, wait \
) \
    (((open_cfw_pwrctrl_control_status_check_function) \
        OPEN_CFW_PWRCTRL_CONTROL_STATUS_CHECK_ENTRY)( \
            (maximum_wait), (address), (mask), (expected), (wait) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_CONTROL_SPOT_UPDATE
typedef unsigned int (*open_cfw_pwrctrl_control_spot_update_function)(
    unsigned int,
    unsigned int,
    unsigned int *
);
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_UPDATE(stimulus, enabled, status) \
    (((open_cfw_pwrctrl_control_spot_update_function) \
        OPEN_CFW_PWRCTRL_CONTROL_SPOT_UPDATE_ENTRY)( \
            (stimulus), (enabled), (status) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_control at 0x0047FEA0...0x0047FFB9.
 */
__attribute__((used, noinline))
unsigned int
open_cfw_pwrctrl_control(unsigned int control, void *arguments)
{
    unsigned int register_value;
    unsigned int status;
    unsigned int all_disabled_status;
    unsigned char enabled;

    (void)arguments;
    status = OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS;

    switch (control & 0xFFU) {
    case OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_INIT:
        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_VRSTATUS_ADDRESS
        );
        if (
            (register_value & OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_STATE_MASK)
            == OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_STATE_ACTIVE
        ) {
            return OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS;
        }

        OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE();
        OPEN_CFW_PWRCTRL_CONTROL_BUCK_LDO_OVERRIDE_INIT();

        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK15_ADDRESS
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK15_ADDRESS,
            register_value
            | OPEN_CFW_PWRCTRL_CONTROL_TRIM_LATCH_OVERRIDE
        );

        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK0_ADDRESS
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK0_ADDRESS,
            register_value
            | OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_COMPENSATIONS
        );

        OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE();
        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_VRCTRL_ADDRESS
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_VRCTRL_ADDRESS,
            register_value | OPEN_CFW_PWRCTRL_CONTROL_SIMOBUCK_ENABLE
        );
        OPEN_CFW_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE();
        break;

    case OPEN_CFW_PWRCTRL_CONTROL_CRYPTO_POWERDOWN:
        enabled = 0U;
        (void)OPEN_CFW_PWRCTRL_CONTROL_PERIPH_ENABLED(
            OPEN_CFW_PWRCTRL_CONTROL_PERIPH_CRYPTO,
            &enabled
        );
        if (enabled != 0U) {
            status = OPEN_CFW_PWRCTRL_CONTROL_CRYPTO_QUIESCE();
            if (status != OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS) {
                return status;
            }
            status = OPEN_CFW_PWRCTRL_CONTROL_PERIPH_DISABLE(
                OPEN_CFW_PWRCTRL_CONTROL_PERIPH_CRYPTO
            );
            if (status != OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS) {
                return status;
            }
        }
        break;

    case OPEN_CFW_PWRCTRL_CONTROL_XTAL_POWERDOWN_DEEPSLEEP:
        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_XTALGENCTRL_ADDRESS
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_XTALGENCTRL_ADDRESS,
            (
                register_value
                & ~OPEN_CFW_PWRCTRL_CONTROL_XTAL_BIAS_MASK
            ) | OPEN_CFW_PWRCTRL_CONTROL_XTAL_BIAS_POWERDOWN
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_XTALCTRL_ADDRESS,
            OPEN_CFW_PWRCTRL_CONTROL_XTAL_POWERDOWN
        );
        break;

    case OPEN_CFW_PWRCTRL_CONTROL_DISABLE_ALL_PERIPHERALS:
        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_DEMCR_ADDRESS
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_DEMCR_ADDRESS,
            register_value & ~OPEN_CFW_PWRCTRL_CONTROL_TRACE_ENABLE
        );

        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_DBGCTRL_ADDRESS
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_DBGCTRL_ADDRESS,
            register_value
            & ~OPEN_CFW_PWRCTRL_CONTROL_TPIU_TRACE_ENABLE
        );
        register_value = OPEN_CFW_PWRCTRL_CONTROL_READ32(
            OPEN_CFW_PWRCTRL_CONTROL_DBGCTRL_ADDRESS
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_DBGCTRL_ADDRESS,
            register_value
            & ~OPEN_CFW_PWRCTRL_CONTROL_TPIU_CLOCK_SELECT
        );

        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_DEVPWREN_ADDRESS,
            0U
        );
        OPEN_CFW_PWRCTRL_CONTROL_WRITE32(
            OPEN_CFW_PWRCTRL_CONTROL_AUDSSPWREN_ADDRESS,
            0U
        );

        status = OPEN_CFW_PWRCTRL_CONTROL_STATUS_CHECK(
            OPEN_CFW_PWRCTRL_CONTROL_MAX_WAIT_US,
            OPEN_CFW_PWRCTRL_CONTROL_DEVPWREN_ADDRESS,
            OPEN_CFW_PWRCTRL_CONTROL_DEVPWR_ALL_MASK,
            0U,
            1U
        );
        if (status != OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS) {
            return status;
        }

        all_disabled_status = 0U;
        status = OPEN_CFW_PWRCTRL_CONTROL_SPOT_UPDATE(
            OPEN_CFW_PWRCTRL_CONTROL_SPOT_DEVPWR_STIMULUS,
            0U,
            &all_disabled_status
        );
        if (status != OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS) {
            return status;
        }

        status = OPEN_CFW_PWRCTRL_CONTROL_STATUS_CHECK(
            OPEN_CFW_PWRCTRL_CONTROL_MAX_WAIT_US,
            OPEN_CFW_PWRCTRL_CONTROL_AUDSSPWREN_ADDRESS,
            OPEN_CFW_PWRCTRL_CONTROL_AUDSSPWR_ALL_MASK,
            0U,
            1U
        );
        if (status != OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS) {
            return status;
        }

        all_disabled_status = 0U;
        status = OPEN_CFW_PWRCTRL_CONTROL_SPOT_UPDATE(
            OPEN_CFW_PWRCTRL_CONTROL_SPOT_AUDSSPWR_STIMULUS,
            0U,
            &all_disabled_status
        );
        if (status != OPEN_CFW_PWRCTRL_CONTROL_STATUS_SUCCESS) {
            return status;
        }
        break;

    default:
        status = OPEN_CFW_PWRCTRL_CONTROL_STATUS_INVALID_ARGUMENT;
        break;
    }

    return status;
}
