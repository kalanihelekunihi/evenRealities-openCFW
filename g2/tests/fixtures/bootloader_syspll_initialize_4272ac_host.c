/* SPDX-License-Identifier: MIT */
#define OPEN_CFW_SYSPLL_INITIALIZE_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_syspll_initialize_4272ac.c"

volatile open_cfw_syspll_initialize_state
    open_cfw_host_syspll_initialize_state[OPEN_CFW_SYSPLL_INITIALIZE_MODULES];

static open_cfw_syspll_initialize_u32 open_cfw_host_power_enable_calls;

void open_cfw_host_pwrctrl_syspll_enable(void)
{
    open_cfw_host_power_enable_calls++;
}

void open_cfw_host_syspll_initialize_reset(
    open_cfw_syspll_initialize_u32 prefix,
    open_cfw_syspll_initialize_u32 module)
{
    open_cfw_host_syspll_initialize_state[0].prefix = prefix;
    open_cfw_host_syspll_initialize_state[0].module = module;
    open_cfw_host_power_enable_calls = 0U;
}

open_cfw_syspll_initialize_u32
open_cfw_host_syspll_initialize_prefix(void)
{
    return open_cfw_host_syspll_initialize_state[0].prefix;
}

open_cfw_syspll_initialize_u32
open_cfw_host_syspll_initialize_module(void)
{
    return open_cfw_host_syspll_initialize_state[0].module;
}

open_cfw_syspll_initialize_u32
open_cfw_host_syspll_initialize_power_calls(void)
{
    return open_cfw_host_power_enable_calls;
}
