/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint8_t config_bytes[20];
static uintptr_t observed[3];
static uint32_t call_count;

uint8_t *open_cfw_mspi_xip_host_config(void) { return config_bytes; }
void *open_cfw_mspi_xip_host_handle(void) { return (void *)(uintptr_t)0x2468U; }

uint32_t open_cfw_mspi_xip_host_control(
    void *handle, uint32_t request, void *config)
{
    observed[0] = (uintptr_t)handle;
    observed[1] = request;
    observed[2] = (uintptr_t)config;
    call_count += 1U;
    return 7U;
}

#define OPEN_CFW_MSPI_XIP_CONFIG_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_xip_config_41ff34.c"

void open_cfw_mspi_xip_fixture_reset(void)
{
    uint32_t index;

    for (index = 0U; index < 20U; ++index) {
        config_bytes[index] = (uint8_t)(0xA0U + index);
    }
    observed[0] = 0U;
    observed[1] = 0U;
    observed[2] = 0U;
    call_count = 0U;
}

uint32_t open_cfw_mspi_xip_fixture_count(void) { return call_count; }
uint32_t open_cfw_mspi_xip_fixture_byte(uint32_t index) { return config_bytes[index]; }
uintptr_t open_cfw_mspi_xip_fixture_observed(uint32_t index) { return observed[index]; }
uintptr_t open_cfw_mspi_xip_fixture_config_address(void) { return (uintptr_t)config_bytes; }
