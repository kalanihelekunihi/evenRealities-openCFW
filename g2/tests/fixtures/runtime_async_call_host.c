/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for source-owned lv_async_call.
 */

static unsigned int open_cfw_test_runtime_async_allocate(unsigned int);
static void open_cfw_test_runtime_async_free(unsigned int);
static unsigned int open_cfw_test_runtime_async_timer_create(
    unsigned int, unsigned int, unsigned int
);
static void open_cfw_test_runtime_async_timer_set_repeat(
    unsigned int, int
);
static void open_cfw_test_runtime_async_timer_delete(unsigned int);
static unsigned int open_cfw_test_runtime_async_timer_get_next(
    unsigned int
);
static void *open_cfw_test_runtime_async_info_from_pointer(unsigned int);
struct open_cfw_runtime_async_timer_view;
static struct open_cfw_runtime_async_timer_view *
open_cfw_test_runtime_async_timer_from_pointer(unsigned int);
static unsigned int open_cfw_test_runtime_async_timer_user_data(
    unsigned int
);
static void open_cfw_test_runtime_async_invoke(
    unsigned int, unsigned int
);

#define OPEN_CFW_RUNTIME_ASYNC_ALLOCATE(size) \
    open_cfw_test_runtime_async_allocate((size))
#define OPEN_CFW_RUNTIME_ASYNC_FREE(pointer) \
    open_cfw_test_runtime_async_free((pointer))
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_CREATE(callback, period, user_data) \
    open_cfw_test_runtime_async_timer_create( \
        (callback), (period), (user_data) \
    )
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_SET_REPEAT(timer, count) \
    open_cfw_test_runtime_async_timer_set_repeat((timer), (count))
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_DELETE(timer) \
    open_cfw_test_runtime_async_timer_delete((timer))
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_GET_NEXT(timer) \
    open_cfw_test_runtime_async_timer_get_next((timer))
#define OPEN_CFW_RUNTIME_ASYNC_INFO_FROM_POINTER(pointer) \
    ((struct open_cfw_runtime_async_info *) \
        open_cfw_test_runtime_async_info_from_pointer((pointer)))
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_FROM_POINTER(pointer) \
    open_cfw_test_runtime_async_timer_from_pointer((pointer))
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_USER_DATA(timer) \
    open_cfw_test_runtime_async_timer_user_data((timer))
#define OPEN_CFW_RUNTIME_ASYNC_INVOKE(callback, user_data) \
    open_cfw_test_runtime_async_invoke((callback), (user_data))
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_CALLBACK 0x004840ADU

#include "../../components/apollo_main/core_overlay/runtime_async_call.c"

enum {
    OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_USER_DATA = 1U,
    OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_DELETE = 2U,
    OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_FREE = 3U,
    OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_INVOKE = 4U,
    OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY = 6U,
    OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_TIMER_BASE = 0x6000U,
    OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_ALLOCATION_BASE = 0x7000U,
    OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_STRIDE = 0x20U
};

struct open_cfw_runtime_async_info open_cfw_test_runtime_async_info;
unsigned int open_cfw_test_runtime_async_allocation_result;
unsigned int open_cfw_test_runtime_async_timer_result;
unsigned int open_cfw_test_runtime_async_allocate_calls;
unsigned int open_cfw_test_runtime_async_allocate_size;
unsigned int open_cfw_test_runtime_async_free_calls;
unsigned int open_cfw_test_runtime_async_freed;
unsigned int open_cfw_test_runtime_async_create_calls;
unsigned int open_cfw_test_runtime_async_create_callback;
unsigned int open_cfw_test_runtime_async_create_period;
unsigned int open_cfw_test_runtime_async_create_user_data;
unsigned int open_cfw_test_runtime_async_repeat_calls;
unsigned int open_cfw_test_runtime_async_repeat_timer;
int open_cfw_test_runtime_async_repeat_count;
unsigned int open_cfw_test_runtime_async_timer_user_data_result;
unsigned int open_cfw_test_runtime_async_timer_user_data_calls;
unsigned int open_cfw_test_runtime_async_timer_user_data_timer;
unsigned int open_cfw_test_runtime_async_delete_calls;
unsigned int open_cfw_test_runtime_async_deleted_timer;
unsigned int open_cfw_test_runtime_async_invoke_calls;
unsigned int open_cfw_test_runtime_async_invoked_callback;
unsigned int open_cfw_test_runtime_async_invoked_user_data;
unsigned int open_cfw_test_runtime_async_invoke_delete_calls_seen;
unsigned int open_cfw_test_runtime_async_invoke_free_calls_seen;
unsigned int open_cfw_test_runtime_async_mutate_info_on_invoke;
unsigned int open_cfw_test_runtime_async_event_count;
unsigned int open_cfw_test_runtime_async_events[8];
struct open_cfw_runtime_async_timer_view
    open_cfw_test_runtime_async_cancel_timer[
        OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY
    ];
struct open_cfw_runtime_async_info
    open_cfw_test_runtime_async_cancel_info[
        OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY
    ];
unsigned int open_cfw_test_runtime_async_cancel_active[
    OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY
];
unsigned int open_cfw_test_runtime_async_cancel_next[
    OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY
];
unsigned int open_cfw_test_runtime_async_cancel_count;
unsigned int open_cfw_test_runtime_async_cancel_head;
unsigned int open_cfw_test_runtime_async_cancel_get_next_calls;
unsigned int open_cfw_test_runtime_async_cancel_get_next_argument[8];
unsigned int open_cfw_test_runtime_async_cancel_invalid_traversals;
unsigned int open_cfw_test_runtime_async_cancel_deleted[6];
unsigned int open_cfw_test_runtime_async_cancel_freed[6];

static unsigned int open_cfw_test_runtime_async_cancel_timer_pointer(
    unsigned int index
)
{
    return OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_TIMER_BASE
        + index * OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_STRIDE;
}

static unsigned int open_cfw_test_runtime_async_cancel_allocation_pointer(
    unsigned int index
)
{
    return OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_ALLOCATION_BASE
        + index * OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_STRIDE;
}

static int open_cfw_test_runtime_async_cancel_index(
    unsigned int pointer,
    unsigned int base
)
{
    unsigned int offset;
    unsigned int index;

    if (pointer < base) {
        return -1;
    }
    offset = pointer - base;
    if (offset % OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_STRIDE != 0U) {
        return -1;
    }
    index = offset / OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_STRIDE;
    if (index >= open_cfw_test_runtime_async_cancel_count) {
        return -1;
    }
    return (int)index;
}

static void open_cfw_test_runtime_async_record_event(unsigned int event)
{
    if (open_cfw_test_runtime_async_event_count < 8U) {
        open_cfw_test_runtime_async_events[
            open_cfw_test_runtime_async_event_count
        ] = event;
    }
    open_cfw_test_runtime_async_event_count += 1U;
}

static unsigned int open_cfw_test_runtime_async_allocate(
    unsigned int size
)
{
    open_cfw_test_runtime_async_allocate_calls += 1U;
    open_cfw_test_runtime_async_allocate_size = size;
    return open_cfw_test_runtime_async_allocation_result;
}

static void open_cfw_test_runtime_async_free(unsigned int pointer)
{
    int index = open_cfw_test_runtime_async_cancel_index(
        pointer,
        OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_ALLOCATION_BASE
    );

    open_cfw_test_runtime_async_record_event(
        OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_FREE
    );
    if (open_cfw_test_runtime_async_free_calls < 6U) {
        open_cfw_test_runtime_async_cancel_freed[
            open_cfw_test_runtime_async_free_calls
        ] = pointer;
    }
    open_cfw_test_runtime_async_free_calls += 1U;
    open_cfw_test_runtime_async_freed = pointer;
    if (index >= 0) {
        open_cfw_test_runtime_async_cancel_info[index].callback =
            0xDEADBEEFU;
        open_cfw_test_runtime_async_cancel_info[index].user_data =
            0xCAFEBABEU;
    }
}

static unsigned int open_cfw_test_runtime_async_timer_create(
    unsigned int callback,
    unsigned int period,
    unsigned int user_data
)
{
    open_cfw_test_runtime_async_create_calls += 1U;
    open_cfw_test_runtime_async_create_callback = callback;
    open_cfw_test_runtime_async_create_period = period;
    open_cfw_test_runtime_async_create_user_data = user_data;
    return open_cfw_test_runtime_async_timer_result;
}

static void open_cfw_test_runtime_async_timer_set_repeat(
    unsigned int timer,
    int count
)
{
    open_cfw_test_runtime_async_repeat_calls += 1U;
    open_cfw_test_runtime_async_repeat_timer = timer;
    open_cfw_test_runtime_async_repeat_count = count;
}

static void open_cfw_test_runtime_async_timer_delete(unsigned int timer)
{
    int index = open_cfw_test_runtime_async_cancel_index(
        timer,
        OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_TIMER_BASE
    );
    unsigned int i;

    open_cfw_test_runtime_async_record_event(
        OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_DELETE
    );
    if (open_cfw_test_runtime_async_delete_calls < 6U) {
        open_cfw_test_runtime_async_cancel_deleted[
            open_cfw_test_runtime_async_delete_calls
        ] = timer;
    }
    open_cfw_test_runtime_async_delete_calls += 1U;
    open_cfw_test_runtime_async_deleted_timer = timer;
    if (
        index >= 0
        && open_cfw_test_runtime_async_cancel_active[index] != 0U
    ) {
        unsigned int next =
            open_cfw_test_runtime_async_cancel_next[index];

        if (open_cfw_test_runtime_async_cancel_head == timer) {
            open_cfw_test_runtime_async_cancel_head = next;
        }
        for (
            i = 0U;
            i < open_cfw_test_runtime_async_cancel_count;
            i += 1U
        ) {
            if (
                open_cfw_test_runtime_async_cancel_active[i] != 0U
                && open_cfw_test_runtime_async_cancel_next[i] == timer
            ) {
                open_cfw_test_runtime_async_cancel_next[i] = next;
            }
        }
        open_cfw_test_runtime_async_cancel_active[index] = 0U;
        open_cfw_test_runtime_async_cancel_next[index] = 0xDEAD0000U;
        open_cfw_test_runtime_async_cancel_timer[index].callback =
            0xDEAD0001U;
        open_cfw_test_runtime_async_cancel_timer[index].user_data =
            0xDEAD0002U;
    }
}

static unsigned int open_cfw_test_runtime_async_timer_get_next(
    unsigned int timer
)
{
    int index;
    unsigned int call =
        open_cfw_test_runtime_async_cancel_get_next_calls;

    if (call < 8U) {
        open_cfw_test_runtime_async_cancel_get_next_argument[call] =
            timer;
    }
    open_cfw_test_runtime_async_cancel_get_next_calls = call + 1U;
    if (timer == 0U) {
        return open_cfw_test_runtime_async_cancel_head;
    }
    index = open_cfw_test_runtime_async_cancel_index(
        timer,
        OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_TIMER_BASE
    );
    if (
        index < 0
        || open_cfw_test_runtime_async_cancel_active[index] == 0U
    ) {
        open_cfw_test_runtime_async_cancel_invalid_traversals += 1U;
        return 0U;
    }
    return open_cfw_test_runtime_async_cancel_next[index];
}

static void *open_cfw_test_runtime_async_info_from_pointer(
    unsigned int pointer
)
{
    int index = open_cfw_test_runtime_async_cancel_index(
        pointer,
        OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_ALLOCATION_BASE
    );

    if (index >= 0) {
        return &open_cfw_test_runtime_async_cancel_info[index];
    }
    return &open_cfw_test_runtime_async_info;
}

static struct open_cfw_runtime_async_timer_view *
open_cfw_test_runtime_async_timer_from_pointer(unsigned int pointer)
{
    int index = open_cfw_test_runtime_async_cancel_index(
        pointer,
        OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_TIMER_BASE
    );

    if (index < 0) {
        return (struct open_cfw_runtime_async_timer_view *)0;
    }
    return &open_cfw_test_runtime_async_cancel_timer[index];
}

static unsigned int open_cfw_test_runtime_async_timer_user_data(
    unsigned int timer
)
{
    open_cfw_test_runtime_async_record_event(
        OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_USER_DATA
    );
    open_cfw_test_runtime_async_timer_user_data_calls += 1U;
    open_cfw_test_runtime_async_timer_user_data_timer = timer;
    return open_cfw_test_runtime_async_timer_user_data_result;
}

static void open_cfw_test_runtime_async_invoke(
    unsigned int callback,
    unsigned int user_data
)
{
    open_cfw_test_runtime_async_record_event(
        OPEN_CFW_TEST_RUNTIME_ASYNC_EVENT_INVOKE
    );
    open_cfw_test_runtime_async_invoke_calls += 1U;
    open_cfw_test_runtime_async_invoke_delete_calls_seen =
        open_cfw_test_runtime_async_delete_calls;
    open_cfw_test_runtime_async_invoke_free_calls_seen =
        open_cfw_test_runtime_async_free_calls;
    if (open_cfw_test_runtime_async_mutate_info_on_invoke != 0U) {
        open_cfw_test_runtime_async_info.callback = 0xDEADBEEFU;
        open_cfw_test_runtime_async_info.user_data = 0xCAFEBABEU;
    }
    open_cfw_test_runtime_async_invoked_callback = callback;
    open_cfw_test_runtime_async_invoked_user_data = user_data;
}

void open_cfw_test_runtime_async_reset(
    unsigned int allocation,
    unsigned int timer
)
{
    open_cfw_test_runtime_async_info.callback = 0xCCCCCCCCU;
    open_cfw_test_runtime_async_info.user_data = 0xCCCCCCCCU;
    open_cfw_test_runtime_async_allocation_result = allocation;
    open_cfw_test_runtime_async_timer_result = timer;
    open_cfw_test_runtime_async_allocate_calls = 0U;
    open_cfw_test_runtime_async_allocate_size = 0U;
    open_cfw_test_runtime_async_free_calls = 0U;
    open_cfw_test_runtime_async_freed = 0U;
    open_cfw_test_runtime_async_create_calls = 0U;
    open_cfw_test_runtime_async_create_callback = 0U;
    open_cfw_test_runtime_async_create_period = 0U;
    open_cfw_test_runtime_async_create_user_data = 0U;
    open_cfw_test_runtime_async_repeat_calls = 0U;
    open_cfw_test_runtime_async_repeat_timer = 0U;
    open_cfw_test_runtime_async_repeat_count = 0;
    open_cfw_test_runtime_async_timer_user_data_result = allocation;
    open_cfw_test_runtime_async_timer_user_data_calls = 0U;
    open_cfw_test_runtime_async_timer_user_data_timer = 0U;
    open_cfw_test_runtime_async_delete_calls = 0U;
    open_cfw_test_runtime_async_deleted_timer = 0U;
    open_cfw_test_runtime_async_invoke_calls = 0U;
    open_cfw_test_runtime_async_invoked_callback = 0U;
    open_cfw_test_runtime_async_invoked_user_data = 0U;
    open_cfw_test_runtime_async_invoke_delete_calls_seen = 0U;
    open_cfw_test_runtime_async_invoke_free_calls_seen = 0U;
    open_cfw_test_runtime_async_mutate_info_on_invoke = 0U;
    open_cfw_test_runtime_async_event_count = 0U;
    open_cfw_test_runtime_async_events[0] = 0U;
    open_cfw_test_runtime_async_events[1] = 0U;
    open_cfw_test_runtime_async_events[2] = 0U;
    open_cfw_test_runtime_async_events[3] = 0U;
    open_cfw_test_runtime_async_events[4] = 0U;
    open_cfw_test_runtime_async_events[5] = 0U;
    open_cfw_test_runtime_async_events[6] = 0U;
    open_cfw_test_runtime_async_events[7] = 0U;
}

void open_cfw_test_runtime_async_cancel_reset(unsigned int count)
{
    unsigned int i;

    if (count > OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY) {
        count = OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY;
    }
    open_cfw_test_runtime_async_cancel_count = count;
    open_cfw_test_runtime_async_cancel_head =
        count == 0U
        ? 0U
        : open_cfw_test_runtime_async_cancel_timer_pointer(0U);
    open_cfw_test_runtime_async_cancel_get_next_calls = 0U;
    open_cfw_test_runtime_async_cancel_invalid_traversals = 0U;
    for (
        i = 0U;
        i < OPEN_CFW_TEST_RUNTIME_ASYNC_CANCEL_CAPACITY;
        i += 1U
    ) {
        open_cfw_test_runtime_async_cancel_timer[i].period = 0U;
        open_cfw_test_runtime_async_cancel_timer[i].last_run = 0U;
        open_cfw_test_runtime_async_cancel_timer[i].callback =
            0x004840ADU;
        open_cfw_test_runtime_async_cancel_timer[i].user_data =
            open_cfw_test_runtime_async_cancel_allocation_pointer(i);
        open_cfw_test_runtime_async_cancel_info[i].callback = 0U;
        open_cfw_test_runtime_async_cancel_info[i].user_data = 0U;
        open_cfw_test_runtime_async_cancel_active[i] =
            i < count ? 1U : 0U;
        open_cfw_test_runtime_async_cancel_next[i] =
            i + 1U < count
            ? open_cfw_test_runtime_async_cancel_timer_pointer(i + 1U)
            : 0U;
        open_cfw_test_runtime_async_cancel_get_next_argument[i] = 0U;
        open_cfw_test_runtime_async_cancel_deleted[i] = 0U;
        open_cfw_test_runtime_async_cancel_freed[i] = 0U;
    }
    open_cfw_test_runtime_async_cancel_get_next_argument[6] = 0U;
    open_cfw_test_runtime_async_cancel_get_next_argument[7] = 0U;
    open_cfw_test_runtime_async_delete_calls = 0U;
    open_cfw_test_runtime_async_deleted_timer = 0U;
    open_cfw_test_runtime_async_free_calls = 0U;
    open_cfw_test_runtime_async_freed = 0U;
    open_cfw_test_runtime_async_event_count = 0U;
}

void open_cfw_test_runtime_async_cancel_configure(
    unsigned int index,
    unsigned int timer_callback,
    unsigned int callback,
    unsigned int user_data
)
{
    if (index >= open_cfw_test_runtime_async_cancel_count) {
        return;
    }
    open_cfw_test_runtime_async_cancel_timer[index].callback =
        timer_callback;
    open_cfw_test_runtime_async_cancel_info[index].callback = callback;
    open_cfw_test_runtime_async_cancel_info[index].user_data =
        user_data;
}
