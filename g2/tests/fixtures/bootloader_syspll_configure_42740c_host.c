/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint32_t host_pllctl0;
static uint32_t host_plldiv0;
static uint32_t host_plldiv1;
static uint32_t host_pllctl0_reads;
static uint32_t host_pllctl0_writes;
static uint32_t host_plldiv0_reads;
static uint32_t host_plldiv0_writes;
static uint32_t host_plldiv1_reads;
static uint32_t host_plldiv1_writes;
static uint32_t host_fref_calls;
static uint32_t host_fref_value;

uint32_t open_cfw_host_syspll_configure_pllctl0_read(void)
{
    host_pllctl0_reads += 1U;
    return host_pllctl0;
}

void open_cfw_host_syspll_configure_pllctl0_write(uint32_t value)
{
    host_pllctl0_writes += 1U;
    host_pllctl0 = value;
}

uint32_t open_cfw_host_syspll_configure_plldiv0_read(void)
{
    host_plldiv0_reads += 1U;
    return host_plldiv0;
}

void open_cfw_host_syspll_configure_plldiv0_write(uint32_t value)
{
    host_plldiv0_writes += 1U;
    host_plldiv0 = value;
}

uint32_t open_cfw_host_syspll_configure_plldiv1_read(void)
{
    host_plldiv1_reads += 1U;
    return host_plldiv1;
}

void open_cfw_host_syspll_configure_plldiv1_write(uint32_t value)
{
    host_plldiv1_writes += 1U;
    host_plldiv1 = value;
}

void open_cfw_host_syspll_configure_fref_update(uint32_t value)
{
    host_fref_calls += 1U;
    host_fref_value = value;
}

#define OPEN_CFW_SYSPLL_CONFIGURE_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_syspll_configure_42740c.c"

static open_cfw_syspll_configure_state host_state;
static open_cfw_syspll_configure_config host_config;

void open_cfw_host_syspll_configure_reset(
    uint32_t prefix, uint32_t module, uint32_t fref, uint32_t vco,
    uint32_t fraction_mode, uint32_t reference_divider,
    uint32_t post_divider_1, uint32_t post_divider_2,
    uint32_t feedback_integer, uint32_t feedback_fraction,
    uint32_t pllctl0, uint32_t plldiv0, uint32_t plldiv1)
{
    host_state.prefix = prefix;
    host_state.module = module;
    host_config.fref = (uint8_t)fref;
    host_config.vco_select = (uint8_t)vco;
    host_config.fraction_mode = (uint8_t)fraction_mode;
    host_config.reference_divider = (uint8_t)reference_divider;
    host_config.post_divider_1 = (uint8_t)post_divider_1;
    host_config.post_divider_2 = (uint8_t)post_divider_2;
    host_config.feedback_divider_integer = (uint16_t)feedback_integer;
    host_config.feedback_divider_fraction = feedback_fraction;
    host_pllctl0 = pllctl0;
    host_plldiv0 = plldiv0;
    host_plldiv1 = plldiv1;
    host_pllctl0_reads = 0U;
    host_pllctl0_writes = 0U;
    host_plldiv0_reads = 0U;
    host_plldiv0_writes = 0U;
    host_plldiv1_reads = 0U;
    host_plldiv1_writes = 0U;
    host_fref_calls = 0U;
    host_fref_value = 0U;
}

uint32_t open_cfw_host_syspll_configure_call(void)
{
    return open_cfw_bootloader_row6_configure_42740c(&host_state, &host_config);
}

#define OPEN_CFW_HOST_GETTER(name, value) \
    uint32_t name(void) { return (value); }
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_pllctl0, host_pllctl0)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_plldiv0, host_plldiv0)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_plldiv1, host_plldiv1)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_pllctl0_reads,
                     host_pllctl0_reads)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_pllctl0_writes,
                     host_pllctl0_writes)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_plldiv0_reads,
                     host_plldiv0_reads)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_plldiv0_writes,
                     host_plldiv0_writes)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_plldiv1_reads,
                     host_plldiv1_reads)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_plldiv1_writes,
                     host_plldiv1_writes)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_fref_calls,
                     host_fref_calls)
OPEN_CFW_HOST_GETTER(open_cfw_host_syspll_configure_fref_value,
                     host_fref_value)
