/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 external-32-MHz-clock status adaptation from
 * AmbiqSuite SDK 5.1.0 and the reviewed G2 2.2.6.10 stock function at
 * 0x00480C56...0x00480C7B.
 */

typedef __UINTPTR_TYPE__ open_cfw_mcuctrl_extclk32m_status_uintptr;

#define OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_SUCCESS 0U
#define OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_OFF 0U
#define OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_XTAL 1U
#define OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_EXT_CLK 2U

#define OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS 0x4002012CU
#define OPEN_CFW_MCUCTRL_XTALHSCTRL_POWERED_MASK 0x00000001U
#define OPEN_CFW_MCUCTRL_XTALHSCTRL_EXTERNAL_MASK 0x00000100U

#ifndef OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_READ32
#define OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_mcuctrl_extclk32m_status_uintptr)(address))
#endif

/*
 * ABI-compatible source replacement for
 * am_hal_mcuctrl_extclk32m_status_get. The reviewed stock ABI stores the
 * short enum through one byte and performs a fresh register read before
 * testing the powered state.
 */
__attribute__((used, noinline))
unsigned int open_cfw_mcuctrl_extclk32m_status_get(
    unsigned char *status
)
{
    if (
        (
            OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            )
            & OPEN_CFW_MCUCTRL_XTALHSCTRL_EXTERNAL_MASK
        ) != 0U
    ) {
        *status = OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_EXT_CLK;
    }
    else if (
        (
            OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_READ32(
                OPEN_CFW_MCUCTRL_XTALHSCTRL_ADDRESS
            )
            & OPEN_CFW_MCUCTRL_XTALHSCTRL_POWERED_MASK
        ) != 0U
    ) {
        *status = OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_XTAL;
    }
    else {
        *status = OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_OFF;
    }

    return OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_SUCCESS;
}
