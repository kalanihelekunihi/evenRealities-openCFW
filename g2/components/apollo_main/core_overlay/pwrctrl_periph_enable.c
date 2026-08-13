/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 peripheral-power enable adaptation from AmbiqSuite SDK
 * 5.1.0. The reviewed stock function, callers, registers, dependencies, and
 * host evidence are recorded in EVIDENCE.md.
 */

typedef struct open_cfw_pwrctrl_enable_descriptor {
    unsigned int power_enable_register;
    unsigned int peripheral_enable_mask;
    unsigned int power_status_register;
    unsigned int peripheral_status_mask;
} open_cfw_pwrctrl_enable_descriptor;

_Static_assert(
    sizeof(open_cfw_pwrctrl_enable_descriptor) == 16U,
    "Apollo510 peripheral-power descriptor ABI must remain 16 bytes"
);

#define OPEN_CFW_PWRCTRL_ENABLE_DEVICE_STATUS_ADDRESS 0x40021008U
#define OPEN_CFW_PWRCTRL_ENABLE_GPU_CURRENT_MODE_ADDRESS 0x20074F60U
#define OPEN_CFW_PWRCTRL_ENABLE_GPU_PREVIOUS_MODE_ADDRESS 0x20074F61U
#define OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_IDLE_ADDRESS 0x400C1F10U

#define OPEN_CFW_PWRCTRL_ENABLE_GPU_PERIPHERAL 20U
#define OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_PERIPHERAL 23U
#define OPEN_CFW_PWRCTRL_ENABLE_OTP_PERIPHERAL 29U
#define OPEN_CFW_PWRCTRL_ENABLE_AUDIO_FIRST_PERIPHERAL 30U
#define OPEN_CFW_PWRCTRL_ENABLE_GPU_HIGH_PERFORMANCE 3U
#define OPEN_CFW_PWRCTRL_ENABLE_OTP_STATUS_MASK 0x08000000U
#define OPEN_CFW_PWRCTRL_ENABLE_AUDIO_MONITOR_MASK 0x000004C4U
#define OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_IDLE_MASK 0x00000001U

#define OPEN_CFW_PWRCTRL_ENABLE_GPU_STATE_LOW_POWER 1U
#define OPEN_CFW_PWRCTRL_ENABLE_GPU_STATE_HIGH_PERFORMANCE 2U
#define OPEN_CFW_PWRCTRL_ENABLE_SPOT_GPU_STATE 1U
#define OPEN_CFW_PWRCTRL_ENABLE_SPOT_DEVICE_POWER 3U
#define OPEN_CFW_PWRCTRL_ENABLE_SPOT_AUDIO_POWER 4U
#define OPEN_CFW_PWRCTRL_ENABLE_CLOCK_HFRC 4U
#define OPEN_CFW_PWRCTRL_ENABLE_CLOCK_HFRC2 5U

#define OPEN_CFW_PWRCTRL_ENABLE_MAXIMUM_WAIT_US 5U
#define OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_WAIT_US 100U
#define OPEN_CFW_PWRCTRL_ENABLE_OTP_DELAY_US 100U
#define OPEN_CFW_PWRCTRL_ENABLE_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_ENABLE_FAILURE 1U

#define OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_POSTPONE_ENTRY 0x0048032DU
#define OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST_ENTRY 0x004C44BDU
#define OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE_ENTRY 0x00480313U
#define OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_PENDING_ENTRY 0x00480343U
#define OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHECK_ENTRY 0x00480827U
#define OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHANGE_ENTRY 0x004807FDU

#ifndef OPEN_CFW_PWRCTRL_ENABLE_READ
#define OPEN_CFW_PWRCTRL_ENABLE_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_WRITE
#define OPEN_CFW_PWRCTRL_ENABLE_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_MODE_READ
#define OPEN_CFW_PWRCTRL_ENABLE_MODE_READ(address) \
    (*(const volatile unsigned char *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_DESCRIPTOR_GET
typedef unsigned int (
    *open_cfw_pwrctrl_enable_descriptor_get_function
)(
    void *,
    unsigned int
);
unsigned int open_cfw_pwrctrl_enable_descriptor_get_target(
    void *,
    unsigned int
) __asm__("open_cfw_pwrctrl_peripheral_descriptor_get");
#define OPEN_CFW_PWRCTRL_ENABLE_DESCRIPTOR_GET(descriptor, peripheral) \
    (((open_cfw_pwrctrl_enable_descriptor_get_function) \
        open_cfw_pwrctrl_enable_descriptor_get_target)( \
            (descriptor), (peripheral) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_POSTPONE
typedef void (*open_cfw_pwrctrl_enable_void_function)(void);
#define OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_POSTPONE() \
    (((open_cfw_pwrctrl_enable_void_function) \
        OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_POSTPONE_ENTRY)())
#define OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_PENDING() \
    (((open_cfw_pwrctrl_enable_void_function) \
        OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_PENDING_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_GPU_MODE_SELECT
unsigned int open_cfw_pwrctrl_gpu_mode_select(unsigned int mode);
#define OPEN_CFW_PWRCTRL_ENABLE_GPU_MODE_SELECT(mode) \
    open_cfw_pwrctrl_gpu_mode_select(mode)
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST
typedef unsigned int (*open_cfw_pwrctrl_enable_clock_function)(
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST(clock, user) \
    (((open_cfw_pwrctrl_enable_clock_function) \
        OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST_ENTRY)((clock), (user)))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE
typedef unsigned int (*open_cfw_pwrctrl_enable_spot_function)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE(stimulus, enabled, value) \
    (((open_cfw_pwrctrl_enable_spot_function) \
        OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE_ENTRY)( \
            (stimulus), (enabled), (value) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_IRQ_DISABLE
unsigned int open_cfw_lv_irq_disable(void);
#define OPEN_CFW_PWRCTRL_ENABLE_IRQ_DISABLE() open_cfw_lv_irq_disable()
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_IRQ_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_pwrctrl_enable_irq_restore_target(unsigned int primask)
{
    __asm__ volatile (
        "msr primask, %0"
        :
        : "r"(primask)
        : "memory"
    );
}
#define OPEN_CFW_PWRCTRL_ENABLE_IRQ_RESTORE(primask) \
    open_cfw_pwrctrl_enable_irq_restore_target(primask)
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHECK
typedef unsigned int (*open_cfw_pwrctrl_enable_status_check_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHECK( \
    wait, address, mask, expected, equal \
) \
    (((open_cfw_pwrctrl_enable_status_check_function) \
        OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHECK_ENTRY)( \
            (wait), (address), (mask), (expected), (equal) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHANGE
typedef unsigned int (*open_cfw_pwrctrl_enable_status_change_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHANGE(wait, address, mask, expected) \
    (((open_cfw_pwrctrl_enable_status_change_function) \
        OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHANGE_ENTRY)( \
            (wait), (address), (mask), (expected) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_ENABLE_DELAY_US
void open_cfw_delay_us(unsigned int microseconds);
#define OPEN_CFW_PWRCTRL_ENABLE_DELAY_US(microseconds) \
    open_cfw_delay_us(microseconds)
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_periph_enable at 0x0047F5B8...0x0047F6F1.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_periph_enable(unsigned int peripheral)
{
    open_cfw_pwrctrl_enable_descriptor descriptor;
    unsigned int peripheral_id = peripheral & 0xFFU;
    unsigned int primask;
    unsigned int result;
    unsigned int value;

    result = OPEN_CFW_PWRCTRL_ENABLE_DESCRIPTOR_GET(
        &descriptor,
        peripheral_id
    );
    if (result != OPEN_CFW_PWRCTRL_ENABLE_SUCCESS) {
        return result;
    }

    if (
        (
            OPEN_CFW_PWRCTRL_ENABLE_READ(
                descriptor.power_enable_register
            ) & descriptor.peripheral_enable_mask
        ) != 0U
    ) {
        return OPEN_CFW_PWRCTRL_ENABLE_SUCCESS;
    }

    if (
        peripheral_id == OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_PERIPHERAL
        && (
            OPEN_CFW_PWRCTRL_ENABLE_READ(
                OPEN_CFW_PWRCTRL_ENABLE_DEVICE_STATUS_ADDRESS
            ) & OPEN_CFW_PWRCTRL_ENABLE_OTP_STATUS_MASK
        ) == 0U
    ) {
        return OPEN_CFW_PWRCTRL_ENABLE_FAILURE;
    }

    OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_POSTPONE();

    if (peripheral_id == OPEN_CFW_PWRCTRL_ENABLE_GPU_PERIPHERAL) {
        unsigned char gpu_state;

        if (
            OPEN_CFW_PWRCTRL_ENABLE_MODE_READ(
                OPEN_CFW_PWRCTRL_ENABLE_GPU_PREVIOUS_MODE_ADDRESS
            ) == OPEN_CFW_PWRCTRL_ENABLE_GPU_HIGH_PERFORMANCE
        ) {
            (void)OPEN_CFW_PWRCTRL_ENABLE_GPU_MODE_SELECT(
                OPEN_CFW_PWRCTRL_ENABLE_GPU_HIGH_PERFORMANCE
            );
        }

        (void)OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST(
            OPEN_CFW_PWRCTRL_ENABLE_CLOCK_HFRC,
            peripheral_id
        );
        if (
            OPEN_CFW_PWRCTRL_ENABLE_MODE_READ(
                OPEN_CFW_PWRCTRL_ENABLE_GPU_CURRENT_MODE_ADDRESS
            ) == OPEN_CFW_PWRCTRL_ENABLE_GPU_HIGH_PERFORMANCE
        ) {
            (void)OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST(
                OPEN_CFW_PWRCTRL_ENABLE_CLOCK_HFRC2,
                peripheral_id
            );
        }

        gpu_state =
            OPEN_CFW_PWRCTRL_ENABLE_MODE_READ(
                OPEN_CFW_PWRCTRL_ENABLE_GPU_CURRENT_MODE_ADDRESS
            ) == 0U
            ? OPEN_CFW_PWRCTRL_ENABLE_GPU_STATE_LOW_POWER
            : OPEN_CFW_PWRCTRL_ENABLE_GPU_STATE_HIGH_PERFORMANCE;
        (void)OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE(
            OPEN_CFW_PWRCTRL_ENABLE_SPOT_GPU_STATE,
            1U,
            &gpu_state
        );
    }
    else {
        if (
            (descriptor.peripheral_enable_mask << 2U) != 0U
            && peripheral_id
                < OPEN_CFW_PWRCTRL_ENABLE_AUDIO_FIRST_PERIPHERAL
        ) {
            (void)OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE(
                OPEN_CFW_PWRCTRL_ENABLE_SPOT_DEVICE_POWER,
                1U,
                &descriptor.peripheral_status_mask
            );
        }
        if (
            (
                descriptor.peripheral_enable_mask
                & OPEN_CFW_PWRCTRL_ENABLE_AUDIO_MONITOR_MASK
            ) != 0U
            && peripheral_id
                >= OPEN_CFW_PWRCTRL_ENABLE_AUDIO_FIRST_PERIPHERAL
        ) {
            (void)OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE(
                OPEN_CFW_PWRCTRL_ENABLE_SPOT_AUDIO_POWER,
                1U,
                &descriptor.peripheral_status_mask
            );
        }
    }

    primask = OPEN_CFW_PWRCTRL_ENABLE_IRQ_DISABLE();
    value = OPEN_CFW_PWRCTRL_ENABLE_READ(
        descriptor.power_enable_register
    );
    OPEN_CFW_PWRCTRL_ENABLE_WRITE(
        descriptor.power_enable_register,
        value | descriptor.peripheral_enable_mask
    );
    OPEN_CFW_PWRCTRL_ENABLE_IRQ_RESTORE(primask);

    OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_PENDING();

    result = OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHECK(
        OPEN_CFW_PWRCTRL_ENABLE_MAXIMUM_WAIT_US,
        descriptor.power_status_register,
        descriptor.peripheral_status_mask,
        descriptor.peripheral_status_mask,
        1U
    );
    if (result != OPEN_CFW_PWRCTRL_ENABLE_SUCCESS) {
        return result;
    }

    if (peripheral_id == OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_PERIPHERAL) {
        result = OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHANGE(
            OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_WAIT_US,
            OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_IDLE_ADDRESS,
            OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_IDLE_MASK,
            OPEN_CFW_PWRCTRL_ENABLE_CRYPTO_IDLE_MASK
        );
        if (result != OPEN_CFW_PWRCTRL_ENABLE_SUCCESS) {
            return result;
        }
        (void)OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST(
            OPEN_CFW_PWRCTRL_ENABLE_CLOCK_HFRC,
            peripheral_id
        );
    }

    if (peripheral_id == OPEN_CFW_PWRCTRL_ENABLE_OTP_PERIPHERAL) {
        OPEN_CFW_PWRCTRL_ENABLE_DELAY_US(
            OPEN_CFW_PWRCTRL_ENABLE_OTP_DELAY_US
        );
    }

    return (
        OPEN_CFW_PWRCTRL_ENABLE_READ(
            descriptor.power_status_register
        ) & descriptor.peripheral_status_mask
    ) != 0U
        ? OPEN_CFW_PWRCTRL_ENABLE_SUCCESS
        : OPEN_CFW_PWRCTRL_ENABLE_FAILURE;
}
