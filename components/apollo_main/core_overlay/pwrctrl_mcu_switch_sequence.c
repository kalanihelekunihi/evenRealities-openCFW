/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 MCU HP/LP switching-sequence adaptation from AmbiqSuite
 * SDK 5.1.0. The reviewed stock helper, sole caller, fixed dependencies,
 * registers, and host behavioral evidence are recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_mcu_switch_uintptr;

#define OPEN_CFW_PWRCTRL_MCU_SWITCH_CLKGEN_MISC_ADDRESS 0x40004044U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_CLOCK_STATUS_ADDRESS 0x40004030U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_PERFORMANCE_ADDRESS 0x40021000U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_ADDRESS 0x20004538U

#define OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_FORCE_MASK 0x00000020U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_READY_MASK 0x01000000U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_REQUEST_MASK 0x00000003U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_ACK_MASK 0x00000004U

#define OPEN_CFW_PWRCTRL_MCU_SWITCH_MODE_HIGH_PERFORMANCE 2U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_CPU_STATE_LOW_POWER 0U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_CPU_STATE_HIGH_PERFORMANCE 1U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_STIMULUS_CPU_STATE 0U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_FAILURE 1U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_TIMEOUT 4U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_ACK_POLLS 20U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_READY_WAIT_US 15U

#define OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE_ENTRY 0x00480313U
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST_ENTRY 0x004803DDU
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS_ENTRY 0x004807FDU

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_READ
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_WRITE
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_WRITE
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_WRITE(value) \
    (*(volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_ADDRESS = \
            (unsigned char)(value))
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_DISABLE
unsigned int open_cfw_lv_irq_disable(void);
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_DISABLE() \
    open_cfw_lv_irq_disable()
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_pwrctrl_mcu_switch_irq_restore_target(unsigned int primask)
{
    __asm__ volatile (
        "msr primask, %0"
        :
        : "r"(primask)
        : "memory"
    );
}
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_RESTORE(primask) \
    open_cfw_pwrctrl_mcu_switch_irq_restore_target(primask)
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_US
void open_cfw_delay_us(unsigned int microseconds);
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_US(microseconds) \
    open_cfw_delay_us(microseconds)
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE
typedef unsigned int (*open_cfw_pwrctrl_mcu_switch_spot_update_function)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE( \
    stimulus, enabled, state \
) \
    (((open_cfw_pwrctrl_mcu_switch_spot_update_function) \
        OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE_ENTRY)( \
            (stimulus), \
            (enabled), \
            (state) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST
typedef void (*open_cfw_pwrctrl_mcu_switch_spot_post_function)(void);
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST() \
    (((open_cfw_pwrctrl_mcu_switch_spot_post_function) \
        OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS
typedef unsigned int (
    *open_cfw_pwrctrl_mcu_switch_delay_status_function
)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS( \
    maximum_delay, address, mask, expected \
) \
    (((open_cfw_pwrctrl_mcu_switch_delay_status_function) \
        OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS_ENTRY)( \
            (maximum_delay), \
            (address), \
            (mask), \
            (expected) \
        ))
#endif

static __attribute__((always_inline)) inline unsigned int
open_cfw_pwrctrl_mcu_switch_request_and_wait(
    unsigned int power_mode
)
{
    unsigned int performance;
    unsigned int poll;

    performance = OPEN_CFW_PWRCTRL_MCU_SWITCH_READ(
        OPEN_CFW_PWRCTRL_MCU_SWITCH_PERFORMANCE_ADDRESS
    );
    performance =
        (performance & ~OPEN_CFW_PWRCTRL_MCU_SWITCH_REQUEST_MASK)
        | (power_mode & OPEN_CFW_PWRCTRL_MCU_SWITCH_REQUEST_MASK);
    OPEN_CFW_PWRCTRL_MCU_SWITCH_WRITE(
        OPEN_CFW_PWRCTRL_MCU_SWITCH_PERFORMANCE_ADDRESS,
        performance
    );

#pragma clang loop unroll(disable)
    for (poll = 0U; poll < OPEN_CFW_PWRCTRL_MCU_SWITCH_ACK_POLLS; ++poll) {
        performance = OPEN_CFW_PWRCTRL_MCU_SWITCH_READ(
            OPEN_CFW_PWRCTRL_MCU_SWITCH_PERFORMANCE_ADDRESS
        );
        if (
            (performance & OPEN_CFW_PWRCTRL_MCU_SWITCH_ACK_MASK)
            != 0U
        ) {
            return OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_SUCCESS;
        }
        OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_US(1U);
    }

    return OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_TIMEOUT;
}

/*
 * ABI-compatible source replacement for AmbiqSuite's private
 * mcu_hp_lp_switch_sequence helper at 0x0047EF74...0x0047F09F.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_mcu_switch_sequence(
    unsigned int requested_mode
)
{
    unsigned int power_mode = requested_mode & 0xFFU;
    unsigned int primask;
    unsigned int status;
    unsigned int misc;
    unsigned int forced_hfrc2;
    unsigned char cpu_state;

    primask = OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_DISABLE();

    if (
        power_mode
        == OPEN_CFW_PWRCTRL_MCU_SWITCH_MODE_HIGH_PERFORMANCE
    ) {
        cpu_state =
            OPEN_CFW_PWRCTRL_MCU_SWITCH_CPU_STATE_HIGH_PERFORMANCE;
        status = OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE(
            OPEN_CFW_PWRCTRL_MCU_SWITCH_STIMULUS_CPU_STATE,
            0U,
            &cpu_state
        );

        if (status == OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_SUCCESS) {
            forced_hfrc2 = 0U;
            misc = OPEN_CFW_PWRCTRL_MCU_SWITCH_READ(
                OPEN_CFW_PWRCTRL_MCU_SWITCH_CLKGEN_MISC_ADDRESS
            );
            if (
                (misc & OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_FORCE_MASK)
                == 0U
            ) {
                OPEN_CFW_PWRCTRL_MCU_SWITCH_WRITE(
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_CLKGEN_MISC_ADDRESS,
                    misc
                        | OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_FORCE_MASK
                );
                OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_US(1U);
                (void)OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS(
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_READY_WAIT_US,
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_CLOCK_STATUS_ADDRESS,
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_READY_MASK,
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_READY_MASK
                );
                forced_hfrc2 = 1U;
            }

            if (
                (OPEN_CFW_PWRCTRL_MCU_SWITCH_READ(
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_CLOCK_STATUS_ADDRESS
                ) & OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_READY_MASK)
                != 0U
            ) {
                status = open_cfw_pwrctrl_mcu_switch_request_and_wait(
                    power_mode
                );
            }
            else {
                status = OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_FAILURE;
            }

            if (forced_hfrc2 != 0U) {
                misc = OPEN_CFW_PWRCTRL_MCU_SWITCH_READ(
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_CLKGEN_MISC_ADDRESS
                );
                OPEN_CFW_PWRCTRL_MCU_SWITCH_WRITE(
                    OPEN_CFW_PWRCTRL_MCU_SWITCH_CLKGEN_MISC_ADDRESS,
                    misc
                        & ~OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_FORCE_MASK
                );
            }
            OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST();
        }
    }
    else {
        status = open_cfw_pwrctrl_mcu_switch_request_and_wait(power_mode);
    }

    if (status == OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_SUCCESS) {
        OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_WRITE(power_mode);
        if (
            power_mode
            != OPEN_CFW_PWRCTRL_MCU_SWITCH_MODE_HIGH_PERFORMANCE
        ) {
            cpu_state = OPEN_CFW_PWRCTRL_MCU_SWITCH_CPU_STATE_LOW_POWER;
            status = OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE(
                OPEN_CFW_PWRCTRL_MCU_SWITCH_STIMULUS_CPU_STATE,
                0U,
                &cpu_state
            );
        }
    }
    else if (
        power_mode
        == OPEN_CFW_PWRCTRL_MCU_SWITCH_MODE_HIGH_PERFORMANCE
    ) {
        cpu_state = OPEN_CFW_PWRCTRL_MCU_SWITCH_CPU_STATE_LOW_POWER;
        (void)OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE(
            OPEN_CFW_PWRCTRL_MCU_SWITCH_STIMULUS_CPU_STATE,
            0U,
            &cpu_state
        );
    }

    OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_RESTORE(primask);
    return status;
}

#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_US
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_RESTORE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_DISABLE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_WRITE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_WRITE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_READ
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS_ENTRY
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST_ENTRY
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE_ENTRY
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_READY_WAIT_US
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_ACK_POLLS
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_TIMEOUT
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_FAILURE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_STATUS_SUCCESS
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_STIMULUS_CPU_STATE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_CPU_STATE_HIGH_PERFORMANCE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_CPU_STATE_LOW_POWER
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_MODE_HIGH_PERFORMANCE
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_ACK_MASK
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_REQUEST_MASK
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_READY_MASK
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_HFRC2_FORCE_MASK
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_ADDRESS
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_PERFORMANCE_ADDRESS
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_CLOCK_STATUS_ADDRESS
#undef OPEN_CFW_PWRCTRL_MCU_SWITCH_CLKGEN_MISC_ADDRESS
