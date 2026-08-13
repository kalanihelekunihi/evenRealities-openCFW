/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 MCUCTRL trim-version adaptation from AmbiqSuite SDK
 * 5.1.0 and the reviewed G2 2.2.6.10 stock function at
 * 0x00480C7C...0x00480D71.
 */

typedef __UINTPTR_TYPE__ open_cfw_mcuctrl_trim_version_uintptr;

#define OPEN_CFW_MCUCTRL_TRIM_INFO1_READ_ENTRY 0x004D3F3DU
#define OPEN_CFW_MCUCTRL_TRIM_INFO_SPACE_CURRENT 1U
#define OPEN_CFW_MCUCTRL_TRIM_REVISION_WORD_OFFSET 0x244U
#define OPEN_CFW_MCUCTRL_TRIM_STATUS_SUCCESS 0U

#define OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS 0x4002000CU
#define OPEN_CFW_MCUCTRL_CHIPREV_MINOR_MASK 0x0000000FU
#define OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_MASK 0x000000F0U
#define OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_SHIFT 4U
#define OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_B 2U
#define OPEN_CFW_MCUCTRL_CHIPREV_MINOR_B1 2U
#define OPEN_CFW_MCUCTRL_CHIPREV_MINOR_B2 3U

#define OPEN_CFW_MCUCTRL_TRIM_MINOR_MASK 0x000000FFU
#define OPEN_CFW_MCUCTRL_TRIM_MAJOR_PCM2 2U
#define OPEN_CFW_MCUCTRL_TRIM_MAJOR_SHIFT 8U
#define OPEN_CFW_MCUCTRL_TRIM_VALID_MASK 0x00010000U
#define OPEN_CFW_MCUCTRL_TRIM_PCM_MASK 0x00020000U

#ifndef OPEN_CFW_MCUCTRL_TRIM_READ32
#define OPEN_CFW_MCUCTRL_TRIM_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_mcuctrl_trim_version_uintptr)(address))
#endif

#ifndef OPEN_CFW_MCUCTRL_TRIM_INFO1_READ
typedef unsigned int (*open_cfw_mcuctrl_trim_info1_read_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int *
);
#define OPEN_CFW_MCUCTRL_TRIM_INFO1_READ( \
    info_space, word_offset, word_count, destination \
) \
    (((open_cfw_mcuctrl_trim_info1_read_function) \
        (open_cfw_mcuctrl_trim_version_uintptr) \
        OPEN_CFW_MCUCTRL_TRIM_INFO1_READ_ENTRY)( \
            (info_space), \
            (word_offset), \
            (word_count), \
            (destination) \
        ))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's private
 * trim_version_get. The feature structure's packed trim word is its fourth
 * 32-bit member. Each CHIPREV expression remains a fresh volatile read,
 * matching the reviewed stock instruction stream.
 */
__attribute__((used, noinline))
unsigned int open_cfw_mcuctrl_trim_version_get(
    unsigned int *feature_words
)
{
    unsigned int status;
    unsigned int trim_version;
    unsigned int packed_trim;

    status = OPEN_CFW_MCUCTRL_TRIM_INFO1_READ(
        OPEN_CFW_MCUCTRL_TRIM_INFO_SPACE_CURRENT,
        OPEN_CFW_MCUCTRL_TRIM_REVISION_WORD_OFFSET,
        1U,
        &trim_version
    );

    packed_trim = 0U;
    if (status == OPEN_CFW_MCUCTRL_TRIM_STATUS_SUCCESS) {
        if (
            (
                (
                    OPEN_CFW_MCUCTRL_TRIM_READ32(
                        OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS
                    ) & OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_MASK
                ) >> OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_SHIFT
            ) == OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_B
            && (
                OPEN_CFW_MCUCTRL_TRIM_READ32(
                    OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS
                ) & OPEN_CFW_MCUCTRL_CHIPREV_MINOR_MASK
            ) >= OPEN_CFW_MCUCTRL_CHIPREV_MINOR_B1
            && trim_version < OPEN_CFW_MCUCTRL_TRIM_MINOR_MASK
        ) {
            if (
                (
                    OPEN_CFW_MCUCTRL_TRIM_READ32(
                        OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS
                    ) & OPEN_CFW_MCUCTRL_CHIPREV_MINOR_MASK
                ) != OPEN_CFW_MCUCTRL_CHIPREV_MINOR_B2
            ) {
                --trim_version;
            }
            packed_trim =
                (
                    OPEN_CFW_MCUCTRL_TRIM_MAJOR_PCM2
                    << OPEN_CFW_MCUCTRL_TRIM_MAJOR_SHIFT
                )
                | (trim_version & OPEN_CFW_MCUCTRL_TRIM_MINOR_MASK)
                | OPEN_CFW_MCUCTRL_TRIM_PCM_MASK
                | OPEN_CFW_MCUCTRL_TRIM_VALID_MASK;
        }
        else {
            packed_trim =
                (trim_version & OPEN_CFW_MCUCTRL_TRIM_MINOR_MASK)
                | OPEN_CFW_MCUCTRL_TRIM_VALID_MASK;
        }
    }
    else {
        packed_trim = trim_version & OPEN_CFW_MCUCTRL_TRIM_MINOR_MASK;
    }

    feature_words[3] = packed_trim;
    return status;
}

#undef OPEN_CFW_MCUCTRL_TRIM_INFO1_READ
#undef OPEN_CFW_MCUCTRL_TRIM_READ32
#undef OPEN_CFW_MCUCTRL_TRIM_PCM_MASK
#undef OPEN_CFW_MCUCTRL_TRIM_VALID_MASK
#undef OPEN_CFW_MCUCTRL_TRIM_MAJOR_SHIFT
#undef OPEN_CFW_MCUCTRL_TRIM_MAJOR_PCM2
#undef OPEN_CFW_MCUCTRL_TRIM_MINOR_MASK
#undef OPEN_CFW_MCUCTRL_CHIPREV_MINOR_B2
#undef OPEN_CFW_MCUCTRL_CHIPREV_MINOR_B1
#undef OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_B
#undef OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_SHIFT
#undef OPEN_CFW_MCUCTRL_CHIPREV_MAJOR_MASK
#undef OPEN_CFW_MCUCTRL_CHIPREV_MINOR_MASK
#undef OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS
#undef OPEN_CFW_MCUCTRL_TRIM_STATUS_SUCCESS
#undef OPEN_CFW_MCUCTRL_TRIM_REVISION_WORD_OFFSET
#undef OPEN_CFW_MCUCTRL_TRIM_INFO_SPACE_CURRENT
#undef OPEN_CFW_MCUCTRL_TRIM_INFO1_READ_ENTRY
