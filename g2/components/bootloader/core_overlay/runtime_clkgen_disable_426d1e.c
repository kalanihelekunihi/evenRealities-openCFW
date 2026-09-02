/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bootloader CLKGEN disable entry at
 * 0x00426D1E.
 */

typedef __UINT32_TYPE__ open_cfw_clkgen_disable_u32;

#if defined(OPEN_CFW_CLKGEN_DISABLE_HOST_TEST)
extern volatile open_cfw_clkgen_disable_u32 open_cfw_clkgen_disable_host_register;
#define OPEN_CFW_CLKGEN_DISABLE_REGISTER open_cfw_clkgen_disable_host_register
#else
#define OPEN_CFW_CLKGEN_DISABLE_REGISTER \
    (*(volatile open_cfw_clkgen_disable_u32 *)(__UINTPTR_TYPE__)0x40004050U)
#endif

__attribute__((used, noinline))
open_cfw_clkgen_disable_u32 open_cfw_bootloader_clkgen_disable_426d1e(void)
{
    open_cfw_clkgen_disable_u32 value = OPEN_CFW_CLKGEN_DISABLE_REGISTER;

    value >>= 1;
    value <<= 1;
    OPEN_CFW_CLKGEN_DISABLE_REGISTER = value;
    return 0U;
}
