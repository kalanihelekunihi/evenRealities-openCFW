/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 trim-version helper adaptation from AmbiqSuite SDK
 * 5.1.0. The reviewed stock helper, caller, INFO1 dependency, cache, and host
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_trim_uintptr;

#define OPEN_CFW_PWRCTRL_TRIM_CACHE_DEFAULT_ADDRESS 0x200001E8U
#define OPEN_CFW_PWRCTRL_TRIM_INFO1_READ_ENTRY 0x004D3F3DU
#define OPEN_CFW_PWRCTRL_TRIM_INFO_SPACE_CURRENT 1U
#define OPEN_CFW_PWRCTRL_TRIM_REVISION_WORD_OFFSET 0x244U
#define OPEN_CFW_PWRCTRL_TRIM_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_TRIM_STATUS_INVALID_ARGUMENT 6U
#define OPEN_CFW_PWRCTRL_TRIM_UNINITIALIZED 0xFFFFFFFFU

#ifndef OPEN_CFW_PWRCTRL_TRIM_CACHE_ADDRESS
#define OPEN_CFW_PWRCTRL_TRIM_CACHE_ADDRESS \
    OPEN_CFW_PWRCTRL_TRIM_CACHE_DEFAULT_ADDRESS
#endif

#ifndef OPEN_CFW_PWRCTRL_TRIM_INFO1_READ
typedef unsigned int (*open_cfw_pwrctrl_trim_info1_read_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int *
);
#define OPEN_CFW_PWRCTRL_TRIM_INFO1_READ( \
    info_space, word_offset, word_count, destination \
) \
    (((open_cfw_pwrctrl_trim_info1_read_function) \
        OPEN_CFW_PWRCTRL_TRIM_INFO1_READ_ENTRY)( \
            (info_space), \
            (word_offset), \
            (word_count), \
            (destination) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's private TrimVersionGet
 * helper at 0x0047EF38...0x0047EF73.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_trim_version_get(
    unsigned int *trim_version
)
{
    volatile unsigned int *cached_trim =
        (volatile unsigned int *)(open_cfw_pwrctrl_trim_uintptr)
            OPEN_CFW_PWRCTRL_TRIM_CACHE_ADDRESS;
    unsigned int status;

    if (*cached_trim == OPEN_CFW_PWRCTRL_TRIM_UNINITIALIZED) {
        status = OPEN_CFW_PWRCTRL_TRIM_INFO1_READ(
            OPEN_CFW_PWRCTRL_TRIM_INFO_SPACE_CURRENT,
            OPEN_CFW_PWRCTRL_TRIM_REVISION_WORD_OFFSET,
            1U,
            (unsigned int *)(open_cfw_pwrctrl_trim_uintptr)cached_trim
        );
        if (
            *cached_trim == 0U
            || status != OPEN_CFW_PWRCTRL_TRIM_STATUS_SUCCESS
        ) {
            *cached_trim = 0U;
        }
    }

    if (trim_version == (unsigned int *)0) {
        return OPEN_CFW_PWRCTRL_TRIM_STATUS_INVALID_ARGUMENT;
    }

    *trim_version = *cached_trim;
    return OPEN_CFW_PWRCTRL_TRIM_STATUS_SUCCESS;
}

#undef OPEN_CFW_PWRCTRL_TRIM_INFO1_READ
#undef OPEN_CFW_PWRCTRL_TRIM_CACHE_ADDRESS
#undef OPEN_CFW_PWRCTRL_TRIM_UNINITIALIZED
#undef OPEN_CFW_PWRCTRL_TRIM_STATUS_INVALID_ARGUMENT
#undef OPEN_CFW_PWRCTRL_TRIM_STATUS_SUCCESS
#undef OPEN_CFW_PWRCTRL_TRIM_REVISION_WORD_OFFSET
#undef OPEN_CFW_PWRCTRL_TRIM_INFO_SPACE_CURRENT
#undef OPEN_CFW_PWRCTRL_TRIM_INFO1_READ_ENTRY
#undef OPEN_CFW_PWRCTRL_TRIM_CACHE_DEFAULT_ADDRESS
