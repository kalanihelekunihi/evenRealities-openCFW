/* SPDX-License-Identifier: MIT */

#include <stdint.h>

static uint32_t control_value;
static uint32_t security_value;
static uintptr_t copied_source;
static uintptr_t copied_destination;
static uint32_t copied_size;
static uint32_t copy_count;

#define OPEN_CFW_MEMORY_SELECT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_address_map_4213d8.c"
#include "../../components/bootloader/core_overlay/runtime_memory_select_copy_4213e6.c"

uint32_t open_cfw_memory_select_host_read(uint32_t address)
{
    return address == 0x400201BCU ? control_value : security_value;
}

void open_cfw_bootloader_copy_41d28a(
    const void *source, void *destination, uint32_t size)
{
    copied_source = (uintptr_t)source;
    copied_destination = (uintptr_t)destination;
    copied_size = size;
    copy_count += 1U;
}

void open_cfw_memory_select_fixture_reset(uint32_t control, uint32_t security)
{
    control_value = control;
    security_value = security;
    copied_source = 0U;
    copied_destination = 0U;
    copied_size = 0U;
    copy_count = 0U;
}

uintptr_t open_cfw_memory_select_fixture_value(uint32_t index)
{
    const uintptr_t values[] = {
        copied_source, copied_destination, copied_size, copy_count
    };
    return index < 4U ? values[index] : 0U;
}
