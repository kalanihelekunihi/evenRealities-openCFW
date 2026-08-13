/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

struct open_cfw_test_rtos_timer_runtime_init_list {
    unsigned int words[5];
};

struct open_cfw_test_rtos_timer_runtime_init_queue_control {
    unsigned char bytes[80];
};

unsigned int open_cfw_test_rtos_timer_runtime_init_events[32];
unsigned int open_cfw_test_rtos_timer_runtime_init_event_count;
unsigned int open_cfw_test_rtos_timer_runtime_init_event_depths[32];
unsigned int open_cfw_test_rtos_timer_runtime_init_critical_depth;
unsigned int open_cfw_test_rtos_timer_runtime_init_enter_calls;
unsigned int open_cfw_test_rtos_timer_runtime_init_exit_calls;
unsigned int open_cfw_test_rtos_timer_runtime_init_queue_reads;
unsigned int open_cfw_test_rtos_timer_runtime_init_queue_writes;
unsigned int open_cfw_test_rtos_timer_runtime_init_list_calls;
unsigned int open_cfw_test_rtos_timer_runtime_init_current_writes;
unsigned int open_cfw_test_rtos_timer_runtime_init_overflow_writes;
unsigned int open_cfw_test_rtos_timer_runtime_init_create_calls;
unsigned int open_cfw_test_rtos_timer_runtime_init_queue_length;
unsigned int open_cfw_test_rtos_timer_runtime_init_item_size;
unsigned int open_cfw_test_rtos_timer_runtime_init_queue_type;

static struct open_cfw_test_rtos_timer_runtime_init_list
    open_cfw_test_rtos_timer_runtime_init_lists[2];
static struct open_cfw_test_rtos_timer_runtime_init_queue_control
    open_cfw_test_rtos_timer_runtime_init_control;
static unsigned char open_cfw_test_rtos_timer_runtime_init_storage[800];
static void *open_cfw_test_rtos_timer_runtime_init_queue;
static void *open_cfw_test_rtos_timer_runtime_init_queue_result;
static void *open_cfw_test_rtos_timer_runtime_init_current;
static void *open_cfw_test_rtos_timer_runtime_init_overflow;
static void *open_cfw_test_rtos_timer_runtime_init_list_arguments[2];
static void *open_cfw_test_rtos_timer_runtime_init_create_storage;
static void *open_cfw_test_rtos_timer_runtime_init_create_control;

static void open_cfw_test_rtos_timer_runtime_init_record(
    unsigned int event
)
{
    unsigned int index =
        open_cfw_test_rtos_timer_runtime_init_event_count++;

    open_cfw_test_rtos_timer_runtime_init_events[index] = event;
    open_cfw_test_rtos_timer_runtime_init_event_depths[index] =
        open_cfw_test_rtos_timer_runtime_init_critical_depth;
}

void open_cfw_test_rtos_timer_runtime_init_reset(void)
{
    unsigned int index;
    unsigned int word;

    open_cfw_test_rtos_timer_runtime_init_event_count = 0U;
    open_cfw_test_rtos_timer_runtime_init_critical_depth = 0U;
    open_cfw_test_rtos_timer_runtime_init_enter_calls = 0U;
    open_cfw_test_rtos_timer_runtime_init_exit_calls = 0U;
    open_cfw_test_rtos_timer_runtime_init_queue_reads = 0U;
    open_cfw_test_rtos_timer_runtime_init_queue_writes = 0U;
    open_cfw_test_rtos_timer_runtime_init_list_calls = 0U;
    open_cfw_test_rtos_timer_runtime_init_current_writes = 0U;
    open_cfw_test_rtos_timer_runtime_init_overflow_writes = 0U;
    open_cfw_test_rtos_timer_runtime_init_create_calls = 0U;
    open_cfw_test_rtos_timer_runtime_init_queue_length = 0U;
    open_cfw_test_rtos_timer_runtime_init_item_size = 0U;
    open_cfw_test_rtos_timer_runtime_init_queue_type = 0U;
    open_cfw_test_rtos_timer_runtime_init_queue = (void *)0;
    open_cfw_test_rtos_timer_runtime_init_queue_result =
        (void *)(__UINTPTR_TYPE__)0x12345678U;
    open_cfw_test_rtos_timer_runtime_init_current = (void *)0;
    open_cfw_test_rtos_timer_runtime_init_overflow = (void *)0;
    open_cfw_test_rtos_timer_runtime_init_create_storage = (void *)0;
    open_cfw_test_rtos_timer_runtime_init_create_control = (void *)0;
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_rtos_timer_runtime_init_events[index] = 0U;
        open_cfw_test_rtos_timer_runtime_init_event_depths[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_rtos_timer_runtime_init_list_arguments[index] =
            (void *)0;
        for (word = 0U; word < 5U; ++word) {
            open_cfw_test_rtos_timer_runtime_init_lists[index].words[word] =
                0xA5A5A5A5U;
        }
    }
    for (index = 0U; index < 80U; ++index) {
        open_cfw_test_rtos_timer_runtime_init_control.bytes[index] = 0xA5U;
    }
    for (index = 0U; index < 800U; ++index) {
        open_cfw_test_rtos_timer_runtime_init_storage[index] = 0x5AU;
    }
}

void open_cfw_test_rtos_timer_runtime_init_set_queue(unsigned int value)
{
    open_cfw_test_rtos_timer_runtime_init_queue =
        (void *)(__UINTPTR_TYPE__)value;
}

void open_cfw_test_rtos_timer_runtime_init_set_result(unsigned int value)
{
    open_cfw_test_rtos_timer_runtime_init_queue_result =
        (void *)(__UINTPTR_TYPE__)value;
}

unsigned int open_cfw_test_rtos_timer_runtime_init_queue_value(void)
{
    return (unsigned int)(__UINTPTR_TYPE__)
        open_cfw_test_rtos_timer_runtime_init_queue;
}

unsigned int open_cfw_test_rtos_timer_runtime_init_current_identity(void)
{
    if (
        open_cfw_test_rtos_timer_runtime_init_current
        == &open_cfw_test_rtos_timer_runtime_init_lists[0]
    ) {
        return 1U;
    }
    return 0U;
}

unsigned int open_cfw_test_rtos_timer_runtime_init_overflow_identity(void)
{
    if (
        open_cfw_test_rtos_timer_runtime_init_overflow
        == &open_cfw_test_rtos_timer_runtime_init_lists[1]
    ) {
        return 2U;
    }
    return 0U;
}

unsigned int open_cfw_test_rtos_timer_runtime_init_create_storage_valid(void)
{
    return open_cfw_test_rtos_timer_runtime_init_create_storage
        == open_cfw_test_rtos_timer_runtime_init_storage;
}

unsigned int open_cfw_test_rtos_timer_runtime_init_create_control_valid(void)
{
    return open_cfw_test_rtos_timer_runtime_init_create_control
        == &open_cfw_test_rtos_timer_runtime_init_control;
}

unsigned int open_cfw_test_rtos_timer_runtime_init_list_argument_identity(
    unsigned int index
)
{
    if (
        open_cfw_test_rtos_timer_runtime_init_list_arguments[index]
        == &open_cfw_test_rtos_timer_runtime_init_lists[index]
    ) {
        return index + 1U;
    }
    return 0U;
}

static void open_cfw_test_rtos_timer_runtime_init_enter(void)
{
    ++open_cfw_test_rtos_timer_runtime_init_critical_depth;
    ++open_cfw_test_rtos_timer_runtime_init_enter_calls;
    open_cfw_test_rtos_timer_runtime_init_record(1U);
}

static void open_cfw_test_rtos_timer_runtime_init_exit(void)
{
    open_cfw_test_rtos_timer_runtime_init_record(40U);
    ++open_cfw_test_rtos_timer_runtime_init_exit_calls;
    --open_cfw_test_rtos_timer_runtime_init_critical_depth;
}

static void *open_cfw_test_rtos_timer_runtime_init_read_queue(void)
{
    open_cfw_test_rtos_timer_runtime_init_record(2U);
    ++open_cfw_test_rtos_timer_runtime_init_queue_reads;
    return open_cfw_test_rtos_timer_runtime_init_queue;
}

static void open_cfw_test_rtos_timer_runtime_init_write_queue(void *value)
{
    open_cfw_test_rtos_timer_runtime_init_record(31U);
    ++open_cfw_test_rtos_timer_runtime_init_queue_writes;
    open_cfw_test_rtos_timer_runtime_init_queue = value;
}

static void open_cfw_test_rtos_timer_runtime_init_list(void *list)
{
    unsigned int index =
        open_cfw_test_rtos_timer_runtime_init_list_calls++;

    open_cfw_test_rtos_timer_runtime_init_record(10U + index);
    open_cfw_test_rtos_timer_runtime_init_list_arguments[index] = list;
}

static void open_cfw_test_rtos_timer_runtime_init_write_current(void *value)
{
    open_cfw_test_rtos_timer_runtime_init_record(20U);
    ++open_cfw_test_rtos_timer_runtime_init_current_writes;
    open_cfw_test_rtos_timer_runtime_init_current = value;
}

static void open_cfw_test_rtos_timer_runtime_init_write_overflow(void *value)
{
    open_cfw_test_rtos_timer_runtime_init_record(21U);
    ++open_cfw_test_rtos_timer_runtime_init_overflow_writes;
    open_cfw_test_rtos_timer_runtime_init_overflow = value;
}

static void *open_cfw_test_rtos_timer_runtime_init_create(
    unsigned int queue_length,
    unsigned int item_size,
    void *storage,
    void *control,
    unsigned int queue_type
)
{
    open_cfw_test_rtos_timer_runtime_init_record(30U);
    ++open_cfw_test_rtos_timer_runtime_init_create_calls;
    open_cfw_test_rtos_timer_runtime_init_queue_length = queue_length;
    open_cfw_test_rtos_timer_runtime_init_item_size = item_size;
    open_cfw_test_rtos_timer_runtime_init_create_storage = storage;
    open_cfw_test_rtos_timer_runtime_init_create_control = control;
    open_cfw_test_rtos_timer_runtime_init_queue_type = queue_type;
    return open_cfw_test_rtos_timer_runtime_init_queue_result;
}

#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_ENTER_CRITICAL() \
    open_cfw_test_rtos_timer_runtime_init_enter()
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_EXIT_CRITICAL() \
    open_cfw_test_rtos_timer_runtime_init_exit()
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_READ_QUEUE() \
    open_cfw_test_rtos_timer_runtime_init_read_queue()
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_QUEUE(value) \
    open_cfw_test_rtos_timer_runtime_init_write_queue(value)
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CURRENT_LIST() \
    ((void *)&open_cfw_test_rtos_timer_runtime_init_lists[0])
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_OVERFLOW_LIST() \
    ((void *)&open_cfw_test_rtos_timer_runtime_init_lists[1])
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_CURRENT(value) \
    open_cfw_test_rtos_timer_runtime_init_write_current(value)
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_WRITE_OVERFLOW(value) \
    open_cfw_test_rtos_timer_runtime_init_write_overflow(value)
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_LIST(list) \
    open_cfw_test_rtos_timer_runtime_init_list(list)
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_STORAGE() \
    ((void *)open_cfw_test_rtos_timer_runtime_init_storage)
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_QUEUE_CONTROL() \
    ((void *)&open_cfw_test_rtos_timer_runtime_init_control)
#define OPEN_CFW_RTOS_TIMER_RUNTIME_INIT_CREATE_QUEUE(...) \
    open_cfw_test_rtos_timer_runtime_init_create(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/rtos_timer_runtime_initialize.c"
