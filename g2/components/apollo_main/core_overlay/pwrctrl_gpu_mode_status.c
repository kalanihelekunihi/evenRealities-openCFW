/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 GPU power-mode status adaptation from AmbiqSuite
 * SDK 5.1.0. The reviewed stock function, sole caller, fixed cache,
 * and host behavioral evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_PWRCTRL_GPU_STATUS_CURRENT_MODE_ADDRESS 0x20074F60U
#define OPEN_CFW_PWRCTRL_GPU_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_GPU_STATUS_INVALID_ARGUMENT 6U

#ifndef OPEN_CFW_PWRCTRL_GPU_STATUS_CURRENT_MODE_READ
#define OPEN_CFW_PWRCTRL_GPU_STATUS_CURRENT_MODE_READ() \
    (*(const volatile unsigned char *) \
        OPEN_CFW_PWRCTRL_GPU_STATUS_CURRENT_MODE_ADDRESS)
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_gpu_mode_status function at 0x0047F108...0x0047F11B.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_gpu_mode_status(
    unsigned char *current_power_mode
)
{
    if (current_power_mode == (void *)0) {
        return OPEN_CFW_PWRCTRL_GPU_STATUS_INVALID_ARGUMENT;
    }

    *current_power_mode =
        OPEN_CFW_PWRCTRL_GPU_STATUS_CURRENT_MODE_READ();
    return OPEN_CFW_PWRCTRL_GPU_STATUS_SUCCESS;
}
