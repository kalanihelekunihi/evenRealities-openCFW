/* SPDX-License-Identifier: MIT */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/freertos/runtime_freertos_queue_generic_reset.h"

enum {
    OPEN_CFW_QUEUE_RESET_HOST_NO_WAITER = 0xFFFFFFFFU,
    OPEN_CFW_QUEUE_RESET_HOST_ASSERTED = 0x80000000U,
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_ASSERT = 1U,
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_ENTER = 2U,
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_REMOVE = 3U,
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_YIELD = 4U,
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_LIST_INIT = 5U,
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_EXIT = 6U,
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_CAPACITY = 16U
};

static struct open_cfw_freertos_queue_reset_control
    open_cfw_queue_reset_host_queue;
static open_cfw_freertos_queue_reset_int8
    open_cfw_queue_reset_host_storage[256];
static uint32_t open_cfw_queue_reset_host_current_priority;
static uint32_t open_cfw_queue_reset_host_waiter_priority;
static uint32_t open_cfw_queue_reset_host_events[
    OPEN_CFW_QUEUE_RESET_HOST_EVENT_CAPACITY
];
static uint32_t open_cfw_queue_reset_host_event_count;
static uint32_t open_cfw_queue_reset_host_remove_calls;
static uint32_t open_cfw_queue_reset_host_yield_calls;
static uint32_t open_cfw_queue_reset_host_enter_calls;
static uint32_t open_cfw_queue_reset_host_exit_calls;
static uint32_t open_cfw_queue_reset_host_list_init_calls;
static uint32_t open_cfw_queue_reset_host_assert_calls;
static int open_cfw_queue_reset_host_execute_active;
static jmp_buf open_cfw_queue_reset_host_assert_jump;

static void open_cfw_queue_reset_host_record(uint32_t event)
{
    if (
        open_cfw_queue_reset_host_event_count <
        OPEN_CFW_QUEUE_RESET_HOST_EVENT_CAPACITY
    ) {
        open_cfw_queue_reset_host_events[
            open_cfw_queue_reset_host_event_count
        ] = event;
    }
    ++open_cfw_queue_reset_host_event_count;
}

static struct open_cfw_freertos_queue_reset_list_item *
open_cfw_queue_reset_host_sentinel(
    struct open_cfw_freertos_queue_reset_list *list
)
{
    return (struct open_cfw_freertos_queue_reset_list_item *)(void *)&list->end;
}

static void open_cfw_queue_reset_host_list_init_body(
    struct open_cfw_freertos_queue_reset_list *list
)
{
    struct open_cfw_freertos_queue_reset_list_item *sentinel =
        open_cfw_queue_reset_host_sentinel(list);

    list->item_count = 0U;
    list->index = sentinel;
    list->end.item_value = 0xFFFFFFFFU;
    list->end.next = sentinel;
    list->end.previous = sentinel;
}

static uint32_t open_cfw_queue_reset_host_assert_mask(void)
{
    return 0x35U;
}

static void open_cfw_queue_reset_host_assert(int condition)
{
    if (!condition) {
        ++open_cfw_queue_reset_host_assert_calls;
        open_cfw_queue_reset_host_record(
            OPEN_CFW_QUEUE_RESET_HOST_EVENT_ASSERT
        );
        (void)open_cfw_queue_reset_host_assert_mask();
        if (open_cfw_queue_reset_host_execute_active != 0) {
            longjmp(open_cfw_queue_reset_host_assert_jump, 1);
        }
    }
}

static void open_cfw_queue_reset_host_enter(void)
{
    ++open_cfw_queue_reset_host_enter_calls;
    open_cfw_queue_reset_host_record(OPEN_CFW_QUEUE_RESET_HOST_EVENT_ENTER);
}

static void open_cfw_queue_reset_host_exit(void)
{
    ++open_cfw_queue_reset_host_exit_calls;
    open_cfw_queue_reset_host_record(OPEN_CFW_QUEUE_RESET_HOST_EVENT_EXIT);
}

static void open_cfw_queue_reset_host_list_initialise(
    struct open_cfw_freertos_queue_reset_list *list
)
{
    ++open_cfw_queue_reset_host_list_init_calls;
    open_cfw_queue_reset_host_record(
        OPEN_CFW_QUEUE_RESET_HOST_EVENT_LIST_INIT
    );
    open_cfw_queue_reset_host_list_init_body(list);
}

static open_cfw_freertos_queue_reset_base_type
open_cfw_queue_reset_host_remove(
    const struct open_cfw_freertos_queue_reset_list *const_list
)
{
    struct open_cfw_freertos_queue_reset_list *list =
        (struct open_cfw_freertos_queue_reset_list *)(void *)const_list;

    ++open_cfw_queue_reset_host_remove_calls;
    open_cfw_queue_reset_host_record(OPEN_CFW_QUEUE_RESET_HOST_EVENT_REMOVE);
    open_cfw_queue_reset_host_list_init_body(list);
    return (
        open_cfw_queue_reset_host_waiter_priority !=
            OPEN_CFW_QUEUE_RESET_HOST_NO_WAITER &&
        open_cfw_queue_reset_host_waiter_priority >
            open_cfw_queue_reset_host_current_priority
    ) ? 1 : 0;
}

static void open_cfw_queue_reset_host_yield(void)
{
    ++open_cfw_queue_reset_host_yield_calls;
    open_cfw_queue_reset_host_record(OPEN_CFW_QUEUE_RESET_HOST_EVENT_YIELD);
}

#undef OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT_MASK
#undef OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT
#undef OPEN_CFW_FREERTOS_QUEUE_RESET_ENTER_CRITICAL
#undef OPEN_CFW_FREERTOS_QUEUE_RESET_EXIT_CRITICAL
#undef OPEN_CFW_FREERTOS_QUEUE_RESET_REMOVE_FROM_EVENT_LIST
#undef OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE
#undef OPEN_CFW_FREERTOS_QUEUE_RESET_YIELD

#define OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT_MASK() \
    open_cfw_queue_reset_host_assert_mask()
#define OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT(condition) \
    open_cfw_queue_reset_host_assert((condition))
#define OPEN_CFW_FREERTOS_QUEUE_RESET_ENTER_CRITICAL() \
    open_cfw_queue_reset_host_enter()
#define OPEN_CFW_FREERTOS_QUEUE_RESET_EXIT_CRITICAL() \
    open_cfw_queue_reset_host_exit()
#define OPEN_CFW_FREERTOS_QUEUE_RESET_REMOVE_FROM_EVENT_LIST(list) \
    open_cfw_queue_reset_host_remove((list))
#define OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE(list) \
    open_cfw_queue_reset_host_list_initialise((list))
#define OPEN_CFW_FREERTOS_QUEUE_RESET_YIELD() \
    open_cfw_queue_reset_host_yield()

#include "../../components/shared/freertos/runtime_freertos_queue_generic_reset.c"

void open_cfw_queue_reset_host_reset(
    uint32_t current_priority,
    uint32_t waiter_priority,
    uint32_t length,
    uint32_t item_size,
    uint32_t messages_waiting,
    uint32_t seed_receive
)
{
    memset(&open_cfw_queue_reset_host_queue, 0xA7,
           sizeof(open_cfw_queue_reset_host_queue));
    memset(open_cfw_queue_reset_host_storage, 0x5A,
           sizeof(open_cfw_queue_reset_host_storage));
    memset(open_cfw_queue_reset_host_events, 0,
           sizeof(open_cfw_queue_reset_host_events));
    open_cfw_queue_reset_host_list_init_body(
        &open_cfw_queue_reset_host_queue.tasks_waiting_to_send
    );
    open_cfw_queue_reset_host_list_init_body(
        &open_cfw_queue_reset_host_queue.tasks_waiting_to_receive
    );
    if (waiter_priority != OPEN_CFW_QUEUE_RESET_HOST_NO_WAITER) {
        open_cfw_queue_reset_host_queue.tasks_waiting_to_send.item_count = 1U;
    }
    if (seed_receive != 0U) {
        open_cfw_queue_reset_host_queue.tasks_waiting_to_receive.item_count = 1U;
    }
    open_cfw_queue_reset_host_queue.head = open_cfw_queue_reset_host_storage;
    open_cfw_queue_reset_host_queue.write_to =
        open_cfw_queue_reset_host_storage + 7;
    open_cfw_queue_reset_host_queue.value.queue.tail =
        open_cfw_queue_reset_host_storage + 11;
    open_cfw_queue_reset_host_queue.value.queue.read_from =
        open_cfw_queue_reset_host_storage + 13;
    open_cfw_queue_reset_host_queue.length = length;
    open_cfw_queue_reset_host_queue.item_size = item_size;
    open_cfw_queue_reset_host_queue.messages_waiting = messages_waiting;
    open_cfw_queue_reset_host_queue.receive_lock = 19;
    open_cfw_queue_reset_host_queue.transmit_lock = 23;
    open_cfw_queue_reset_host_current_priority = current_priority;
    open_cfw_queue_reset_host_waiter_priority = waiter_priority;
    open_cfw_queue_reset_host_event_count = 0U;
    open_cfw_queue_reset_host_remove_calls = 0U;
    open_cfw_queue_reset_host_yield_calls = 0U;
    open_cfw_queue_reset_host_enter_calls = 0U;
    open_cfw_queue_reset_host_exit_calls = 0U;
    open_cfw_queue_reset_host_list_init_calls = 0U;
    open_cfw_queue_reset_host_assert_calls = 0U;
    open_cfw_queue_reset_host_execute_active = 0;
}

static int32_t open_cfw_queue_reset_host_run(
    struct open_cfw_freertos_queue_reset_control *queue,
    int32_t new_queue
)
{
    int32_t result;

    open_cfw_queue_reset_host_execute_active = 1;
    if (setjmp(open_cfw_queue_reset_host_assert_jump) != 0) {
        open_cfw_queue_reset_host_execute_active = 0;
        return (int32_t)OPEN_CFW_QUEUE_RESET_HOST_ASSERTED;
    }
    result = open_cfw_freertos_queue_generic_reset(
        queue,
        new_queue
    );
    open_cfw_queue_reset_host_execute_active = 0;
    return result;
}

int32_t open_cfw_queue_reset_host_execute(int32_t new_queue)
{
    return open_cfw_queue_reset_host_run(
        &open_cfw_queue_reset_host_queue,
        new_queue
    );
}

int32_t open_cfw_queue_reset_host_execute_null(void)
{
    return open_cfw_queue_reset_host_run(
        (struct open_cfw_freertos_queue_reset_control *)0,
        0
    );
}

static uint32_t open_cfw_queue_reset_host_offset(
    const open_cfw_freertos_queue_reset_int8 *pointer
)
{
    return (uint32_t)(pointer - open_cfw_queue_reset_host_storage);
}

uint32_t open_cfw_queue_reset_host_get_tail(void)
{
    return open_cfw_queue_reset_host_offset(
        open_cfw_queue_reset_host_queue.value.queue.tail
    );
}

uint32_t open_cfw_queue_reset_host_get_write(void)
{
    return open_cfw_queue_reset_host_offset(
        open_cfw_queue_reset_host_queue.write_to
    );
}

uint32_t open_cfw_queue_reset_host_get_read(void)
{
    return open_cfw_queue_reset_host_offset(
        open_cfw_queue_reset_host_queue.value.queue.read_from
    );
}

uint32_t open_cfw_queue_reset_host_get_messages(void)
{
    return open_cfw_queue_reset_host_queue.messages_waiting;
}

int32_t open_cfw_queue_reset_host_get_receive_lock(void)
{
    return open_cfw_queue_reset_host_queue.receive_lock;
}

int32_t open_cfw_queue_reset_host_get_transmit_lock(void)
{
    return open_cfw_queue_reset_host_queue.transmit_lock;
}

uint32_t open_cfw_queue_reset_host_get_send_count(void)
{
    return open_cfw_queue_reset_host_queue.tasks_waiting_to_send.item_count;
}

uint32_t open_cfw_queue_reset_host_get_receive_count(void)
{
    return open_cfw_queue_reset_host_queue.tasks_waiting_to_receive.item_count;
}

#define OPEN_CFW_QUEUE_RESET_HOST_GETTER(name) \
    uint32_t open_cfw_queue_reset_host_get_##name(void) \
    { \
        return open_cfw_queue_reset_host_##name; \
    }

OPEN_CFW_QUEUE_RESET_HOST_GETTER(event_count)
OPEN_CFW_QUEUE_RESET_HOST_GETTER(remove_calls)
OPEN_CFW_QUEUE_RESET_HOST_GETTER(yield_calls)
OPEN_CFW_QUEUE_RESET_HOST_GETTER(enter_calls)
OPEN_CFW_QUEUE_RESET_HOST_GETTER(exit_calls)
OPEN_CFW_QUEUE_RESET_HOST_GETTER(list_init_calls)
OPEN_CFW_QUEUE_RESET_HOST_GETTER(assert_calls)

uint32_t open_cfw_queue_reset_host_get_event(uint32_t index)
{
    return index < OPEN_CFW_QUEUE_RESET_HOST_EVENT_CAPACITY ?
        open_cfw_queue_reset_host_events[index] : 0xFFFFFFFFU;
}
