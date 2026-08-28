/* SPDX-License-Identifier: MIT */

#include <stdarg.h>
#include <stdint.h>

#include "../../components/bootloader/core_overlay/runtime_littlefs_erase_421348.c"

static uint32_t host_status;
static uint32_t host_address;
static uint32_t host_log_count;
static uint32_t host_log_values[3];

void open_cfw_littlefs_erase_fixture_reset(void)
{
    host_status = 0U;
    host_address = 0U;
    host_log_count = 0U;
    for (uint32_t index = 0U; index < 3U; ++index) {
        host_log_values[index] = 0U;
    }
}

void open_cfw_littlefs_erase_fixture_status(uint32_t status)
{
    host_status = status;
}

uint32_t open_cfw_littlefs_erase_fixture_value(uint32_t index)
{
    if (index == 0U) {
        return host_address;
    }
    if (index == 1U) {
        return host_log_count;
    }
    if (index >= 2U && index < 5U) {
        return host_log_values[index - 2U];
    }
    return 0U;
}

open_cfw_littlefs_erase_u32 open_cfw_bootloader_mspi_sector_erase_420a08(
    open_cfw_littlefs_erase_u32 address)
{
    host_address = address;
    return host_status;
}

unsigned int open_cfw_bootloader_log_dispatch(const char *format, ...)
{
    va_list arguments;
    (void)format;
    va_start(arguments, format);
    for (uint32_t index = 0U; index < 3U; ++index) {
        host_log_values[index] = va_arg(arguments, uint32_t);
    }
    va_end(arguments);
    ++host_log_count;
    return 0U;
}
