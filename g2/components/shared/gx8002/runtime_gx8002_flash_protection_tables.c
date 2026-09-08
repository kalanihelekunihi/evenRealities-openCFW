/* SPDX-License-Identifier: MIT */
/* Recovered protection policies. Masks/values are interpreted by the source
 * protection query/setter; lengths name the protected prefix in bytes. */
#include "runtime_gx8002_flash_protection_tables.h"
#define UNPROTECTED { .status1_mask=0x9c, .status2_mask=0x41 }
#define PREFIX(value, complement, blocks) { .status1_value=(value), \
    .status1_mask=0xfc, .status2_value=(complement), .status2_mask=0x41, \
    .protected_bytes=(blocks)*65536u }
const struct open_cfw_flash_protection_entry open_cfw_gx8002_flash_protection_256k[]={
    UNPROTECTED, PREFIX(0x24,0,1), PREFIX(0x28,0,2),
    PREFIX(0x04,0x40,3), PREFIX(0x1c,0,4)
};
const struct open_cfw_flash_protection_entry open_cfw_gx8002_flash_protection_512k[]={
    UNPROTECTED, PREFIX(0x24,0,1), PREFIX(0x28,0,2), PREFIX(0x2c,0,4),
    PREFIX(0x08,0x40,6), PREFIX(0x04,0x40,7), PREFIX(0x1c,0,8)
};
const struct open_cfw_flash_protection_entry open_cfw_gx8002_flash_protection_1024k[]={
    UNPROTECTED, PREFIX(0x24,0,1), PREFIX(0x28,0,2), PREFIX(0x2c,0,4),
    PREFIX(0x30,0,8), PREFIX(0x0c,0x40,12), PREFIX(0x08,0x40,14),
    PREFIX(0x04,0x40,15), PREFIX(0x1c,0,16)
};
