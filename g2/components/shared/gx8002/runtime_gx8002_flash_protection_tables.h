/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_FLASH_PROTECTION_TABLES_H
#define OPEN_CFW_FLASH_PROTECTION_TABLES_H
#include <stdint.h>
#include <stddef.h>
struct open_cfw_flash_protection_entry {
    uint8_t status1_value, status1_mask, status2_value, status2_mask;
    uint32_t protected_bytes;
};
_Static_assert(sizeof(struct open_cfw_flash_protection_entry)==8,"entry size");
_Static_assert(offsetof(struct open_cfw_flash_protection_entry,protected_bytes)==4,"length offset");
extern const struct open_cfw_flash_protection_entry open_cfw_gx8002_flash_protection_256k[5];
extern const struct open_cfw_flash_protection_entry open_cfw_gx8002_flash_protection_512k[7];
extern const struct open_cfw_flash_protection_entry open_cfw_gx8002_flash_protection_1024k[9];
#endif
