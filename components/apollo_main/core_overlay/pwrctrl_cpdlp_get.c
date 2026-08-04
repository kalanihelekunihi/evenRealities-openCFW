/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 CPDLPSTATE getter adaptation from AmbiqSuite SDK 5.1.0.
 * Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_cpdlp_get_uintptr;

#define OPEN_CFW_PWRCTRL_CPDLP_GET_STATE_ADDRESS 0xE001E300U
#define OPEN_CFW_PWRCTRL_CPDLP_GET_FIELD_MASK 0x3U
#define OPEN_CFW_PWRCTRL_CPDLP_GET_RLP_SHIFT 8U
#define OPEN_CFW_PWRCTRL_CPDLP_GET_ELP_SHIFT 4U
#define OPEN_CFW_PWRCTRL_CPDLP_GET_CLP_SHIFT 0U

#ifndef OPEN_CFW_PWRCTRL_CPDLP_GET_READ32
#define OPEN_CFW_PWRCTRL_CPDLP_GET_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_cpdlp_get_uintptr)(address))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_pwrmodctl_cpdlp_get at
 * 0x00480008...0x00480027.
 *
 * The stock image uses short enums, so the three output fields occupy three
 * consecutive bytes.
 */
__attribute__((used, noinline))
void
open_cfw_pwrctrl_cpdlp_get(unsigned char *configuration)
{
    unsigned int state;

    state = OPEN_CFW_PWRCTRL_CPDLP_GET_READ32(
        OPEN_CFW_PWRCTRL_CPDLP_GET_STATE_ADDRESS
    );
    configuration[0] = (unsigned char)(
        (state >> OPEN_CFW_PWRCTRL_CPDLP_GET_RLP_SHIFT)
        & OPEN_CFW_PWRCTRL_CPDLP_GET_FIELD_MASK
    );
    configuration[1] = (unsigned char)(
        (state >> OPEN_CFW_PWRCTRL_CPDLP_GET_ELP_SHIFT)
        & OPEN_CFW_PWRCTRL_CPDLP_GET_FIELD_MASK
    );
    configuration[2] = (unsigned char)(
        (state >> OPEN_CFW_PWRCTRL_CPDLP_GET_CLP_SHIFT)
        & OPEN_CFW_PWRCTRL_CPDLP_GET_FIELD_MASK
    );
}
