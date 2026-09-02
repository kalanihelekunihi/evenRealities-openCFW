/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0
 * am_hal_syspll_initialize(), authenticated at bootloader address
 * 0x004272ac.  The exported name retains the row-six client ABI used by the
 * already source-owned caller at 0x0042215e.
 */

typedef __UINT32_TYPE__ open_cfw_syspll_initialize_u32;

typedef struct open_cfw_syspll_initialize_state {
    open_cfw_syspll_initialize_u32 prefix;
    open_cfw_syspll_initialize_u32 module;
} open_cfw_syspll_initialize_state;

#define OPEN_CFW_SYSPLL_INITIALIZE_MODULES 1U
#define OPEN_CFW_SYSPLL_INITIALIZE_BIT     0x01000000U
#define OPEN_CFW_SYSPLL_HANDLE_MAGIC       0x00504c30U

#if defined(OPEN_CFW_SYSPLL_INITIALIZE_HOST_TEST)
extern volatile open_cfw_syspll_initialize_state
    open_cfw_host_syspll_initialize_state[OPEN_CFW_SYSPLL_INITIALIZE_MODULES];
extern void open_cfw_host_pwrctrl_syspll_enable(void);
#define OPEN_CFW_SYSPLL_INITIALIZE_STATE open_cfw_host_syspll_initialize_state
#define OPEN_CFW_SYSPLL_POWER_ENABLE() open_cfw_host_pwrctrl_syspll_enable()
#else
#define OPEN_CFW_SYSPLL_INITIALIZE_STATE                                  \
    ((volatile open_cfw_syspll_initialize_state *)(__UINTPTR_TYPE__)      \
        0x20027010U)
extern void open_cfw_bootloader_pwrctrl_syspll_enable_41ca5c(void);
#define OPEN_CFW_SYSPLL_POWER_ENABLE()                                    \
    open_cfw_bootloader_pwrctrl_syspll_enable_41ca5c()
#endif

__attribute__((used, noinline))
open_cfw_syspll_initialize_u32 open_cfw_bootloader_row6_create_4272ac(
    open_cfw_syspll_initialize_u32 module,
    volatile open_cfw_syspll_initialize_state **output_handle)
{
    volatile open_cfw_syspll_initialize_state *state;
    open_cfw_syspll_initialize_u32 prefix;

    if (module >= OPEN_CFW_SYSPLL_INITIALIZE_MODULES) {
        return 5U;
    }
    if (output_handle ==
            (volatile open_cfw_syspll_initialize_state **)0) {
        return 6U;
    }

    state = &OPEN_CFW_SYSPLL_INITIALIZE_STATE[module];
    prefix = state->prefix;
    if ((prefix & OPEN_CFW_SYSPLL_INITIALIZE_BIT) != 0U) {
        return 7U;
    }

    prefix |= OPEN_CFW_SYSPLL_INITIALIZE_BIT;
    state->prefix =
        (prefix & 0xff000000U) | OPEN_CFW_SYSPLL_HANDLE_MAGIC;
    state->module = module;
    OPEN_CFW_SYSPLL_POWER_ENABLE();
    *output_handle = state;
    return 0U;
}
