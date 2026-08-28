/* SPDX-License-Identifier: MIT */

#include <stdarg.h>
#include <stdint.h>

#include "../../components/bootloader/core_overlay/runtime_littlefs_read_4212d8.c"

static uint32_t host_status;
static uint32_t host_address;
static uintptr_t host_buffer;
static uint32_t host_size;
static uint32_t host_log_count;
static uint32_t host_log_values[5];

void open_cfw_littlefs_read_fixture_reset(void)
{
    host_status = 0U;
    host_address = 0U;
    host_buffer = 0U;
    host_size = 0U;
    host_log_count = 0U;
    for (uint32_t index = 0U; index < 5U; ++index) {
        host_log_values[index] = 0U;
    }
}

void open_cfw_littlefs_read_fixture_status(uint32_t status)
{
    host_status = status;
}

uint32_t open_cfw_littlefs_read_fixture_value(uint32_t index)
{
    if (index == 0U) {
        return host_address;
    }
    if (index == 1U) {
        return (uint32_t)host_buffer;
    }
    if (index == 2U) {
        return host_size;
    }
    if (index == 3U) {
        return host_log_count;
    }
    if (index >= 4U && index < 9U) {
        return host_log_values[index - 4U];
    }
    return 0U;
}

open_cfw_littlefs_read_u32 open_cfw_bootloader_mspi_read_420f70(
    open_cfw_littlefs_read_u32 address, void *buffer,
    open_cfw_littlefs_read_u32 size)
{
    host_address = address;
    host_buffer = (uintptr_t)buffer;
    host_size = size;
    return host_status;
}

unsigned int open_cfw_bootloader_log_dispatch(const char *format, ...)
{
    va_list arguments;
    (void)format;
    va_start(arguments, format);
    for (uint32_t index = 0U; index < 5U; ++index) {
        host_log_values[index] = va_arg(arguments, uint32_t);
    }
    va_end(arguments);
    ++host_log_count;
    return 0U;
}
