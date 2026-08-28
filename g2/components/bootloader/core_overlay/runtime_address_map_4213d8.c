/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two G2 bootloader address-index helpers. */

typedef __UINT32_TYPE__ open_cfw_address_map_u32;

__attribute__((used, noinline))
open_cfw_address_map_u32 open_cfw_bootloader_address_identity_4213d8(
    open_cfw_address_map_u32 value)
{
    return value;
}

__attribute__((used, noinline))
open_cfw_address_map_u32 open_cfw_bootloader_address_map_4213da(
    open_cfw_address_map_u32 value)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "cmp.w %0, #0x200\n"
        "blo 1f\n"
        "adds.w %0, %0, #0x280\n"
        "1:\n"
        : "+r"(value)
        :
        : "cc");
#else
    if (value >= 0x200U) {
        value += 0x280U;
    }
#endif
    return value;
}
