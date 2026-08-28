#include <stdint.h>

#define OPEN_CFW_LITTLEFS_INIT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_littlefs_init_421210.c"

static int32_t results[11];
static int32_t events[48];
static uint32_t event_count;
static uint32_t mount_call_count;
static int32_t ready;
static int32_t written_count;
static uint32_t open_flags;

static void fixture_event(int32_t kind, int32_t value)
{
    if (event_count + 2U <= 48U) {
        events[event_count++] = kind;
        events[event_count++] = value;
    }
}

void open_cfw_littlefs_init_fixture_reset(void)
{
    uint32_t index;
    for (index = 0U; index < 11U; ++index) results[index] = 0;
    for (index = 0U; index < 48U; ++index) events[index] = 0;
    event_count = 0U;
    mount_call_count = 0U;
    ready = 0;
    written_count = 0;
    open_flags = 0U;
}

void open_cfw_littlefs_init_fixture_config(uint32_t operation, int32_t value)
{
    if (operation < 11U) results[operation] = value;
}

int32_t open_cfw_littlefs_init_fixture_value(uint32_t index)
{
    if (index == 48U) return (int32_t)event_count;
    if (index == 49U) return ready;
    if (index == 50U) return written_count;
    if (index == 51U) return (int32_t)open_flags;
    if (index == 52U) return (int32_t)mount_call_count;
    return index < 48U ? events[index] : 0;
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_mount(void)
{
    uint32_t index = mount_call_count++;
    int32_t value = results[index < 2U ? index : 1U];
    fixture_event(1, value);
    return value;
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_format(void)
{
    fixture_event(2, results[2]);
    return results[2];
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_directories(void)
{
    fixture_event(3, results[3]);
    return results[3];
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_recovery(void)
{
    fixture_event(4, results[4]);
    return results[4];
}

void open_cfw_littlefs_init_host_ready(void)
{
    ready = 1;
    fixture_event(5, 1);
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_open(
    open_cfw_littlefs_init_u32 flags)
{
    open_flags = flags;
    fixture_event(6, results[5]);
    return results[5];
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_read(
    open_cfw_littlefs_init_i32 *count, open_cfw_littlefs_init_u32 size)
{
    if (size == 4U) *count = results[10];
    fixture_event(7, results[6]);
    return results[6];
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_rewind(void)
{
    fixture_event(8, results[7]);
    return results[7];
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_write(
    const open_cfw_littlefs_init_i32 *count, open_cfw_littlefs_init_u32 size)
{
    if (size == 4U) written_count = *count;
    fixture_event(9, results[8]);
    return results[8];
}

open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_close(void)
{
    fixture_event(10, results[9]);
    return results[9];
}

void open_cfw_littlefs_init_host_log(
    open_cfw_littlefs_init_i32 kind, open_cfw_littlefs_init_i32 value)
{
    fixture_event(10 + kind, value);
}
