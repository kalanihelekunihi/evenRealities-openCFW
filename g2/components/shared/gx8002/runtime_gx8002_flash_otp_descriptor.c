/* SPDX-License-Identifier: MIT */
/* Configuration recovered from the shipped descriptor at 0x200266cc.
 * Address formation is established by OTP read at image-A 0x15fb8;
 * size/count/selection by the four separately recovered region accessors. */
#include <stdint.h>
struct open_cfw_gx8002_otp_descriptor {
    uint32_t base_address;
    uint32_t region_stride;
    uint32_t region_bytes;
    uint32_t region_count;
    uint32_t selection_flags;
};
struct open_cfw_gx8002_otp_descriptor open_cfw_gx8002_flash_otp_descriptor = {
    .base_address = 0x1000,
    .region_stride = 0x1000,
    .region_bytes = 512,
    .region_count = 3,
    .selection_flags = 0,
};
_Static_assert(sizeof(struct open_cfw_gx8002_otp_descriptor)==20,"descriptor size");
