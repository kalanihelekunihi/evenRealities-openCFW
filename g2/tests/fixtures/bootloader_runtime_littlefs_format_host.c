#include <stdint.h>

#define OPEN_CFW_LITTLEFS_FORMAT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_littlefs_format_4211b0.c"

static int32_t results[4];
static int32_t events[16];
static uint32_t event_count;

static void fixture_event(int32_t kind, int32_t value)
{
    if (event_count + 2U <= 16U) {
        events[event_count++] = kind;
        events[event_count++] = value;
    }
}

void open_cfw_littlefs_format_fixture_reset(void)
{
    uint32_t index;
    for (index = 0U; index < 4U; ++index) results[index] = 0;
    for (index = 0U; index < 16U; ++index) events[index] = 0;
    event_count = 0U;
}

void open_cfw_littlefs_format_fixture_config(uint32_t operation, int32_t result)
{
    if (operation < 4U) results[operation] = result;
}

int32_t open_cfw_littlefs_format_fixture_value(uint32_t index)
{
    if (index == 16U) return (int32_t)event_count;
    return index < 16U ? events[index] : 0;
}

open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_unmount(void)
{
    fixture_event(1, results[0]);
    return results[0];
}

open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_format(void)
{
    fixture_event(2, results[1]);
    return results[1];
}

open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_mount(void)
{
    fixture_event(3, results[2]);
    return results[2];
}

open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_directories(void)
{
    fixture_event(4, results[3]);
    return results[3];
}

void open_cfw_littlefs_format_host_log(
    open_cfw_littlefs_format_i32 kind, open_cfw_littlefs_format_i32 status)
{
    fixture_event(10 + kind, status);
}
