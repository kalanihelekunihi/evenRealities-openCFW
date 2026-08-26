#include "thread_ring_host.h"

#include <stdlib.h>
#include <string.h>

void *host_thread_ring_thread_id;
void *host_thread_ring_queue_id;
uint32_t host_thread_ring_thread_new_count;
uint32_t host_thread_ring_thread_terminate_count;
uint32_t host_thread_ring_queue_new_count;
uint32_t host_thread_ring_queue_delete_count;
uint32_t host_thread_ring_queue_count;
uint32_t host_thread_ring_queue_depth;
uint32_t host_thread_ring_queue_item_size;
uint32_t host_thread_ring_queue_put_fail;
uint32_t host_thread_ring_alloc_fail;
uint32_t host_thread_ring_alloc_count;
uint32_t host_thread_ring_free_count;
uint32_t host_thread_ring_assert_count;
uint32_t host_thread_ring_flags;
uint32_t host_thread_ring_active_index;
uint32_t host_thread_ring_ready_index;
uint32_t host_thread_ring_exit_index;
uint32_t host_thread_ring_exit_wait_count;
uint32_t host_thread_ring_remove_count;
uint32_t host_thread_ring_push_count;
uint32_t host_thread_ring_push_delays[16];
uintptr_t host_thread_ring_push_callbacks[16];
uint8_t host_thread_ring_connection_state;
uint32_t host_thread_ring_phone_role_value;
uint32_t host_thread_ring_heartbeat_count;
uint32_t host_thread_ring_touch_time_count;
uint16_t host_thread_ring_touch_time_value;
uint32_t host_thread_ring_touch_enable_count;
uint8_t host_thread_ring_touch_enable_value;
uint32_t host_thread_ring_status_count;
uint8_t host_thread_ring_status_values[2];
uint32_t host_thread_ring_post_touch_count;
uint8_t host_thread_ring_post_touch_value;
uint32_t host_thread_ring_glasses_status_count;
uint32_t host_thread_ring_pair_count;
uint32_t host_thread_ring_owner_callback_count;
uint32_t host_thread_ring_touch_error_count;
uint32_t host_thread_ring_disconnect_count;
uint32_t host_thread_ring_parse_count;
uint16_t host_thread_ring_parse_length;
uint8_t host_thread_ring_parse_data[32];

static void *host_thread_ring_records[8];

void host_thread_ring_reset(void)
{
    uint32_t index;

    for (index = 0u; index < host_thread_ring_queue_count; ++index) {
        free(host_thread_ring_records[index]);
    }
    host_thread_ring_thread_id = NULL;
    host_thread_ring_queue_id = NULL;
    host_thread_ring_thread_new_count = 0u;
    host_thread_ring_thread_terminate_count = 0u;
    host_thread_ring_queue_new_count = 0u;
    host_thread_ring_queue_delete_count = 0u;
    host_thread_ring_queue_count = 0u;
    host_thread_ring_queue_depth = 0u;
    host_thread_ring_queue_item_size = 0u;
    host_thread_ring_queue_put_fail = 0u;
    host_thread_ring_alloc_fail = 0u;
    host_thread_ring_alloc_count = 0u;
    host_thread_ring_free_count = 0u;
    host_thread_ring_assert_count = 0u;
    host_thread_ring_flags = 0u;
    host_thread_ring_active_index = 0u;
    host_thread_ring_ready_index = 0u;
    host_thread_ring_exit_index = 0u;
    host_thread_ring_exit_wait_count = 0u;
    host_thread_ring_remove_count = 0u;
    host_thread_ring_push_count = 0u;
    host_thread_ring_connection_state = 0u;
    host_thread_ring_phone_role_value = 0u;
    host_thread_ring_heartbeat_count = 0u;
    host_thread_ring_touch_time_count = 0u;
    host_thread_ring_touch_time_value = 0u;
    host_thread_ring_touch_enable_count = 0u;
    host_thread_ring_touch_enable_value = 0u;
    host_thread_ring_status_count = 0u;
    host_thread_ring_status_values[0] = 0u;
    host_thread_ring_status_values[1] = 0u;
    host_thread_ring_post_touch_count = 0u;
    host_thread_ring_post_touch_value = 0u;
    host_thread_ring_glasses_status_count = 0u;
    host_thread_ring_pair_count = 0u;
    host_thread_ring_owner_callback_count = 0u;
    host_thread_ring_touch_error_count = 0u;
    host_thread_ring_disconnect_count = 0u;
    host_thread_ring_parse_count = 0u;
    host_thread_ring_parse_length = 0u;
    memset(host_thread_ring_records, 0, sizeof(host_thread_ring_records));
    memset(host_thread_ring_push_delays, 0,
           sizeof(host_thread_ring_push_delays));
    memset(host_thread_ring_push_callbacks, 0,
           sizeof(host_thread_ring_push_callbacks));
    memset(host_thread_ring_parse_data, 0, sizeof(host_thread_ring_parse_data));
}

void *host_thread_ring_thread_new(
    void (*entry)(void *), void *argument, const void *attributes)
{
    (void)entry;
    (void)argument;
    (void)attributes;
    ++host_thread_ring_thread_new_count;
    return (void *)(uintptr_t)0x1001u;
}

int32_t host_thread_ring_thread_terminate(void *thread_id)
{
    (void)thread_id;
    ++host_thread_ring_thread_terminate_count;
    return 0;
}

uint32_t host_thread_ring_flags_set(void *thread_id, uint32_t flags)
{
    (void)thread_id;
    host_thread_ring_flags |= flags;
    return host_thread_ring_flags;
}

uint32_t host_thread_ring_flags_wait(
    uint32_t flags, uint32_t options, uint32_t timeout)
{
    (void)flags;
    (void)options;
    (void)timeout;
    return 0x80000000u;
}

int32_t host_thread_ring_delay(uint32_t ticks)
{
    (void)ticks;
    return 0;
}

void *host_thread_ring_queue_new(
    uint32_t count, uint32_t size, const void *attributes)
{
    (void)attributes;
    ++host_thread_ring_queue_new_count;
    host_thread_ring_queue_depth = count;
    host_thread_ring_queue_item_size = size;
    return (void *)(uintptr_t)0x2001u;
}

int32_t host_thread_ring_queue_put(
    void *queue_id, const void *message, uint8_t priority, uint32_t timeout)
{
    (void)queue_id;
    (void)priority;
    (void)timeout;
    if (host_thread_ring_queue_put_fail != 0u ||
        host_thread_ring_queue_count >= 8u) {
        return -1;
    }
    host_thread_ring_records[host_thread_ring_queue_count++] =
        *(void * const *)message;
    return 0;
}

int32_t host_thread_ring_queue_get(
    void *queue_id, void *message, uint8_t *priority, uint32_t timeout)
{
    uint32_t index;

    (void)queue_id;
    (void)priority;
    (void)timeout;
    if (host_thread_ring_queue_count == 0u) {
        return -1;
    }
    *(void **)message = host_thread_ring_records[0];
    --host_thread_ring_queue_count;
    for (index = 0u; index < host_thread_ring_queue_count; ++index) {
        host_thread_ring_records[index] = host_thread_ring_records[index + 1u];
    }
    host_thread_ring_records[host_thread_ring_queue_count] = NULL;
    return 0;
}

int32_t host_thread_ring_queue_delete(void *queue_id)
{
    (void)queue_id;
    ++host_thread_ring_queue_delete_count;
    return 0;
}

void host_thread_ring_assert_fail(void)
{
    ++host_thread_ring_assert_count;
}

void *host_thread_ring_alloc(size_t size)
{
    if (host_thread_ring_alloc_fail != 0u) {
        return NULL;
    }
    ++host_thread_ring_alloc_count;
    return malloc(size);
}

void host_thread_ring_free(void *allocation)
{
    ++host_thread_ring_free_count;
    free(allocation);
}

void host_thread_ring_state_active(uint32_t thread_index)
{
    host_thread_ring_active_index = thread_index;
}

void host_thread_ring_state_ready(uint32_t thread_index)
{
    host_thread_ring_ready_index = thread_index;
}

void host_thread_ring_state_exit(uint32_t thread_index)
{
    host_thread_ring_exit_index = thread_index;
}

uint8_t host_thread_ring_phone_connection_state(void)
{
    return host_thread_ring_connection_state;
}

uint32_t host_thread_ring_phone_role(void)
{
    return host_thread_ring_phone_role_value;
}

uint8_t host_thread_ring_remove(void (*callback)(uint32_t))
{
    (void)callback;
    ++host_thread_ring_remove_count;
    return 1u;
}

void host_thread_ring_push(
    void (*callback)(uint32_t), uint32_t argument, uint32_t delay)
{
    uint32_t index = host_thread_ring_push_count;

    (void)argument;
    if (index < 16u) {
        host_thread_ring_push_callbacks[index] = (uintptr_t)callback;
        host_thread_ring_push_delays[index] = delay;
    }
    ++host_thread_ring_push_count;
}

uint32_t host_thread_ring_heartbeat(void)
{
    ++host_thread_ring_heartbeat_count;
    return 0u;
}

uint32_t host_thread_ring_touch_time(uint16_t ticks)
{
    ++host_thread_ring_touch_time_count;
    host_thread_ring_touch_time_value = ticks;
    return 0u;
}

uint32_t host_thread_ring_touch_enable(uint8_t enabled)
{
    ++host_thread_ring_touch_enable_count;
    host_thread_ring_touch_enable_value = enabled;
    return 0u;
}

uint32_t host_thread_ring_status(uint8_t bit7, uint8_t bit6)
{
    ++host_thread_ring_status_count;
    host_thread_ring_status_values[0] = bit7;
    host_thread_ring_status_values[1] = bit6;
    return 0u;
}

int32_t host_thread_ring_post_touch(uint8_t event)
{
    ++host_thread_ring_post_touch_count;
    host_thread_ring_post_touch_value = event;
    return 0;
}

int32_t host_thread_ring_glasses_status(void)
{
    ++host_thread_ring_glasses_status_count;
    return 0;
}

uint32_t host_thread_ring_pair_request(void)
{
    ++host_thread_ring_pair_count;
    return 0u;
}

void host_thread_ring_owner_callback(uint32_t argument)
{
    (void)argument;
    ++host_thread_ring_owner_callback_count;
}

void host_thread_ring_touch_error_callback(uint32_t argument)
{
    (void)argument;
    ++host_thread_ring_touch_error_count;
}

void host_thread_ring_post_disconnect(void)
{
    ++host_thread_ring_disconnect_count;
}

void host_thread_ring_parse(const uint8_t *packet, uint16_t length)
{
    uint16_t copy = length > sizeof(host_thread_ring_parse_data) ?
        (uint16_t)sizeof(host_thread_ring_parse_data) : length;

    ++host_thread_ring_parse_count;
    host_thread_ring_parse_length = length;
    if (copy != 0u) {
        memcpy(host_thread_ring_parse_data, packet, copy);
    }
}

void host_thread_ring_exit_wait(void)
{
    ++host_thread_ring_exit_wait_count;
}
