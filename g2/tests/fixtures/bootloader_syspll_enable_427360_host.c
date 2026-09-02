/* SPDX-License-Identifier: MIT */
#define OPEN_CFW_SYSPLL_ENABLE_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_syspll_enable_427360.c"

static open_cfw_syspll_enable_state open_cfw_host_syspll_enable_state;
static open_cfw_syspll_enable_u32 open_cfw_host_vrctrl;
static open_cfw_syspll_enable_u32 open_cfw_host_pllctl0;
static open_cfw_syspll_enable_u32 open_cfw_host_vrctrl_reads;
static open_cfw_syspll_enable_u32 open_cfw_host_pllctl0_reads;
static open_cfw_syspll_enable_u32 open_cfw_host_pllctl0_writes;

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_vrctrl_read(void)
{
    open_cfw_host_vrctrl_reads++;
    return open_cfw_host_vrctrl;
}

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_pllctl0_read(void)
{
    open_cfw_host_pllctl0_reads++;
    return open_cfw_host_pllctl0;
}

void open_cfw_host_syspll_enable_pllctl0_write(
    open_cfw_syspll_enable_u32 value)
{
    open_cfw_host_pllctl0_writes++;
    open_cfw_host_pllctl0 = value;
}

void open_cfw_host_syspll_enable_reset(
    open_cfw_syspll_enable_u32 prefix,
    open_cfw_syspll_enable_u32 vrctrl,
    open_cfw_syspll_enable_u32 pllctl0)
{
    open_cfw_host_syspll_enable_state.prefix = prefix;
    open_cfw_host_syspll_enable_state.module = 0U;
    open_cfw_host_vrctrl = vrctrl;
    open_cfw_host_pllctl0 = pllctl0;
    open_cfw_host_vrctrl_reads = 0U;
    open_cfw_host_pllctl0_reads = 0U;
    open_cfw_host_pllctl0_writes = 0U;
}

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_call(void)
{
    return open_cfw_bootloader_row6_start_427360(
        &open_cfw_host_syspll_enable_state);
}

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_prefix(void)
{
    return open_cfw_host_syspll_enable_state.prefix;
}

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_pllctl0(void)
{
    return open_cfw_host_pllctl0;
}

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_vrctrl_reads(void)
{
    return open_cfw_host_vrctrl_reads;
}

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_pllctl0_reads(void)
{
    return open_cfw_host_pllctl0_reads;
}

open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_pllctl0_writes(void)
{
    return open_cfw_host_pllctl0_writes;
}
