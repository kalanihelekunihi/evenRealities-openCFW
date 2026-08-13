/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 CPDLPSTATE configuration adaptation from AmbiqSuite SDK
 * 5.1.0. Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_cpdlp_uintptr;

#define OPEN_CFW_PWRCTRL_CPDLP_CACHE_CONTROL_ADDRESS 0xE000ED14U
#define OPEN_CFW_PWRCTRL_CPDLP_STATE_ADDRESS 0xE001E300U
#define OPEN_CFW_PWRCTRL_CPDLP_CACHE_ENABLE_MASK 0x00030000U
#define OPEN_CFW_PWRCTRL_CPDLP_RLP_OFF 3U
#define OPEN_CFW_PWRCTRL_CPDLP_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_CPDLP_STATUS_FAIL 1U

#ifndef OPEN_CFW_PWRCTRL_CPDLP_READ32
#define OPEN_CFW_PWRCTRL_CPDLP_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_cpdlp_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_CPDLP_WRITE32
#define OPEN_CFW_PWRCTRL_CPDLP_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_pwrctrl_cpdlp_uintptr)(address) = (value))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_pwrmodctl_cpdlp_config at
 * 0x0047FFC4...0x00480001.
 *
 * The stock image uses short enums, so the by-value three-enum structure
 * arrives packed into the low three bytes of r0.
 */
__attribute__((used, noinline))
unsigned int
open_cfw_pwrctrl_cpdlp_config(unsigned int configuration)
{
    unsigned int cache_control;
    unsigned int rlp;
    unsigned int elp;
    unsigned int clp;
    unsigned int packed;

    cache_control = OPEN_CFW_PWRCTRL_CPDLP_READ32(
        OPEN_CFW_PWRCTRL_CPDLP_CACHE_CONTROL_ADDRESS
    );
    rlp = configuration & 0xFFU;
    if (
        (cache_control & OPEN_CFW_PWRCTRL_CPDLP_CACHE_ENABLE_MASK) != 0U
        && rlp == OPEN_CFW_PWRCTRL_CPDLP_RLP_OFF
    ) {
        return OPEN_CFW_PWRCTRL_CPDLP_STATUS_FAIL;
    }

    elp = (configuration >> 8) & 0xFFU;
    clp = (configuration >> 16) & 0xFFU;
    packed = (rlp << 8) | (elp << 4) | clp;
    OPEN_CFW_PWRCTRL_CPDLP_WRITE32(
        OPEN_CFW_PWRCTRL_CPDLP_STATE_ADDRESS,
        packed
    );

    return OPEN_CFW_PWRCTRL_CPDLP_STATUS_SUCCESS;
}
