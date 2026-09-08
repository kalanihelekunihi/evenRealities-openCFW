/* SPDX-License-Identifier: MIT */
/* OTP region accessors recovered from image-A 0x15b38..0x15ba0.
 * Selected device and OTP descriptor must be valid, as in the original. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
static inline volatile uint32_t *otp(void)
{
    volatile uint32_t *device=(volatile uint32_t *)(uintptr_t)open_cfw_gx8002_flash_state.selected_device;
    return (volatile uint32_t *)(uintptr_t)device[5];
}
int open_cfw_gx8002_flash_otp_get_region(unsigned *count)
{
    *count=otp()[3];
    return 0;
}
int open_cfw_gx8002_flash_otp_set_region(unsigned region)
{
    volatile uint32_t *descriptor=otp();
    if (region>=descriptor[3]) return -1;
    descriptor[4]=(descriptor[4]&~7u)|region;
    return 0;
}
int open_cfw_gx8002_flash_otp_get_current_region(unsigned *region)
{
    *region=otp()[4]&7u;
    return 0;
}
int open_cfw_gx8002_flash_otp_get_region_size(unsigned *size)
{
    *size=otp()[2];
    return 0;
}
