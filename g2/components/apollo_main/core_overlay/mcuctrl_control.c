/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 MCUCTRL control adaptation from AmbiqSuite SDK 5.1.0
 * and the reviewed G2 2.2.6.10 stock function at
 * 0x004809C4...0x00480C55.
 */

typedef __UINTPTR_TYPE__ open_cfw_mcuctrl_control_uintptr;

#define OPEN_CFW_MCUCTRL_CONTROL_SUCCESS 0U
#define OPEN_CFW_MCUCTRL_CONTROL_INVALID_ARGUMENT 6U

#define OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32K_ENABLE 0U
#define OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32K_DISABLE 1U
#define OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_KICK_START 2U
#define OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_NORMAL 3U
#define OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_DISABLE 4U
#define OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_CLKOUT_ENABLE 5U
#define OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_CLKOUT_DISABLE 6U

#define OPEN_CFW_MCUCTRL_XTALCTRL_ADDRESS 0x40020120U
#define OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS 0x40020128U
#define OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS 0x4002012CU
#define OPEN_CFW_MCUCTRL_XTALHSCAP2TRIM_ADDRESS 0x200001E0U
#define OPEN_CFW_MCUCTRL_XTALHSCAPTRIM_ADDRESS 0x200001E4U

#define OPEN_CFW_MCUCTRL_CONTROL_DELAY_US_ENTRY 0x004807A1U
#define OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST_ENTRY 0x004C44BDU
#define OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE_ENTRY 0x004C4531U

#define OPEN_CFW_MCUCTRL_CLOCK_XTAL_HS 2U
#define OPEN_CFW_MCUCTRL_CLOCKOUT_XTAL_USER 0x34U

#ifndef OPEN_CFW_MCUCTRL_CONTROL_READ32
#define OPEN_CFW_MCUCTRL_CONTROL_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_mcuctrl_control_uintptr)(address))
#endif

#ifndef OPEN_CFW_MCUCTRL_CONTROL_WRITE32
#define OPEN_CFW_MCUCTRL_CONTROL_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_mcuctrl_control_uintptr)(address) = (value))
#endif

#ifndef OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT8
#define OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT8(arguments) \
    (*(const unsigned char *)(arguments))
#endif

#ifndef OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT32
#define OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT32(arguments) \
    (*(const unsigned int *)(arguments))
#endif

#ifndef OPEN_CFW_MCUCTRL_CONTROL_DELAY_US
typedef void (*open_cfw_mcuctrl_control_delay_function)(unsigned int);
#define OPEN_CFW_MCUCTRL_CONTROL_DELAY_US(microseconds) \
    (((open_cfw_mcuctrl_control_delay_function) \
        (open_cfw_mcuctrl_control_uintptr) \
        OPEN_CFW_MCUCTRL_CONTROL_DELAY_US_ENTRY)((microseconds)))
#endif

#ifndef OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST
typedef unsigned int (*open_cfw_mcuctrl_control_clock_function)(
    unsigned int,
    unsigned int
);
#define OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST(clock, user) \
    (((open_cfw_mcuctrl_control_clock_function) \
        (open_cfw_mcuctrl_control_uintptr) \
        OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST_ENTRY)((clock), (user)))
#endif

#ifndef OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE
#define OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE(clock, user) \
    (((open_cfw_mcuctrl_control_clock_function) \
        (open_cfw_mcuctrl_control_uintptr) \
        OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE_ENTRY)((clock), (user)))
#endif

static unsigned int
open_cfw_mcuctrl_control_trim_value(unsigned int normal_value)
{
    unsigned int value;

    value =
        OPEN_CFW_MCUCTRL_CONTROL_READ32(
            OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS
        ) & 0xC0007000U;
    value |=
        OPEN_CFW_MCUCTRL_CONTROL_READ32(
            OPEN_CFW_MCUCTRL_XTALHSCAP2TRIM_ADDRESS
        ) & 0x3FU;
    value |=
        (
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCAPTRIM_ADDRESS
            ) & 0x0FU
        ) << 6U;
    value |= normal_value;
    return value;
}

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_mcuctrl_control. The low byte of control is the reviewed stock
 * dispatch input.
 */
__attribute__((used, noinline))
unsigned int open_cfw_mcuctrl_control(
    unsigned int control,
    void *arguments
)
{
    unsigned int value;
    unsigned int status;

    switch ((unsigned char)control) {
    case OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32K_ENABLE:
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALCTRL_ADDRESS
            ) & 0xFFFFFFE0U;
        if (
            arguments != (void *)0
            && OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT8(arguments) == 1U
        ) {
            value |= 0x05U;
        }
        else {
            value |= 0x19U;
        }
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALCTRL_ADDRESS,
            value
        );
        break;

    case OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32K_DISABLE:
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALCTRL_ADDRESS
            ) & 0xFFFFFFFCU;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALCTRL_ADDRESS,
            value
        );
        break;

    case OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_KICK_START:
        value = open_cfw_mcuctrl_control_trim_value(0x0FFF8C00U);
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS,
            value
        );

        value =
            (
                OPEN_CFW_MCUCTRL_CONTROL_READ32(
                    OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
                ) & 0xFFFFFFDDU
            ) | 0x02U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            ) | 0x01U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            ) | 0x10U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            ) | 0x08U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        OPEN_CFW_MCUCTRL_CONTROL_DELAY_US(5U);
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            ) & 0xFFFFFFEFU;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );

        if (
            arguments != (void *)0
            && OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT8(arguments) == 1U
        ) {
            value =
                (
                    OPEN_CFW_MCUCTRL_CONTROL_READ32(
                        OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
                    ) & 0xFFFFFEF6U
                ) | 0x100U;
            OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
                value
            );
        }
        break;

    case OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_NORMAL:
        value = open_cfw_mcuctrl_control_trim_value(0x0FFF8C00U);
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS,
            value
        );

        value =
            (
                OPEN_CFW_MCUCTRL_CONTROL_READ32(
                    OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
                ) & 0xFFFFFFDDU
            ) | 0x22U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            ) | 0x01U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            );

        if (
            arguments != (void *)0
            && OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT8(arguments) == 1U
        ) {
            value = (value & 0xFFFFFEFEU) | 0x100U;
        }
        else {
            value = (value & 0xFFFFFFD7U) | 0x08U;
        }
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        break;

    case OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_DISABLE:
        value = open_cfw_mcuctrl_control_trim_value(0x03118000U);
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS,
            value
        );
        value =
            (
                OPEN_CFW_MCUCTRL_CONTROL_READ32(
                    OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
                ) & 0xFFFFFED4U
            ) | 0x02U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        break;

    case OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_CLKOUT_ENABLE:
        status = OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST(
            OPEN_CFW_MCUCTRL_CLOCK_XTAL_HS,
            OPEN_CFW_MCUCTRL_CLOCKOUT_XTAL_USER
        );
        if (status != OPEN_CFW_MCUCTRL_CONTROL_SUCCESS) {
            return status;
        }

        if (arguments == (void *)0) {
            value = 4U;
        }
        else {
            value = OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT32(arguments);
            if (value != 0U && (value < 3U || value > 7U)) {
                return OPEN_CFW_MCUCTRL_CONTROL_INVALID_ARGUMENT;
            }
            value = OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT32(arguments);
        }

        value =
            (
                OPEN_CFW_MCUCTRL_CONTROL_READ32(
                    OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS
                ) & 0xFFFF8FFFU
            ) | ((value & 7U) << 12U);
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS,
            value
        );
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            ) | 0x80U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        break;

    case OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_CLKOUT_DISABLE:
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS
            ) | 0x7000U;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS,
            value
        );
        value =
            OPEN_CFW_MCUCTRL_CONTROL_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            ) & 0xFFFFFF7FU;
        OPEN_CFW_MCUCTRL_CONTROL_WRITE32(
            OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS,
            value
        );
        status = OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE(
            OPEN_CFW_MCUCTRL_CLOCK_XTAL_HS,
            OPEN_CFW_MCUCTRL_CLOCKOUT_XTAL_USER
        );
        if (status != OPEN_CFW_MCUCTRL_CONTROL_SUCCESS) {
            return status;
        }
        break;

    default:
        return OPEN_CFW_MCUCTRL_CONTROL_INVALID_ARGUMENT;
    }

    return OPEN_CFW_MCUCTRL_CONTROL_SUCCESS;
}

#undef OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE
#undef OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST
#undef OPEN_CFW_MCUCTRL_CONTROL_DELAY_US
#undef OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT32
#undef OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT8
#undef OPEN_CFW_MCUCTRL_CONTROL_WRITE32
#undef OPEN_CFW_MCUCTRL_CONTROL_READ32
#undef OPEN_CFW_MCUCTRL_CLOCKOUT_XTAL_USER
#undef OPEN_CFW_MCUCTRL_CLOCK_XTAL_HS
#undef OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE_ENTRY
#undef OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST_ENTRY
#undef OPEN_CFW_MCUCTRL_CONTROL_DELAY_US_ENTRY
#undef OPEN_CFW_MCUCTRL_XTALHSCAPTRIM_ADDRESS
#undef OPEN_CFW_MCUCTRL_XTALHSCAP2TRIM_ADDRESS
#undef OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
#undef OPEN_CFW_MCUCTRL_XTALHSTRIMS_ADDRESS
#undef OPEN_CFW_MCUCTRL_XTALCTRL_ADDRESS
#undef OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_CLKOUT_DISABLE
#undef OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_CLKOUT_ENABLE
#undef OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_DISABLE
#undef OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_NORMAL
#undef OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32M_KICK_START
#undef OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32K_DISABLE
#undef OPEN_CFW_MCUCTRL_CONTROL_EXTCLK32K_ENABLE
#undef OPEN_CFW_MCUCTRL_CONTROL_INVALID_ARGUMENT
#undef OPEN_CFW_MCUCTRL_CONTROL_SUCCESS
