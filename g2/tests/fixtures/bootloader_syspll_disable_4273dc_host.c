/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint32_t host_pllctl0;
static uint32_t host_pllctl0_reads;
static uint32_t host_pllctl0_writes;

uint32_t open_cfw_host_syspll_disable_pllctl0_read(void)
{
    host_pllctl0_reads += 1U;
    return host_pllctl0;
}

void open_cfw_host_syspll_disable_pllctl0_write(uint32_t value)
{
    host_pllctl0_writes += 1U;
    host_pllctl0 = value;
}

#define OPEN_CFW_SYSPLL_DISABLE_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_syspll_disable_4273dc.c"

static open_cfw_syspll_disable_state host_state;

void open_cfw_host_syspll_disable_reset(uint32_t prefix, uint32_t module,
                                        uint32_t pllctl0)
{
    host_state.prefix = prefix;
    host_state.module = module;
    host_pllctl0 = pllctl0;
    host_pllctl0_reads = 0U;
    host_pllctl0_writes = 0U;
}

uint32_t open_cfw_host_syspll_disable_call(void)
{
    return open_cfw_bootloader_row6_stop_4273dc(&host_state);
}

uint32_t open_cfw_host_syspll_disable_prefix(void)
{
    return host_state.prefix;
}

uint32_t open_cfw_host_syspll_disable_module(void)
{
    return host_state.module;
}

uint32_t open_cfw_host_syspll_disable_pllctl0(void)
{
    return host_pllctl0;
}

uint32_t open_cfw_host_syspll_disable_pllctl0_reads(void)
{
    return host_pllctl0_reads;
}

uint32_t open_cfw_host_syspll_disable_pllctl0_writes(void)
{
    return host_pllctl0_writes;
}
