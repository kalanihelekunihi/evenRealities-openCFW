/* SPDX-License-Identifier: MIT
 * Recovered 16-word mode1 record; SDK am_hal_mcuctrl_device_t corroborates
 * field identities. Sizes are bytes: locked halfword KiB values shift by10.
 * Stock does not write flash_size_bytes (word7); preserve its incoming value.
 */
#ifndef OPENCFW_BOOT_DEVICE_INFO_LAYOUT_H
#define OPENCFW_BOOT_DEVICE_INFO_LAYOUT_H
#include <stddef.h>
#include <stdint.h>
struct opencfw_boot_device_info_record {
    uint32_t chip_part_number;
    uint32_t chip_id0;
    uint32_t chip_id1;
    uint32_t chip_revision;
    uint32_t vendor_id;
    uint32_t sku;
    uint32_t qualified;
    uint32_t flash_size_bytes; /* untouched by recovered mode1 helper */
    uint32_t itcm_size_bytes;
    uint32_t dtcm_size_bytes;
    uint32_t shared_sram_size_bytes;
    uint32_t mram_size_bytes;
    uint32_t jedec_part_number;
    uint32_t jedec_jepid;
    uint32_t jedec_chip_revision;
    uint32_t jedec_cid;
};
_Static_assert(sizeof(struct opencfw_boot_device_info_record)==64,
               "recovered device-info record size");
_Static_assert(offsetof(struct opencfw_boot_device_info_record,itcm_size_bytes)==32,
               "recovered memory-size fields");
_Static_assert(offsetof(struct opencfw_boot_device_info_record,mram_size_bytes)==44,
               "storage range cache consumes word11");
/* Selector0's feature record uses one-byte enum representations in the
 * locked image. Do not substitute compiler-default enum fields here. */
struct opencfw_boot_device_feature_record {
    uint8_t dtcm_kind;
    uint8_t itcm_kind;
    uint8_t shared_sram_kind;
    uint8_t mram_kind;
    uint8_t supports_hp_mode;
    uint8_t supports_mipi_dsi;
    uint8_t supports_gpu;
    uint8_t supports_usb;
    uint8_t supports_secure_boot;
    uint8_t supports_fpu;
    uint8_t mve_configuration;
    uint8_t untouched_padding;
    uint32_t trim_version; /* minor[7:0],major[15:8],valid16,PCM17 */
};
_Static_assert(sizeof(struct opencfw_boot_device_feature_record)==16,
               "recovered selector0 feature size");
_Static_assert(offsetof(struct opencfw_boot_device_feature_record,trim_version)==12,
               "recovered feature trim field");
#endif
