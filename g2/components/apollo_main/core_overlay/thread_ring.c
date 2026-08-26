/*
 * OpenCFW clean-room G2 Ring worker thread.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Recreated from authenticated linked-object behavior and ABI evidence.  No
 * vendor source text is included.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_THREAD_RING_SELECTOR
#define OPEN_CFW_THREAD_RING_SELECTOR 0
#endif

typedef void (*open_cfw_thread_ring_callback)(uint32_t argument);

#ifndef OPEN_CFW_THREAD_RING_THREAD_ID
#define OPEN_CFW_THREAD_RING_THREAD_ID \
    (*(void * volatile *)(uintptr_t)0x20004128u)
#endif
#ifndef OPEN_CFW_THREAD_RING_QUEUE_ID
#define OPEN_CFW_THREAD_RING_QUEUE_ID \
    (*(void * volatile *)(uintptr_t)0x2000412cu)
#endif
#ifndef OPEN_CFW_THREAD_RING_THREAD_ATTRIBUTES
#define OPEN_CFW_THREAD_RING_THREAD_ATTRIBUTES \
    ((const void *)(uintptr_t)0x0075b8a4u)
#endif

#ifndef OPEN_CFW_THREAD_RING_THREAD_NEW
void *open_cfw_cmsis_thread_new(
    void (*entry)(void *), void *argument, const void *attributes);
#define OPEN_CFW_THREAD_RING_THREAD_NEW(entry, argument, attributes) \
    open_cfw_cmsis_thread_new((entry), (argument), (attributes))
#endif
#ifndef OPEN_CFW_THREAD_RING_THREAD_TERMINATE
int32_t open_cfw_cmsis_thread_terminate(void *thread_id);
#define OPEN_CFW_THREAD_RING_THREAD_TERMINATE(thread_id) \
    open_cfw_cmsis_thread_terminate((thread_id))
#endif
#ifndef OPEN_CFW_THREAD_RING_FLAGS_SET
uint32_t open_cfw_cmsis_thread_flags_set(void *thread_id, uint32_t flags);
#define OPEN_CFW_THREAD_RING_FLAGS_SET(thread_id, flags) \
    open_cfw_cmsis_thread_flags_set((thread_id), (flags))
#endif
#ifndef OPEN_CFW_THREAD_RING_FLAGS_WAIT
uint32_t open_cfw_cmsis_thread_flags_wait(
    uint32_t flags, uint32_t options, uint32_t timeout);
#define OPEN_CFW_THREAD_RING_FLAGS_WAIT(flags, options, timeout) \
    open_cfw_cmsis_thread_flags_wait((flags), (options), (timeout))
#endif
#ifndef OPEN_CFW_THREAD_RING_DELAY
int32_t open_cfw_cmsis_delay(uint32_t ticks);
#define OPEN_CFW_THREAD_RING_DELAY(ticks) open_cfw_cmsis_delay((ticks))
#endif
#ifndef OPEN_CFW_THREAD_RING_QUEUE_NEW
void *open_cfw_cmsis_message_queue_new(
    uint32_t count, uint32_t size, const void *attributes);
#define OPEN_CFW_THREAD_RING_QUEUE_NEW(count, size, attributes) \
    open_cfw_cmsis_message_queue_new((count), (size), (attributes))
#endif
#ifndef OPEN_CFW_THREAD_RING_QUEUE_PUT
int32_t open_cfw_cmsis_message_queue_put(
    void *queue_id, const void *message, uint8_t priority, uint32_t timeout);
#define OPEN_CFW_THREAD_RING_QUEUE_PUT(queue_id, message, priority, timeout) \
    open_cfw_cmsis_message_queue_put( \
        (queue_id), (message), (priority), (timeout))
#endif
#ifndef OPEN_CFW_THREAD_RING_QUEUE_GET
int32_t open_cfw_cmsis_message_queue_get(
    void *queue_id, void *message, uint8_t *priority, uint32_t timeout);
#define OPEN_CFW_THREAD_RING_QUEUE_GET(queue_id, message, priority, timeout) \
    open_cfw_cmsis_message_queue_get( \
        (queue_id), (message), (priority), (timeout))
#endif
#ifndef OPEN_CFW_THREAD_RING_QUEUE_DELETE
int32_t open_cfw_cmsis_message_queue_delete(void *queue_id);
#define OPEN_CFW_THREAD_RING_QUEUE_DELETE(queue_id) \
    open_cfw_cmsis_message_queue_delete((queue_id))
#endif
#ifndef OPEN_CFW_THREAD_RING_ASSERT_FAIL
void open_cfw_freertos_assert_fail(void);
#define OPEN_CFW_THREAD_RING_ASSERT_FAIL() open_cfw_freertos_assert_fail()
#endif
#ifndef OPEN_CFW_THREAD_RING_ALLOC
void *open_cfw_runtime_alloc(size_t size);
#define OPEN_CFW_THREAD_RING_ALLOC(size) open_cfw_runtime_alloc((size))
#endif
#ifndef OPEN_CFW_THREAD_RING_FREE
void open_cfw_runtime_free(void *allocation);
#define OPEN_CFW_THREAD_RING_FREE(allocation) \
    open_cfw_runtime_free((allocation))
#endif

#ifndef OPEN_CFW_THREAD_RING_STATE_ACTIVE
void open_cfw_retained_thread_state_active(uint32_t thread_index);
#define OPEN_CFW_THREAD_RING_STATE_ACTIVE(index) \
    open_cfw_retained_thread_state_active((index))
#endif
#ifndef OPEN_CFW_THREAD_RING_STATE_READY
void open_cfw_retained_thread_state_ready(uint32_t thread_index);
#define OPEN_CFW_THREAD_RING_STATE_READY(index) \
    open_cfw_retained_thread_state_ready((index))
#endif
#ifndef OPEN_CFW_THREAD_RING_STATE_EXIT
void open_cfw_retained_thread_state_exit(uint32_t thread_index);
#define OPEN_CFW_THREAD_RING_STATE_EXIT(index) \
    open_cfw_retained_thread_state_exit((index))
#endif
#ifndef OPEN_CFW_THREAD_RING_PHONE_CONNECTION_STATE
uint8_t open_cfw_retained_phone_connection_state(void);
#define OPEN_CFW_THREAD_RING_PHONE_CONNECTION_STATE() \
    open_cfw_retained_phone_connection_state()
#endif
#ifndef OPEN_CFW_THREAD_RING_PHONE_ROLE
uint32_t open_cfw_retained_phone_role(void);
#define OPEN_CFW_THREAD_RING_PHONE_ROLE() open_cfw_retained_phone_role()
#endif

#ifndef OPEN_CFW_THREAD_RING_REMOVE
uint8_t open_cfw_event_loop_remove_delayed(
    open_cfw_thread_ring_callback callback);
#define OPEN_CFW_THREAD_RING_REMOVE(callback) \
    open_cfw_event_loop_remove_delayed((callback))
#endif
#ifndef OPEN_CFW_THREAD_RING_PUSH
void open_cfw_event_loop_push_delayed(
    open_cfw_thread_ring_callback callback, uint32_t argument, uint32_t delay);
#define OPEN_CFW_THREAD_RING_PUSH(callback, argument, delay) \
    open_cfw_event_loop_push_delayed((callback), (argument), (delay))
#endif

uint32_t open_cfw_ring_service_heartbeat_process(void);
uint32_t open_cfw_ring_service_touch_report_time_process(uint16_t ticks);
uint32_t open_cfw_ring_service_send_touch_enable(uint8_t enabled);
uint32_t open_cfw_ring_service_send_status_bits(uint8_t bit7, uint8_t bit6);
int32_t open_cfw_ring_service_post_touch_event(uint8_t event);
int32_t open_cfw_ring_service_send_glasses_status_event(void);
uint32_t open_cfw_ring_service_send_pair_request(void);
void open_cfw_ring_service_owner_connect_callback(uint32_t argument);
void open_cfw_ring_service_touch_error_callback(uint32_t argument);
void open_cfw_ring_service_post_disconnect_event(void);
void open_cfw_ring_service_cmd_package_parse(
    const uint8_t *packet, uint16_t length);

#ifndef OPEN_CFW_THREAD_RING_ADVERTISING_CALLBACK
#define OPEN_CFW_THREAD_RING_ADVERTISING_CALLBACK \
    ((open_cfw_thread_ring_callback)(uintptr_t)0x0046ee71u)
#endif
#ifndef OPEN_CFW_THREAD_RING_DOMINANT_CALLBACK
#define OPEN_CFW_THREAD_RING_DOMINANT_CALLBACK \
    ((open_cfw_thread_ring_callback)(uintptr_t)0x004a285du)
#endif
#ifndef OPEN_CFW_THREAD_RING_EXIT_WAIT_FOREVER
#define OPEN_CFW_THREAD_RING_EXIT_WAIT_FOREVER() \
    do { \
        for (;;) { \
            (void)OPEN_CFW_THREAD_RING_DELAY(UINT32_MAX); \
        } \
    } while (0)
#endif

enum {
    OPEN_CFW_THREAD_RING_INDEX = 6u,
    OPEN_CFW_THREAD_RING_QUEUE_DEPTH = 3u,
    OPEN_CFW_THREAD_RING_EVENT_TOUCH_ENABLE = 0x000004u,
    OPEN_CFW_THREAD_RING_EVENT_DISCOVERY = 0x000008u,
    OPEN_CFW_THREAD_RING_EVENT_DISCONNECT = 0x000010u,
    OPEN_CFW_THREAD_RING_EVENT_HEARTBEAT = 0x000020u,
    OPEN_CFW_THREAD_RING_EVENT_PAIR = 0x000040u,
    OPEN_CFW_THREAD_RING_EVENT_ADVERTISING = 0x000100u,
    OPEN_CFW_THREAD_RING_EVENT_STATUS = 0x000800u,
    OPEN_CFW_THREAD_RING_EVENT_MESSAGE = 0x400000u,
    OPEN_CFW_THREAD_RING_EVENT_EXIT = 0x800000u,
    OPEN_CFW_THREAD_RING_EVENT_MASK = 0x00ffffffu,
    OPEN_CFW_THREAD_RING_RECORD_PROTOCOL = 2u,
    OPEN_CFW_THREAD_RING_RECORD_TOUCH_ENABLE = 0x80u,
    OPEN_CFW_THREAD_RING_RECORD_STATUS = 0x400u,
    OPEN_CFW_THREAD_RING_RECORD_TOUCH_TIME = 0x1000u
};

struct open_cfw_thread_ring_record {
    uint32_t message_id;
    uint32_t length;
    uint8_t data[];
};

_Static_assert(offsetof(struct open_cfw_thread_ring_record, data) == 8u,
               "G2 Ring record header size changed");

void open_cfw_thread_ring_entry(void *argument);
void open_cfw_thread_ring_init_hook(void);
void open_cfw_thread_ring_queue_init(void);
void open_cfw_thread_ring_resource_hook(void);
void open_cfw_thread_ring_state_enter(void);
void open_cfw_thread_ring_state_ready(void);
void open_cfw_thread_ring_create(void);
void open_cfw_thread_ring_terminate(void);
void open_cfw_thread_ring_message_handler(void);
void open_cfw_thread_ring_enable_touch(uint32_t argument);
void open_cfw_thread_ring_disable_touch(uint32_t argument);
void open_cfw_thread_ring_enable_pair(uint32_t argument);
void open_cfw_thread_ring_event_handler(uint32_t events);
void open_cfw_thread_ring_exit(void);
uint32_t open_cfw_thread_ring_send_event(uint32_t event);
int32_t open_cfw_thread_ring_send_message(const void *data, uint16_t length);
int32_t open_cfw_thread_ring_record_send(
    uint32_t message_id, const void *data, uint16_t length);

static __attribute__((unused)) void open_cfw_thread_ring_schedule(
    open_cfw_thread_ring_callback callback, uint32_t delay)
{
    (void)OPEN_CFW_THREAD_RING_REMOVE(callback);
    OPEN_CFW_THREAD_RING_PUSH(callback, 0u, delay);
}

static __attribute__((unused)) uint16_t open_cfw_thread_ring_read_u16(
    const uint8_t *data)
{
    return (uint16_t)data[0] | ((uint16_t)data[1] << 8);
}

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 1
__attribute__((noinline)) void open_cfw_thread_ring_entry(void *argument)
{
    uint32_t events;

    (void)argument;
    open_cfw_thread_ring_state_enter();
    open_cfw_thread_ring_queue_init();
    open_cfw_thread_ring_init_hook();
    open_cfw_thread_ring_resource_hook();
    open_cfw_thread_ring_state_ready();
    for (;;) {
        events = OPEN_CFW_THREAD_RING_FLAGS_WAIT(
            OPEN_CFW_THREAD_RING_EVENT_MASK, 0u, UINT32_MAX);
        if (events != 0u && (events & 0x80000000u) == 0u) {
            open_cfw_thread_ring_event_handler(events);
        }
    }
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 2
__attribute__((noinline)) void open_cfw_thread_ring_init_hook(void)
{
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 3
__attribute__((noinline)) void open_cfw_thread_ring_queue_init(void)
{
    OPEN_CFW_THREAD_RING_QUEUE_ID = OPEN_CFW_THREAD_RING_QUEUE_NEW(
        OPEN_CFW_THREAD_RING_QUEUE_DEPTH, sizeof(uint32_t), NULL);
    if (OPEN_CFW_THREAD_RING_QUEUE_ID == NULL) {
        OPEN_CFW_THREAD_RING_ASSERT_FAIL();
    }
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 4
__attribute__((noinline)) void open_cfw_thread_ring_resource_hook(void)
{
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 5
__attribute__((noinline)) void open_cfw_thread_ring_state_enter(void)
{
    OPEN_CFW_THREAD_RING_STATE_ACTIVE(OPEN_CFW_THREAD_RING_INDEX);
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 6
__attribute__((noinline)) void open_cfw_thread_ring_state_ready(void)
{
    OPEN_CFW_THREAD_RING_STATE_READY(OPEN_CFW_THREAD_RING_INDEX);
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 7
__attribute__((noinline)) void open_cfw_thread_ring_create(void)
{
    OPEN_CFW_THREAD_RING_THREAD_ID = OPEN_CFW_THREAD_RING_THREAD_NEW(
        open_cfw_thread_ring_entry, NULL,
        OPEN_CFW_THREAD_RING_THREAD_ATTRIBUTES);
    if (OPEN_CFW_THREAD_RING_THREAD_ID == NULL) {
        OPEN_CFW_THREAD_RING_ASSERT_FAIL();
    }
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 8
__attribute__((noinline)) void open_cfw_thread_ring_terminate(void)
{
    void *thread_id = OPEN_CFW_THREAD_RING_THREAD_ID;

    if (thread_id != NULL) {
        (void)OPEN_CFW_THREAD_RING_THREAD_TERMINATE(thread_id);
        OPEN_CFW_THREAD_RING_THREAD_ID = NULL;
    }
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 9
__attribute__((noinline)) void open_cfw_thread_ring_message_handler(void)
{
    struct open_cfw_thread_ring_record *record;

    for (;;) {
        record = NULL;
        if (OPEN_CFW_THREAD_RING_QUEUE_GET(
                OPEN_CFW_THREAD_RING_QUEUE_ID, &record, NULL, 0u) != 0 ||
            record == NULL) {
            return;
        }
        switch (record->message_id) {
        case OPEN_CFW_THREAD_RING_RECORD_PROTOCOL:
            open_cfw_ring_service_cmd_package_parse(
                record->data, (uint16_t)record->length);
            break;
        case OPEN_CFW_THREAD_RING_RECORD_TOUCH_ENABLE:
            if (record->length >= 1u) {
                (void)open_cfw_ring_service_send_touch_enable(record->data[0]);
            }
            break;
        case OPEN_CFW_THREAD_RING_RECORD_STATUS:
            if (record->length >= 2u) {
                (void)open_cfw_ring_service_send_status_bits(
                    record->data[0], record->data[1]);
            }
            break;
        case OPEN_CFW_THREAD_RING_RECORD_TOUCH_TIME:
            if (record->length >= 2u) {
                (void)open_cfw_ring_service_touch_report_time_process(
                    open_cfw_thread_ring_read_u16(record->data));
            }
            break;
        default:
            break;
        }
        OPEN_CFW_THREAD_RING_FREE(record);
    }
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 10
__attribute__((noinline)) void
open_cfw_thread_ring_enable_touch(uint32_t argument)
{
    (void)argument;
    (void)open_cfw_ring_service_post_touch_event(1u);
    if (OPEN_CFW_THREAD_RING_PHONE_CONNECTION_STATE() == 0u) {
        open_cfw_thread_ring_schedule(
            OPEN_CFW_THREAD_RING_ADVERTISING_CALLBACK, 500u);
    }
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 11
__attribute__((noinline)) void
open_cfw_thread_ring_disable_touch(uint32_t argument)
{
    (void)argument;
    (void)open_cfw_ring_service_post_touch_event(0u);
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 12
__attribute__((noinline)) void
open_cfw_thread_ring_enable_pair(uint32_t argument)
{
    (void)argument;
    open_cfw_ring_service_post_disconnect_event();
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 13
__attribute__((noinline)) void
open_cfw_thread_ring_event_handler(uint32_t events)
{
    uint16_t touch_report_ticks;

    if ((events & OPEN_CFW_THREAD_RING_EVENT_MESSAGE) != 0u) {
        open_cfw_thread_ring_message_handler();
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_TOUCH_ENABLE) != 0u) {
        open_cfw_thread_ring_schedule(open_cfw_thread_ring_enable_pair, 200u);
        open_cfw_thread_ring_schedule(open_cfw_thread_ring_enable_touch, 500u);
        open_cfw_thread_ring_schedule(
            OPEN_CFW_THREAD_RING_DOMINANT_CALLBACK, 3000u);
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_DISCOVERY) != 0u) {
        /* The stock path records this state but has no functional side effect. */
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_DISCONNECT) != 0u) {
        open_cfw_thread_ring_schedule(open_cfw_thread_ring_enable_touch, 200u);
        open_cfw_thread_ring_schedule(
            OPEN_CFW_THREAD_RING_DOMINANT_CALLBACK, 3000u);
        (void)open_cfw_ring_service_send_glasses_status_event();
        touch_report_ticks = OPEN_CFW_THREAD_RING_PHONE_ROLE() == 0u ?
            1000u : 500u;
        (void)open_cfw_ring_service_touch_report_time_process(
            touch_report_ticks);
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_HEARTBEAT) != 0u) {
        (void)open_cfw_ring_service_heartbeat_process();
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_PAIR) != 0u) {
        (void)open_cfw_ring_service_send_pair_request();
        open_cfw_thread_ring_schedule(
            open_cfw_ring_service_owner_connect_callback, 500u);
        open_cfw_thread_ring_schedule(
            open_cfw_ring_service_touch_error_callback, 700u);
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_STATUS) != 0u) {
        (void)open_cfw_ring_service_send_glasses_status_event();
        touch_report_ticks = OPEN_CFW_THREAD_RING_PHONE_ROLE() == 0u ?
            1000u : 500u;
        (void)open_cfw_ring_service_touch_report_time_process(
            touch_report_ticks);
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_ADVERTISING) != 0u) {
        /* The stock path records this state but has no functional side effect. */
    }
    if ((events & OPEN_CFW_THREAD_RING_EVENT_EXIT) != 0u) {
        open_cfw_thread_ring_exit();
    }
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 14
__attribute__((noinline)) void open_cfw_thread_ring_exit(void)
{
    OPEN_CFW_THREAD_RING_STATE_EXIT(OPEN_CFW_THREAD_RING_INDEX);
    if (OPEN_CFW_THREAD_RING_QUEUE_ID != NULL) {
        (void)OPEN_CFW_THREAD_RING_QUEUE_DELETE(OPEN_CFW_THREAD_RING_QUEUE_ID);
        OPEN_CFW_THREAD_RING_QUEUE_ID = NULL;
    }
    OPEN_CFW_THREAD_RING_EXIT_WAIT_FOREVER();
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 15
__attribute__((noinline)) uint32_t
open_cfw_thread_ring_send_event(uint32_t event)
{
    return OPEN_CFW_THREAD_RING_FLAGS_SET(
        OPEN_CFW_THREAD_RING_THREAD_ID, event);
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 16
__attribute__((noinline)) int32_t open_cfw_thread_ring_send_message(
    const void *data, uint16_t length)
{
    return open_cfw_thread_ring_record_send(
        OPEN_CFW_THREAD_RING_RECORD_PROTOCOL, data, length);
}
#endif

#if OPEN_CFW_THREAD_RING_SELECTOR == 0 || OPEN_CFW_THREAD_RING_SELECTOR == 17
__attribute__((noinline)) int32_t open_cfw_thread_ring_record_send(
    uint32_t message_id, const void *data, uint16_t length)
{
    struct open_cfw_thread_ring_record *record;
    const uint8_t *source;
    uint8_t *destination;
    uint16_t remaining;

    if ((data == NULL && length != 0u) ||
        OPEN_CFW_THREAD_RING_QUEUE_ID == NULL) {
        return -1;
    }
    record = (struct open_cfw_thread_ring_record *)
        OPEN_CFW_THREAD_RING_ALLOC(sizeof(*record) + length);
    if (record == NULL) {
        return -1;
    }
    record->message_id = message_id;
    record->length = length;
    source = (const uint8_t *)data;
    destination = record->data;
    remaining = length;
    while (remaining != 0u) {
        *destination++ = *source++;
        --remaining;
    }
    if (OPEN_CFW_THREAD_RING_QUEUE_PUT(
            OPEN_CFW_THREAD_RING_QUEUE_ID, &record, 0u, 0u) != 0) {
        OPEN_CFW_THREAD_RING_FREE(record);
        return -1;
    }
    (void)open_cfw_thread_ring_send_event(
        OPEN_CFW_THREAD_RING_EVENT_MESSAGE);
    return 0;
}
#endif
