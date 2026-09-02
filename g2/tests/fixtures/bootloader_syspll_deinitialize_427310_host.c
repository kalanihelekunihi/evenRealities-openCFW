/* SPDX-License-Identifier: MIT */
#define OPEN_CFW_SYSPLL_DEINITIALIZE_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_syspll_deinitialize_427310.c"

static open_cfw_syspll_deinitialize_state
    open_cfw_host_syspll_deinitialize_state;
static open_cfw_syspll_deinitialize_u32 open_cfw_host_stop_status;
static open_cfw_syspll_deinitialize_u32 open_cfw_host_power_query_status;
static open_cfw_syspll_deinitialize_u32 open_cfw_host_power_disable_status;
static _Bool open_cfw_host_power_enabled;
static open_cfw_syspll_deinitialize_u32 open_cfw_host_stop_calls;
static open_cfw_syspll_deinitialize_u32 open_cfw_host_power_query_calls;
static open_cfw_syspll_deinitialize_u32 open_cfw_host_power_disable_calls;
static open_cfw_syspll_deinitialize_u32 open_cfw_host_trace;

open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_stop(
    open_cfw_syspll_deinitialize_state *state)
{
    (void)state;
    open_cfw_host_stop_calls++;
    open_cfw_host_trace = open_cfw_host_trace * 10U + 1U;
    return open_cfw_host_stop_status;
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_pwrctrl_syspll_enabled(_Bool *enabled)
{
    open_cfw_host_power_query_calls++;
    open_cfw_host_trace = open_cfw_host_trace * 10U + 2U;
    *enabled = open_cfw_host_power_enabled;
    return open_cfw_host_power_query_status;
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_pwrctrl_syspll_disable(void)
{
    open_cfw_host_power_disable_calls++;
    open_cfw_host_trace = open_cfw_host_trace * 10U + 3U;
    return open_cfw_host_power_disable_status;
}

void open_cfw_host_syspll_deinitialize_reset(
    open_cfw_syspll_deinitialize_u32 prefix,
    open_cfw_syspll_deinitialize_u32 stop_status,
    open_cfw_syspll_deinitialize_u32 power_query_status,
    open_cfw_syspll_deinitialize_u32 power_disable_status,
    open_cfw_syspll_deinitialize_u32 power_enabled)
{
    open_cfw_host_syspll_deinitialize_state.prefix = prefix;
    open_cfw_host_syspll_deinitialize_state.module = 0U;
    open_cfw_host_stop_status = stop_status;
    open_cfw_host_power_query_status = power_query_status;
    open_cfw_host_power_disable_status = power_disable_status;
    open_cfw_host_power_enabled = power_enabled != 0U;
    open_cfw_host_stop_calls = 0U;
    open_cfw_host_power_query_calls = 0U;
    open_cfw_host_power_disable_calls = 0U;
    open_cfw_host_trace = 0U;
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_call(void)
{
    return open_cfw_bootloader_row6_destroy_427310(
        &open_cfw_host_syspll_deinitialize_state);
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_prefix(void)
{
    return open_cfw_host_syspll_deinitialize_state.prefix;
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_stop_calls(void)
{
    return open_cfw_host_stop_calls;
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_power_query_calls(void)
{
    return open_cfw_host_power_query_calls;
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_power_disable_calls(void)
{
    return open_cfw_host_power_disable_calls;
}

open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_trace(void)
{
    return open_cfw_host_trace;
}
