/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bootloader CLKGEN HFADJ configuration
 * leaf at 0x00426C72. The authenticated ABI forces HFADJ enable bit 0 while
 * publishing the caller-provided configuration and returns success.
 */

typedef unsigned int open_cfw_hfadj_config_u32;

#if defined(OPEN_CFW_HFADJ_CONFIG_HOST_TEST)
extern volatile open_cfw_hfadj_config_u32 open_cfw_hfadj_config_host_register;
#define OPEN_CFW_HFADJ_CONFIG_REGISTER open_cfw_hfadj_config_host_register
#else
#define OPEN_CFW_HFADJ_CONFIG_REGISTER \
    (*(volatile open_cfw_hfadj_config_u32 *)(__UINTPTR_TYPE__)0x40004020U)
#endif

__attribute__((used, noinline))
open_cfw_hfadj_config_u32 open_cfw_bootloader_clkgen_hfadj_config_426c72(
    open_cfw_hfadj_config_u32 configuration
)
{
    OPEN_CFW_HFADJ_CONFIG_REGISTER = configuration | 1U;
    return 0U;
}
