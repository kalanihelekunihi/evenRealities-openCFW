/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 temperature-update adaptation from AmbiqSuite SDK 5.1.0.
 * Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_PWRCTRL_TEMP_VFP_ABI \
    __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_PWRCTRL_TEMP_VFP_ABI
#endif

#define OPEN_CFW_PWRCTRL_TEMP_SPOT_STIMULUS 2U
#define OPEN_CFW_PWRCTRL_TEMP_SPOT_DISABLED 0U
#define OPEN_CFW_PWRCTRL_TEMP_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_TEMP_STATUS_FAIL 1U

struct open_cfw_pwrctrl_tempco {
    float temperature;
    float range_lower;
    float range_higher;
};

struct open_cfw_pwrctrl_temp_thresholds {
    float low;
    float high;
};

typedef unsigned int (*open_cfw_pwrctrl_temp_spot_update_fn)(
    unsigned int stimulus,
    unsigned int enabled,
    void *arguments
);

#ifndef OPEN_CFW_PWRCTRL_TEMP_SPOT_UPDATE
#define OPEN_CFW_PWRCTRL_TEMP_SPOT_UPDATE(stimulus, enabled, arguments) \
    (((open_cfw_pwrctrl_temp_spot_update_fn)0x00480313U)( \
        (stimulus), \
        (enabled), \
        (arguments) \
    ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_temp_update at 0x00480028...0x00480057.
 */
__attribute__((used, noinline))
OPEN_CFW_PWRCTRL_TEMP_VFP_ABI
unsigned int
open_cfw_pwrctrl_temp_update(
    float current_temperature,
    struct open_cfw_pwrctrl_temp_thresholds *thresholds
)
{
    struct open_cfw_pwrctrl_tempco parameters;
    unsigned int status;

    parameters.temperature = current_temperature;
    status = OPEN_CFW_PWRCTRL_TEMP_SPOT_UPDATE(
        OPEN_CFW_PWRCTRL_TEMP_SPOT_STIMULUS,
        OPEN_CFW_PWRCTRL_TEMP_SPOT_DISABLED,
        &parameters
    );
    if (status != OPEN_CFW_PWRCTRL_TEMP_STATUS_SUCCESS) {
        thresholds->low = 0.0F;
        thresholds->high = 0.0F;
        return OPEN_CFW_PWRCTRL_TEMP_STATUS_FAIL;
    }

    thresholds->low = parameters.range_lower;
    thresholds->high = parameters.range_higher;
    return OPEN_CFW_PWRCTRL_TEMP_STATUS_SUCCESS;
}
