/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 public MCUCTRL information-getter adaptation from
 * AmbiqSuite SDK 5.1.0 and the reviewed G2 2.2.6.10 stock function at
 * 0x00480D72...0x00480E6B.
 */

typedef __UINTPTR_TYPE__ open_cfw_mcuctrl_info_uintptr;

#define OPEN_CFW_MCUCTRL_INFO_STATUS_SUCCESS 0U
#define OPEN_CFW_MCUCTRL_INFO_STATUS_INVALID_ARGUMENT 6U
#define OPEN_CFW_MCUCTRL_INFO_FEATURES_AVAILABLE 0U
#define OPEN_CFW_MCUCTRL_INFO_DEVICE_ID 1U

#define OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS 0x40020014U

#ifndef OPEN_CFW_MCUCTRL_INFO_READ32
#define OPEN_CFW_MCUCTRL_INFO_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_mcuctrl_info_uintptr)(address))
#endif

#ifndef OPEN_CFW_MCUCTRL_INFO_TRIM_VERSION_GET
unsigned int open_cfw_mcuctrl_trim_version_get(unsigned int *);
#define OPEN_CFW_MCUCTRL_INFO_TRIM_VERSION_GET(feature) \
    open_cfw_mcuctrl_trim_version_get((unsigned int *)(feature))
#endif

#ifndef OPEN_CFW_MCUCTRL_INFO_DEVICE_INFO_GET
#define OPEN_CFW_MCUCTRL_INFO_DEVICE_INFO_GET(device) \
    open_cfw_mcuctrl_device_info_get( \
        (open_cfw_mcuctrl_device_info *)(device))
#endif

/*
 * ABI-compatible source replacement for am_hal_mcuctrl_info_get. The stock
 * short-enum ABI dispatches on the selector's low byte and lays the feature
 * structure out as eleven byte-sized fields followed by one padding byte and
 * the aligned packed trim word.
 */
__attribute__((used, noinline))
unsigned int open_cfw_mcuctrl_info_get(
    unsigned int info_get,
    void *information
)
{
    unsigned char *feature = (unsigned char *)information;
    unsigned int ram_size;

    if (information == (void *)0) {
        return OPEN_CFW_MCUCTRL_INFO_STATUS_INVALID_ARGUMENT;
    }

    switch ((unsigned char)info_get) {
    case OPEN_CFW_MCUCTRL_INFO_FEATURES_AVAILABLE:
        ram_size =
            OPEN_CFW_MCUCTRL_INFO_READ32(
                OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
            ) & 3U;
        switch (ram_size) {
        case 0U:
            feature[1] = 0U;
            feature[0] = 0U;
            feature[2] = 0U;
            break;
        case 1U:
            feature[1] = 0U;
            feature[0] = 0U;
            feature[2] = 1U;
            break;
        case 2U:
            feature[1] = 1U;
            feature[0] = 1U;
            feature[2] = 1U;
            break;
        default:
            feature[1] = 1U;
            feature[0] = 1U;
            feature[2] = 2U;
            break;
        }

        feature[3] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 2U
            ) & 3U
        );
        feature[4] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 6U
            ) & 1U
        );
        feature[5] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 7U
            ) & 1U
        );
        feature[6] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 8U
            ) & 1U
        );
        feature[7] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 9U
            ) & 1U
        );
        feature[8] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 10U
            ) & 1U
        );
        feature[9] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 19U
            ) & 1U
        );
        feature[10] = (unsigned char)(
            (
                OPEN_CFW_MCUCTRL_INFO_READ32(
                    OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
                ) >> 20U
            ) & 3U
        );
        (void)OPEN_CFW_MCUCTRL_INFO_TRIM_VERSION_GET(information);
        return OPEN_CFW_MCUCTRL_INFO_STATUS_SUCCESS;

    case OPEN_CFW_MCUCTRL_INFO_DEVICE_ID:
        OPEN_CFW_MCUCTRL_INFO_DEVICE_INFO_GET(information);
        return OPEN_CFW_MCUCTRL_INFO_STATUS_SUCCESS;

    default:
        return OPEN_CFW_MCUCTRL_INFO_STATUS_INVALID_ARGUMENT;
    }
}

#undef OPEN_CFW_MCUCTRL_INFO_DEVICE_INFO_GET
#undef OPEN_CFW_MCUCTRL_INFO_TRIM_VERSION_GET
#undef OPEN_CFW_MCUCTRL_INFO_READ32
#undef OPEN_CFW_MCUCTRL_INFO_SKU_ADDRESS
#undef OPEN_CFW_MCUCTRL_INFO_DEVICE_ID
#undef OPEN_CFW_MCUCTRL_INFO_FEATURES_AVAILABLE
#undef OPEN_CFW_MCUCTRL_INFO_STATUS_INVALID_ARGUMENT
#undef OPEN_CFW_MCUCTRL_INFO_STATUS_SUCCESS
