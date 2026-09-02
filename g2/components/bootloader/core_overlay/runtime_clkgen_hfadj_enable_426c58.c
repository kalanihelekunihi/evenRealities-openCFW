/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bootloader CLKGEN HFADJ enable leaf at
 * 0x00426C58.  The authenticated ABI treats the low input byte as a boolean,
 * updates only HFADJ bit 0, and returns success.
 */

typedef unsigned int open_cfw_hfadj_u32;

#if defined(OPEN_CFW_HFADJ_HOST_TEST)
extern volatile open_cfw_hfadj_u32 open_cfw_hfadj_host_register;
#define OPEN_CFW_HFADJ_REGISTER open_cfw_hfadj_host_register
#else
#define OPEN_CFW_HFADJ_REGISTER \
    (*(volatile open_cfw_hfadj_u32 *)(__UINTPTR_TYPE__)0x40004044U)
#endif

__attribute__((used, noinline))
open_cfw_hfadj_u32 open_cfw_bootloader_clkgen_hfadj_enable_426c58(
    open_cfw_hfadj_u32 enable
)
{
    open_cfw_hfadj_u32 bit = (enable & 0xFFU) != 0U ? 1U : 0U;
    open_cfw_hfadj_u32 value = OPEN_CFW_HFADJ_REGISTER;
    value = (value & ~1U) | bit;
    OPEN_CFW_HFADJ_REGISTER = value;
    return 0U;
}
