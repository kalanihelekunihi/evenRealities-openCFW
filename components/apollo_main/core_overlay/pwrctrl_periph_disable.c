/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 peripheral-power disable adaptation from AmbiqSuite SDK
 * 5.1.0. The reviewed stock function, callers, registers, dependencies, and
 * host evidence are recorded in EVIDENCE.md.
 */

typedef struct open_cfw_pwrctrl_disable_descriptor {
    unsigned int power_enable_register;
    unsigned int peripheral_enable_mask;
    unsigned int power_status_register;
    unsigned int peripheral_status_mask;
} open_cfw_pwrctrl_disable_descriptor;

_Static_assert(
    sizeof(open_cfw_pwrctrl_disable_descriptor) == 16U,
    "Apollo510 peripheral-power descriptor ABI must remain 16 bytes"
);

#define OPEN_CFW_PWRCTRL_DISABLE_CHIP_REVISION_ADDRESS 0x4002000CU
#define OPEN_CFW_PWRCTRL_DISABLE_DEVICE_STATUS_ADDRESS 0x40021008U
#define OPEN_CFW_PWRCTRL_DISABLE_OTP_STATUS_ADDRESS 0x40014AC4U
#define OPEN_CFW_PWRCTRL_DISABLE_DEMCR_ADDRESS 0xE000EDFCU
#define OPEN_CFW_PWRCTRL_DISABLE_DEBUG_CONTROL_ADDRESS 0x40020250U
#define OPEN_CFW_PWRCTRL_DISABLE_GPU_CURRENT_MODE_ADDRESS 0x20074F60U
#define OPEN_CFW_PWRCTRL_DISABLE_GPU_PREVIOUS_MODE_ADDRESS 0x20074F61U

#define OPEN_CFW_PWRCTRL_DISABLE_GPU_PERIPHERAL 20U
#define OPEN_CFW_PWRCTRL_DISABLE_CRYPTO_PERIPHERAL 23U
#define OPEN_CFW_PWRCTRL_DISABLE_DEBUG_PERIPHERAL 28U
#define OPEN_CFW_PWRCTRL_DISABLE_OTP_PERIPHERAL 29U
#define OPEN_CFW_PWRCTRL_DISABLE_AUDIO_FIRST_PERIPHERAL 30U

#define OPEN_CFW_PWRCTRL_DISABLE_FIRST_B1_REVISION 0x22U
#define OPEN_CFW_PWRCTRL_DISABLE_CRYPTO_STATUS_MASK 0x00200000U
#define OPEN_CFW_PWRCTRL_DISABLE_OTP_BUSY_MASK 0x00000001U
#define OPEN_CFW_PWRCTRL_DISABLE_DEMCR_TRACE_ENABLE_MASK 0x01000000U
#define OPEN_CFW_PWRCTRL_DISABLE_DEBUG_TRACE_ENABLE_MASK 0x00000001U
#define OPEN_CFW_PWRCTRL_DISABLE_DEBUG_CLOCK_MASK 0x0000000EU
#define OPEN_CFW_PWRCTRL_DISABLE_AUDIO_MONITOR_MASK 0x000004C4U

#define OPEN_CFW_PWRCTRL_DISABLE_GPU_LOW_POWER_MODE 0U
#define OPEN_CFW_PWRCTRL_DISABLE_GPU_HIGH_PERFORMANCE_MODE 3U
#define OPEN_CFW_PWRCTRL_DISABLE_GPU_STATE_OFF 0U
#define OPEN_CFW_PWRCTRL_DISABLE_SPOT_GPU_STATE 1U
#define OPEN_CFW_PWRCTRL_DISABLE_SPOT_DEVICE_POWER 3U
#define OPEN_CFW_PWRCTRL_DISABLE_SPOT_AUDIO_POWER 4U
#define OPEN_CFW_PWRCTRL_DISABLE_CLOCK_HFRC 4U

#define OPEN_CFW_PWRCTRL_DISABLE_MAXIMUM_WAIT_US 5U
#define OPEN_CFW_PWRCTRL_DISABLE_OTP_MAXIMUM_WAIT_US 100000U
#define OPEN_CFW_PWRCTRL_DISABLE_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_DISABLE_IN_USE 3U

#define OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_POSTPONE_ENTRY 0x0048032DU
#define OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE_ENTRY 0x00480313U
#define OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_PENDING_ENTRY 0x00480343U
#define OPEN_CFW_PWRCTRL_DISABLE_STATUS_CHECK_ENTRY 0x00480827U
#define OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ENTRY 0x004C4531U
#define OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ALL_ENTRY 0x004C45A5U

#ifndef OPEN_CFW_PWRCTRL_DISABLE_READ
#define OPEN_CFW_PWRCTRL_DISABLE_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_WRITE
#define OPEN_CFW_PWRCTRL_DISABLE_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_MODE_READ
#define OPEN_CFW_PWRCTRL_DISABLE_MODE_READ(address) \
    (*(const volatile unsigned char *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_MODE_WRITE
#define OPEN_CFW_PWRCTRL_DISABLE_MODE_WRITE(address, value) \
    (*(volatile unsigned char *)(address) = (unsigned char)(value))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_DESCRIPTOR_GET
unsigned int open_cfw_pwrctrl_disable_descriptor_get_target(
    void *,
    unsigned int
) __asm__("open_cfw_pwrctrl_peripheral_descriptor_get");
#define OPEN_CFW_PWRCTRL_DISABLE_DESCRIPTOR_GET(descriptor, peripheral) \
    open_cfw_pwrctrl_disable_descriptor_get_target( \
        (descriptor), (peripheral) \
    )
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_POSTPONE
typedef void (*open_cfw_pwrctrl_disable_void_function)(void);
#define OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_POSTPONE() \
    (((open_cfw_pwrctrl_disable_void_function) \
        OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_POSTPONE_ENTRY)())
#define OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_PENDING() \
    (((open_cfw_pwrctrl_disable_void_function) \
        OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_PENDING_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_IRQ_DISABLE
unsigned int open_cfw_lv_irq_disable(void);
#define OPEN_CFW_PWRCTRL_DISABLE_IRQ_DISABLE() open_cfw_lv_irq_disable()
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_IRQ_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_pwrctrl_disable_irq_restore_target(unsigned int primask)
{
    __asm__ volatile (
        "msr primask, %0"
        :
        : "r"(primask)
        : "memory"
    );
}
#define OPEN_CFW_PWRCTRL_DISABLE_IRQ_RESTORE(primask) \
    open_cfw_pwrctrl_disable_irq_restore_target(primask)
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_MASK_CHECK
unsigned int open_cfw_pwrctrl_periph_disable_mask_check(
    unsigned int peripheral
);
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_CHECK(peripheral) \
    open_cfw_pwrctrl_periph_disable_mask_check(peripheral)
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_STATUS_CHECK
typedef unsigned int (*open_cfw_pwrctrl_disable_status_check_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_DISABLE_STATUS_CHECK( \
    wait, address, mask, expected, equal \
) \
    (((open_cfw_pwrctrl_disable_status_check_function) \
        OPEN_CFW_PWRCTRL_DISABLE_STATUS_CHECK_ENTRY)( \
            (wait), (address), (mask), (expected), (equal) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_GPU_MODE_SELECT
unsigned int open_cfw_pwrctrl_gpu_mode_select(unsigned int mode);
#define OPEN_CFW_PWRCTRL_DISABLE_GPU_MODE_SELECT(mode) \
    open_cfw_pwrctrl_gpu_mode_select(mode)
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE
typedef unsigned int (*open_cfw_pwrctrl_disable_spot_function)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE(stimulus, enabled, value) \
    (((open_cfw_pwrctrl_disable_spot_function) \
        OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE_ENTRY)( \
            (stimulus), (enabled), (value) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE
typedef unsigned int (*open_cfw_pwrctrl_disable_clock_function)(
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE(clock, user) \
    (((open_cfw_pwrctrl_disable_clock_function) \
        OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ENTRY)((clock), (user)))
#endif

#ifndef OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ALL
typedef unsigned int (*open_cfw_pwrctrl_disable_clock_all_function)(
    unsigned int
);
#define OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ALL(user) \
    (((open_cfw_pwrctrl_disable_clock_all_function) \
        OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ALL_ENTRY)(user))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_periph_disable at 0x0047F7AE...0x0047F90B.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_periph_disable(unsigned int peripheral)
{
    open_cfw_pwrctrl_disable_descriptor descriptor;
    unsigned int peripheral_id = peripheral & 0xFFU;
    unsigned int primask;
    unsigned int result;
    unsigned int value;

    result = OPEN_CFW_PWRCTRL_DISABLE_DESCRIPTOR_GET(
        &descriptor,
        peripheral_id
    );
    if (result != OPEN_CFW_PWRCTRL_DISABLE_SUCCESS) {
        return result;
    }

    if (
        (
            OPEN_CFW_PWRCTRL_DISABLE_READ(
                descriptor.power_enable_register
            ) & descriptor.peripheral_enable_mask
        ) == 0U
    ) {
        return OPEN_CFW_PWRCTRL_DISABLE_SUCCESS;
    }

    if (peripheral_id == OPEN_CFW_PWRCTRL_DISABLE_OTP_PERIPHERAL) {
        if (
            (
                OPEN_CFW_PWRCTRL_DISABLE_READ(
                    OPEN_CFW_PWRCTRL_DISABLE_CHIP_REVISION_ADDRESS
                ) & 0xFFU
            ) < OPEN_CFW_PWRCTRL_DISABLE_FIRST_B1_REVISION
            && (
                OPEN_CFW_PWRCTRL_DISABLE_READ(
                    OPEN_CFW_PWRCTRL_DISABLE_DEVICE_STATUS_ADDRESS
                ) & OPEN_CFW_PWRCTRL_DISABLE_CRYPTO_STATUS_MASK
            ) != 0U
        ) {
            return OPEN_CFW_PWRCTRL_DISABLE_IN_USE;
        }

        result = OPEN_CFW_PWRCTRL_DISABLE_STATUS_CHECK(
            OPEN_CFW_PWRCTRL_DISABLE_OTP_MAXIMUM_WAIT_US,
            OPEN_CFW_PWRCTRL_DISABLE_OTP_STATUS_ADDRESS,
            OPEN_CFW_PWRCTRL_DISABLE_OTP_BUSY_MASK,
            0U,
            1U
        );
        if (result != OPEN_CFW_PWRCTRL_DISABLE_SUCCESS) {
            return result;
        }
    }

    if (peripheral_id == OPEN_CFW_PWRCTRL_DISABLE_DEBUG_PERIPHERAL) {
        value = OPEN_CFW_PWRCTRL_DISABLE_READ(
            OPEN_CFW_PWRCTRL_DISABLE_DEMCR_ADDRESS
        );
        OPEN_CFW_PWRCTRL_DISABLE_WRITE(
            OPEN_CFW_PWRCTRL_DISABLE_DEMCR_ADDRESS,
            value & ~OPEN_CFW_PWRCTRL_DISABLE_DEMCR_TRACE_ENABLE_MASK
        );

        value = OPEN_CFW_PWRCTRL_DISABLE_READ(
            OPEN_CFW_PWRCTRL_DISABLE_DEBUG_CONTROL_ADDRESS
        );
        OPEN_CFW_PWRCTRL_DISABLE_WRITE(
            OPEN_CFW_PWRCTRL_DISABLE_DEBUG_CONTROL_ADDRESS,
            value & ~OPEN_CFW_PWRCTRL_DISABLE_DEBUG_TRACE_ENABLE_MASK
        );
        value = OPEN_CFW_PWRCTRL_DISABLE_READ(
            OPEN_CFW_PWRCTRL_DISABLE_DEBUG_CONTROL_ADDRESS
        );
        OPEN_CFW_PWRCTRL_DISABLE_WRITE(
            OPEN_CFW_PWRCTRL_DISABLE_DEBUG_CONTROL_ADDRESS,
            value & ~OPEN_CFW_PWRCTRL_DISABLE_DEBUG_CLOCK_MASK
        );
    }

    OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_POSTPONE();

    primask = OPEN_CFW_PWRCTRL_DISABLE_IRQ_DISABLE();
    value = OPEN_CFW_PWRCTRL_DISABLE_READ(
        descriptor.power_enable_register
    );
    OPEN_CFW_PWRCTRL_DISABLE_WRITE(
        descriptor.power_enable_register,
        value & ~descriptor.peripheral_enable_mask
    );
    OPEN_CFW_PWRCTRL_DISABLE_IRQ_RESTORE(primask);

    if (OPEN_CFW_PWRCTRL_DISABLE_MASK_CHECK(peripheral_id) != 0U) {
        result = OPEN_CFW_PWRCTRL_DISABLE_STATUS_CHECK(
            OPEN_CFW_PWRCTRL_DISABLE_MAXIMUM_WAIT_US,
            descriptor.power_status_register,
            descriptor.peripheral_status_mask,
            descriptor.peripheral_status_mask,
            0U
        );
        if (result == OPEN_CFW_PWRCTRL_DISABLE_SUCCESS) {
            if (
                peripheral_id
                == OPEN_CFW_PWRCTRL_DISABLE_CRYPTO_PERIPHERAL
            ) {
                (void)OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE(
                    OPEN_CFW_PWRCTRL_DISABLE_CLOCK_HFRC,
                    peripheral_id
                );
            }

            if (
                peripheral_id
                == OPEN_CFW_PWRCTRL_DISABLE_GPU_PERIPHERAL
            ) {
                unsigned char gpu_state =
                    OPEN_CFW_PWRCTRL_DISABLE_GPU_STATE_OFF;

                if (
                    OPEN_CFW_PWRCTRL_DISABLE_MODE_READ(
                        OPEN_CFW_PWRCTRL_DISABLE_GPU_CURRENT_MODE_ADDRESS
                    )
                    == OPEN_CFW_PWRCTRL_DISABLE_GPU_HIGH_PERFORMANCE_MODE
                ) {
                    (void)OPEN_CFW_PWRCTRL_DISABLE_GPU_MODE_SELECT(
                        OPEN_CFW_PWRCTRL_DISABLE_GPU_LOW_POWER_MODE
                    );
                    OPEN_CFW_PWRCTRL_DISABLE_MODE_WRITE(
                        OPEN_CFW_PWRCTRL_DISABLE_GPU_PREVIOUS_MODE_ADDRESS,
                        OPEN_CFW_PWRCTRL_DISABLE_GPU_HIGH_PERFORMANCE_MODE
                    );
                }
                else {
                    OPEN_CFW_PWRCTRL_DISABLE_MODE_WRITE(
                        OPEN_CFW_PWRCTRL_DISABLE_GPU_PREVIOUS_MODE_ADDRESS,
                        OPEN_CFW_PWRCTRL_DISABLE_GPU_LOW_POWER_MODE
                    );
                }

                (void)OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE(
                    OPEN_CFW_PWRCTRL_DISABLE_SPOT_GPU_STATE,
                    1U,
                    &gpu_state
                );
                (void)OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ALL(
                    peripheral_id
                );
            }
            else {
                if (
                    peripheral_id
                        < OPEN_CFW_PWRCTRL_DISABLE_AUDIO_FIRST_PERIPHERAL
                    && (descriptor.peripheral_enable_mask << 2U) != 0U
                ) {
                    (void)OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE(
                        OPEN_CFW_PWRCTRL_DISABLE_SPOT_DEVICE_POWER,
                        0U,
                        &descriptor.peripheral_status_mask
                    );
                }
                if (
                    peripheral_id
                        >= OPEN_CFW_PWRCTRL_DISABLE_AUDIO_FIRST_PERIPHERAL
                    && (
                        descriptor.peripheral_enable_mask
                        & OPEN_CFW_PWRCTRL_DISABLE_AUDIO_MONITOR_MASK
                    ) != 0U
                ) {
                    (void)OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE(
                        OPEN_CFW_PWRCTRL_DISABLE_SPOT_AUDIO_POWER,
                        0U,
                        &descriptor.peripheral_status_mask
                    );
                }
            }
        }
    }

    OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_PENDING();
    return result;
}
