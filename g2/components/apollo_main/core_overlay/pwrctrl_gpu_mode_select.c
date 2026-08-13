/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 GPU power-mode selector adaptation from AmbiqSuite
 * SDK 5.1.0. The reviewed stock function, callers, dependencies, fixed
 * registers/caches, and host evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_PWRCTRL_GPU_SELECT_VR_STATUS_ADDRESS 0x40021108U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_POWER_SWITCH_ADDRESS 0x40021090U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PERFORMANCE_ADDRESS 0x4002108CU
#define OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_ADDRESS 0x20074F60U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_ADDRESS 0x20074F61U

#define OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_LOW_POWER 0U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_HIGH_PERFORMANCE 3U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_SIMOBUCK_SHIFT 4U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_SIMOBUCK_MASK 0x3U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_SIMOBUCK_ACTIVE 3U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_VOLTAGE_MASK 0x1U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PERFORMANCE_MASK 0x3U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_GFX_PERIPHERAL 20U

#define OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_FAILURE 1U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_IN_USE 3U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_INVALID_ARGUMENT 6U
#define OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_INVALID_OPERATION 7U

#define OPEN_CFW_PWRCTRL_GPU_SELECT_PERIPH_ENABLED_ENTRY 0x0047F90DU
#define OPEN_CFW_PWRCTRL_GPU_SELECT_TON_UPDATE_ENTRY 0x004803C3U

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_READ
#define OPEN_CFW_PWRCTRL_GPU_SELECT_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_WRITE
#define OPEN_CFW_PWRCTRL_GPU_SELECT_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_READ
#define OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_READ() \
    (*(const volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_ADDRESS)
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_READ
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_READ() \
    (*(const volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_ADDRESS)
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_WRITE
#define OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_WRITE(value) \
    (*(volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_ADDRESS = \
            (unsigned char)(value))
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_WRITE
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_WRITE(value) \
    (*(volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_ADDRESS = \
            (unsigned char)(value))
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_PERIPH_ENABLED
typedef unsigned int (
    *open_cfw_pwrctrl_gpu_select_periph_enabled_function
)(
    unsigned int,
    unsigned char *
);
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PERIPH_ENABLED(id, enabled) \
    (((open_cfw_pwrctrl_gpu_select_periph_enabled_function) \
        OPEN_CFW_PWRCTRL_GPU_SELECT_PERIPH_ENABLED_ENTRY)( \
            (id), \
            (enabled) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_DISABLE
unsigned int open_cfw_lv_irq_disable(void);
#define OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_DISABLE() \
    open_cfw_lv_irq_disable()
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_pwrctrl_gpu_select_irq_restore_target(unsigned int primask)
{
    __asm__ volatile (
        "msr primask, %0"
        :
        : "r"(primask)
        : "memory"
    );
}
#define OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_RESTORE(primask) \
    open_cfw_pwrctrl_gpu_select_irq_restore_target(primask)
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_DELAY_US
void open_cfw_delay_us(unsigned int microseconds);
#define OPEN_CFW_PWRCTRL_GPU_SELECT_DELAY_US(microseconds) \
    open_cfw_delay_us(microseconds)
#endif

#ifndef OPEN_CFW_PWRCTRL_GPU_SELECT_TON_UPDATE
typedef void (*open_cfw_pwrctrl_gpu_select_ton_update_function)(
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_GPU_SELECT_TON_UPDATE(enabled, mode) \
    (((open_cfw_pwrctrl_gpu_select_ton_update_function) \
        OPEN_CFW_PWRCTRL_GPU_SELECT_TON_UPDATE_ENTRY)( \
            (enabled), \
            (mode) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_gpu_mode_select function at 0x0047F11C...0x0047F203.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_gpu_mode_select(
    unsigned int requested_mode
)
{
    unsigned int power_mode = requested_mode & 0xFFU;
    unsigned int register_value;
    unsigned int primask;
    unsigned char graphics_enabled;

    if (
        power_mode != OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_LOW_POWER
        && power_mode
            != OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_HIGH_PERFORMANCE
    ) {
        return OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_INVALID_ARGUMENT;
    }

    if (
        power_mode
            == OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_HIGH_PERFORMANCE
    ) {
        register_value = OPEN_CFW_PWRCTRL_GPU_SELECT_READ(
            OPEN_CFW_PWRCTRL_GPU_SELECT_VR_STATUS_ADDRESS
        );
        if (
            ((
                register_value
                >> OPEN_CFW_PWRCTRL_GPU_SELECT_SIMOBUCK_SHIFT
            ) & OPEN_CFW_PWRCTRL_GPU_SELECT_SIMOBUCK_MASK)
            != OPEN_CFW_PWRCTRL_GPU_SELECT_SIMOBUCK_ACTIVE
        ) {
            return OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_INVALID_OPERATION;
        }
    }

    graphics_enabled = 0U;
    if (
        OPEN_CFW_PWRCTRL_GPU_SELECT_PERIPH_ENABLED(
            OPEN_CFW_PWRCTRL_GPU_SELECT_GFX_PERIPHERAL,
            &graphics_enabled
        ) != OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_SUCCESS
    ) {
        return OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_FAILURE;
    }
    if (graphics_enabled != 0U) {
        return OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_IN_USE;
    }

    if (
        power_mode == OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_READ()
    ) {
        if (
            OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_READ()
            != OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_READ()
        ) {
            OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_WRITE(power_mode);
        }
        return OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_SUCCESS;
    }

    primask = OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_DISABLE();

    if (
        power_mode
            == OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_HIGH_PERFORMANCE
    ) {
        OPEN_CFW_PWRCTRL_GPU_SELECT_TON_UPDATE(1U, power_mode);
    }

    register_value = OPEN_CFW_PWRCTRL_GPU_SELECT_READ(
        OPEN_CFW_PWRCTRL_GPU_SELECT_POWER_SWITCH_ADDRESS
    );
    if (
        power_mode
            == OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_HIGH_PERFORMANCE
    ) {
        register_value |= OPEN_CFW_PWRCTRL_GPU_SELECT_VOLTAGE_MASK;
    }
    else {
        register_value &= ~OPEN_CFW_PWRCTRL_GPU_SELECT_VOLTAGE_MASK;
    }
    OPEN_CFW_PWRCTRL_GPU_SELECT_WRITE(
        OPEN_CFW_PWRCTRL_GPU_SELECT_POWER_SWITCH_ADDRESS,
        register_value
    );

    OPEN_CFW_PWRCTRL_GPU_SELECT_DELAY_US(1U);

    register_value = OPEN_CFW_PWRCTRL_GPU_SELECT_READ(
        OPEN_CFW_PWRCTRL_GPU_SELECT_PERFORMANCE_ADDRESS
    );
    register_value =
        (register_value
            & ~OPEN_CFW_PWRCTRL_GPU_SELECT_PERFORMANCE_MASK)
        | (power_mode & OPEN_CFW_PWRCTRL_GPU_SELECT_PERFORMANCE_MASK);
    OPEN_CFW_PWRCTRL_GPU_SELECT_WRITE(
        OPEN_CFW_PWRCTRL_GPU_SELECT_PERFORMANCE_ADDRESS,
        register_value
    );
    OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_WRITE(power_mode);
    OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_WRITE(power_mode);

    OPEN_CFW_PWRCTRL_GPU_SELECT_DELAY_US(6U);

    if (
        power_mode == OPEN_CFW_PWRCTRL_GPU_SELECT_MODE_LOW_POWER
    ) {
        OPEN_CFW_PWRCTRL_GPU_SELECT_TON_UPDATE(1U, power_mode);
    }

    OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_RESTORE(primask);
    return OPEN_CFW_PWRCTRL_GPU_SELECT_STATUS_SUCCESS;
}
