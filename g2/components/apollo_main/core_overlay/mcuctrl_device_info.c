/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 MCUCTRL device-information adaptation from AmbiqSuite
 * SDK 5.1.0 and the reviewed G2 2.2.6.10 stock function at
 * 0x00480874...0x004809C3.
 */

typedef __UINTPTR_TYPE__ open_cfw_mcuctrl_device_info_uintptr;

typedef struct open_cfw_mcuctrl_device_info {
    unsigned int chip_part_number;
    unsigned int chip_id0;
    unsigned int chip_id1;
    unsigned int chip_revision;
    unsigned int vendor_id;
    unsigned int sku;
    unsigned int qualified;
    unsigned int flash_size;
    unsigned int itcm_size;
    unsigned int dtcm_size;
    unsigned int shared_sram_size;
    unsigned int mram_size;
    unsigned int jedec_part_number;
    unsigned int jedec_manufacturer_id;
    unsigned int jedec_chip_revision;
    unsigned int jedec_coresight_id;
} open_cfw_mcuctrl_device_info;

_Static_assert(
    sizeof(open_cfw_mcuctrl_device_info) == 64U,
    "Apollo510 MCUCTRL device-information ABI must remain 16 words"
);

#define OPEN_CFW_MCUCTRL_CHIPPN_ADDRESS 0x40020000U
#define OPEN_CFW_MCUCTRL_CHIPID0_ADDRESS 0x40020004U
#define OPEN_CFW_MCUCTRL_CHIPID1_ADDRESS 0x40020008U
#define OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS 0x4002000CU
#define OPEN_CFW_MCUCTRL_VENDORID_ADDRESS 0x40020010U
#define OPEN_CFW_MCUCTRL_SKU_ADDRESS 0x40020014U

#define OPEN_CFW_JEDEC_PID0_ADDRESS 0xE00FEFE0U
#define OPEN_CFW_JEDEC_PID1_ADDRESS 0xE00FEFE4U
#define OPEN_CFW_JEDEC_PID2_ADDRESS 0xE00FEFE8U
#define OPEN_CFW_JEDEC_PID3_ADDRESS 0xE00FEFECU
#define OPEN_CFW_JEDEC_CID0_ADDRESS 0xE00FEFF0U
#define OPEN_CFW_JEDEC_CID1_ADDRESS 0xE00FEFF4U
#define OPEN_CFW_JEDEC_CID2_ADDRESS 0xE00FEFF8U
#define OPEN_CFW_JEDEC_CID3_ADDRESS 0xE00FEFFCU

#define OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_ENTRY 0x00491103U

#ifndef OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32
#define OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_mcuctrl_device_info_uintptr)(address))
#endif

#ifndef OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US
typedef void (*open_cfw_mcuctrl_device_info_delay_function)(unsigned int);
#define OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(microseconds) \
    (((open_cfw_mcuctrl_device_info_delay_function) \
        (open_cfw_mcuctrl_device_info_uintptr) \
        OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_ENTRY)((microseconds)))
#endif

static const unsigned short open_cfw_mcuctrl_mram_size_kib[4] = {
    1024U,
    2048U,
    3072U,
    4096U,
};

static const unsigned short open_cfw_mcuctrl_ram_size_kib[4][3] = {
    {128U, 256U, 1024U},
    {128U, 256U, 2048U},
    {256U, 512U, 2048U},
    {256U, 512U, 3072U},
};

/*
 * ABI-compatible source replacement for AmbiqSuite's private
 * device_info_get. Its sole stock caller is the DEVICEID branch of
 * am_hal_mcuctrl_info_get.
 */
__attribute__((used, noinline))
void open_cfw_mcuctrl_device_info_get(
    open_cfw_mcuctrl_device_info *device
)
{
    unsigned int sku_index;

    device->chip_part_number =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_CHIPPN_ADDRESS
        );
    device->chip_id0 =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_CHIPID0_ADDRESS
        );
    device->chip_id1 =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_CHIPID1_ADDRESS
        );
    device->chip_revision =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS
        );
    device->vendor_id =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_VENDORID_ADDRESS
        );
    device->sku =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_SKU_ADDRESS
        );
    device->qualified = 1U;

    sku_index =
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_MCUCTRL_SKU_ADDRESS
            ) >> 2U
        ) & 3U;
    device->mram_size =
        (unsigned int)open_cfw_mcuctrl_mram_size_kib[sku_index] * 1024U;

    sku_index =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_SKU_ADDRESS
        ) & 3U;
    device->itcm_size =
        (unsigned int)open_cfw_mcuctrl_ram_size_kib[sku_index][0] * 1024U;

    sku_index =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_SKU_ADDRESS
        ) & 3U;
    device->dtcm_size =
        (unsigned int)open_cfw_mcuctrl_ram_size_kib[sku_index][1] * 1024U;

    sku_index =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_MCUCTRL_SKU_ADDRESS
        ) & 3U;
    device->shared_sram_size =
        (unsigned int)open_cfw_mcuctrl_ram_size_kib[sku_index][2] * 1024U;

    device->jedec_part_number =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_JEDEC_PID0_ADDRESS
        ) & 0xFFU;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);
    device->jedec_part_number |=
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_JEDEC_PID1_ADDRESS
            ) & 0x0FU
        ) << 8U;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);

    device->jedec_manufacturer_id =
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_JEDEC_PID1_ADDRESS
            ) >> 4U
        ) & 0x0FU;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);
    device->jedec_manufacturer_id |=
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_JEDEC_PID2_ADDRESS
            ) & 0x0FU
        ) << 4U;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);

    device->jedec_chip_revision =
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_JEDEC_PID2_ADDRESS
        ) & 0xF0U;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);
    device->jedec_chip_revision |=
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_JEDEC_PID3_ADDRESS
            ) >> 4U
        ) & 0x0FU;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);

    device->jedec_coresight_id =
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_JEDEC_CID3_ADDRESS
            ) & 0xFFU
        ) << 24U;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);
    device->jedec_coresight_id |=
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_JEDEC_CID2_ADDRESS
            ) & 0xFFU
        ) << 16U;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);
    device->jedec_coresight_id |=
        (
            OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
                OPEN_CFW_JEDEC_CID1_ADDRESS
            ) & 0xFFU
        ) << 8U;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);
    device->jedec_coresight_id |=
        OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32(
            OPEN_CFW_JEDEC_CID0_ADDRESS
        ) & 0xFFU;
    OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US(10U);
}

#undef OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_US
#undef OPEN_CFW_MCUCTRL_DEVICE_INFO_READ32
#undef OPEN_CFW_MCUCTRL_DEVICE_INFO_DELAY_ENTRY
#undef OPEN_CFW_JEDEC_CID3_ADDRESS
#undef OPEN_CFW_JEDEC_CID2_ADDRESS
#undef OPEN_CFW_JEDEC_CID1_ADDRESS
#undef OPEN_CFW_JEDEC_CID0_ADDRESS
#undef OPEN_CFW_JEDEC_PID3_ADDRESS
#undef OPEN_CFW_JEDEC_PID2_ADDRESS
#undef OPEN_CFW_JEDEC_PID1_ADDRESS
#undef OPEN_CFW_JEDEC_PID0_ADDRESS
#undef OPEN_CFW_MCUCTRL_SKU_ADDRESS
#undef OPEN_CFW_MCUCTRL_VENDORID_ADDRESS
#undef OPEN_CFW_MCUCTRL_CHIPREV_ADDRESS
#undef OPEN_CFW_MCUCTRL_CHIPID1_ADDRESS
#undef OPEN_CFW_MCUCTRL_CHIPID0_ADDRESS
#undef OPEN_CFW_MCUCTRL_CHIPPN_ADDRESS
