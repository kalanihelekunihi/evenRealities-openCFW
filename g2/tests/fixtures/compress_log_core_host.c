/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdint.h>
#include <string.h>

#include "../../components/apollo_main/core_overlay/compress_log_core.h"

static unsigned char ring_storage[32768];
static struct open_cfw_compress_log_ring ring_state;
static void *mutex_handle;
static unsigned char mutex_storage[128];
static uint8_t host_sequence;
static uint32_t last_sync_tick;
static unsigned char sync_buffer[32768];
static uint32_t tick_count;
static uint32_t wall_time;
static uint8_t host_mode_value;
static uint8_t filter_level;
static uint32_t exception_number;
static uint32_t sync_calls;
static uint32_t sync_bytes;
static uint32_t schedule_calls;
static uint32_t take_calls;
static uint32_t give_calls;

static void *host_mutex_create(unsigned int type, void *storage)
{
    assert(type == 4u);
    assert(storage == mutex_storage);
    return storage;
}
static int host_mutex_take(void *handle, unsigned int timeout)
{
    assert(handle == mutex_storage);
    assert(timeout == 500u);
    ++take_calls;
    return 1;
}
static int host_mutex_give(void *handle)
{
    assert(handle == mutex_storage);
    ++give_calls;
    return 1;
}
static uint32_t host_set_mask(void) { return 0x55u; }
static void host_clear_mask(uint32_t mask) { assert(mask == 0x55u); }
static void host_enter_critical(void) {}
static void host_exit_critical(void) {}
static int host_allowed_a(void) { return 0; }
static int host_allowed_b(void) { return 1; }
static void host_schedule(void) { ++schedule_calls; }
static uint32_t host_tick(void) { return tick_count; }
static uint32_t host_wall_time(void) { return wall_time; }
static uint8_t host_export_active(void) { return 0u; }
static void host_sync(const unsigned char *data, unsigned int size)
{
    assert(data == sync_buffer);
    ++sync_calls;
    sync_bytes += size;
}

#define OPEN_CFW_COMPRESS_LOG_RING ring_state
#define OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE mutex_handle
#define OPEN_CFW_COMPRESS_LOG_MUTEX_STORAGE ((void *)mutex_storage)
#define OPEN_CFW_COMPRESS_LOG_SEQUENCE host_sequence
#define OPEN_CFW_COMPRESS_LOG_LAST_SYNC_TICK last_sync_tick
#define OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER sync_buffer
#define OPEN_CFW_COMPRESS_LOG_MUTEX_CREATE_STATIC(t, s) host_mutex_create((t), (s))
#define OPEN_CFW_COMPRESS_LOG_MUTEX_TAKE_RECURSIVE(h, t) host_mutex_take((h), (t))
#define OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE(h) host_mutex_give(h)
#define OPEN_CFW_COMPRESS_LOG_ENTER_CRITICAL() host_enter_critical()
#define OPEN_CFW_COMPRESS_LOG_EXIT_CRITICAL() host_exit_critical()
#define OPEN_CFW_COMPRESS_LOG_SET_INTERRUPT_MASK() host_set_mask()
#define OPEN_CFW_COMPRESS_LOG_CLEAR_INTERRUPT_MASK(m) host_clear_mask(m)
#define OPEN_CFW_COMPRESS_LOG_MODE() host_mode_value
#define OPEN_CFW_COMPRESS_LOG_FILTER_LEVEL() filter_level
#define OPEN_CFW_COMPRESS_LOG_TICK_COUNT() host_tick()
#define OPEN_CFW_COMPRESS_LOG_WALL_TIME() host_wall_time()
#define OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_A() host_allowed_a()
#define OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_B() host_allowed_b()
#define OPEN_CFW_COMPRESS_LOG_SCHEDULE_SYNC() host_schedule()
#define OPEN_CFW_COMPRESS_LOG_EXCEPTION_NUMBER() exception_number
#define open_cfw_compress_log_export_active host_export_active
#define open_cfw_compress_log_sync_to_files host_sync
#include "../../components/apollo_main/core_overlay/compress_log_core.c"

static void reset_state(uint32_t capacity)
{
    memset(ring_storage, 0, sizeof(ring_storage));
    memset(sync_buffer, 0, sizeof(sync_buffer));
    ring_state.buffer = ring_storage;
    ring_state.capacity = capacity;
    ring_state.read_offset = 0u;
    ring_state.write_offset = 0u;
    mutex_handle = NULL;
    host_sequence = 0u;
    last_sync_tick = 0u;
    tick_count = 0u;
    wall_time = 0u;
    host_mode_value = 1u;
    filter_level = 7u;
    exception_number = 0u;
    sync_calls = 0u;
    sync_bytes = 0u;
    schedule_calls = 0u;
    take_calls = 0u;
    give_calls = 0u;
}

static uint32_t load_u32(const unsigned char *data)
{
    uint32_t value;
    memcpy(&value, data, sizeof(value));
    return value;
}

int main(void)
{
    unsigned char output[64];
    uint32_t metadata;

    reset_state(sizeof(ring_storage));
    open_cfw_compress_log_mutex_init();
    assert(mutex_handle == mutex_storage);
    tick_count = 2345u;
    wall_time = 0x12345678u;
    metadata = (3u << 26) | (3u << 22) | 0x00123456u;
    open_cfw_compress_log_output(metadata, 0x00654321u, "%u:%s:%f",
        0x89abcdefu, "abcdefghijklmnopQRST", 1.5);
    assert(ring_state.write_offset == 36u);
    assert(load_u32(ring_storage) ==
        (0xDC00007Bu | ((2345u % 1000u) << 16)));
    assert(load_u32(ring_storage + 4u) == wall_time);
    assert((load_u32(ring_storage + 8u) & 0x003fffffu) ==
        (0x00654321u & 0x003fffffu));
    assert(((load_u32(ring_storage + 8u) >> 22) & 0xfu) == 3u);
    assert(load_u32(ring_storage + 12u) == 0x89abcdefu);
    assert(memcmp(ring_storage + 16u, "efghijklmnopQRST", 16u) == 0);
    assert(load_u32(ring_storage + 32u) == 0x3fc00000u);

    assert(open_cfw_compress_log_get_all_buffer(output, 36u) == 1);
    assert(memcmp(output, ring_storage, 36u) == 0);
    assert(ring_state.read_offset == ring_state.write_offset);

    reset_state(128u);
    open_cfw_compress_log_mutex_init();
    ring_state.write_offset = 120u;
    memset(ring_storage, 0xaa, 120u);
    assert(open_cfw_compress_log_ring_write("0123456789", 10u) == 0);
    assert(schedule_calls == 1u);

    reset_state(sizeof(ring_storage));
    open_cfw_compress_log_mutex_init();
    memset(ring_storage, 0x5a, 9000u);
    ring_state.write_offset = 9000u;
    tick_count = 10001u;
    open_cfw_compress_log_periodic_sync();
    assert(sync_calls == 2u);
    assert(sync_bytes == 8192u);
    assert(ring_state.read_offset == 8192u);
    open_cfw_compress_log_force_sync();
    assert(sync_calls == 3u);
    assert(sync_bytes == 9000u);
    assert(ring_state.read_offset == ring_state.write_offset);

    exception_number = 3u;
    assert(open_cfw_compress_log_ring_read_locked(output, 1u) == 0);
    assert(take_calls == give_calls);
    return 0;
}
