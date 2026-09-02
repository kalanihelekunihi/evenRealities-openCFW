/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bootloader CLKGEN HFADJ disable leaf at
 * 0x00426C7E. The authenticated ABI clears only HFADJ enable bit 0 and returns
 * success.
 */

typedef unsigned int open_cfw_hfadj_disable_u32;

#if defined(OPEN_CFW_HFADJ_DISABLE_HOST_TEST)
extern volatile open_cfw_hfadj_disable_u32 open_cfw_hfadj_disable_host_register;
#define OPEN_CFW_HFADJ_DISABLE_REGISTER open_cfw_hfadj_disable_host_register
#else
#define OPEN_CFW_HFADJ_DISABLE_REGISTER \
    (*(volatile open_cfw_hfadj_disable_u32 *)(__UINTPTR_TYPE__)0x40004020U)
#endif

__attribute__((used, noinline))
open_cfw_hfadj_disable_u32 open_cfw_bootloader_clkgen_hfadj_disable_426c7e(void)
{
    open_cfw_hfadj_disable_u32 value = OPEN_CFW_HFADJ_DISABLE_REGISTER;
    value &= ~1U;
    OPEN_CFW_HFADJ_DISABLE_REGISTER = value;
    return 0U;
}
