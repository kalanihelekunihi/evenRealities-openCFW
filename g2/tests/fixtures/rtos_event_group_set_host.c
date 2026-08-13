/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_event_group_set_uintptr;

struct open_cfw_test_rtos_event_group_set_item {
    unsigned int value;
    unsigned int next_index;
};

unsigned int open_cfw_test_rtos_event_group_set_events[128];
unsigned int open_cfw_test_rtos_event_group_set_event_count;
unsigned int open_cfw_test_rtos_event_group_set_fail_stop_calls;
unsigned int open_cfw_test_rtos_event_group_set_suspend_calls;
unsigned int open_cfw_test_rtos_event_group_set_resume_calls;
unsigned int open_cfw_test_rtos_event_group_set_read_calls;
unsigned int open_cfw_test_rtos_event_group_set_write_calls;
unsigned int open_cfw_test_rtos_event_group_set_head_calls;
unsigned int open_cfw_test_rtos_event_group_set_next_calls;
unsigned int open_cfw_test_rtos_event_group_set_value_calls;
unsigned int open_cfw_test_rtos_event_group_set_remove_calls;
unsigned int open_cfw_test_rtos_event_group_set_bits;
unsigned int open_cfw_test_rtos_event_group_set_head_index;
unsigned int open_cfw_test_rtos_event_group_set_last_write;
unsigned int open_cfw_test_rtos_event_group_set_remove_mutation_call;
unsigned int open_cfw_test_rtos_event_group_set_remove_mutation_bits;
unsigned int open_cfw_test_rtos_event_group_set_resume_mutation_enabled;
unsigned int open_cfw_test_rtos_event_group_set_resume_mutation_bits;
unsigned int open_cfw_test_rtos_event_group_set_removed_indices[8];
unsigned int open_cfw_test_rtos_event_group_set_removed_values[8];
open_cfw_test_rtos_event_group_set_uintptr
    open_cfw_test_rtos_event_group_set_last_group;
struct open_cfw_test_rtos_event_group_set_item
    open_cfw_test_rtos_event_group_set_items[8];

static void open_cfw_test_rtos_event_group_set_record(unsigned int event)
{
    open_cfw_test_rtos_event_group_set_events[
        open_cfw_test_rtos_event_group_set_event_count++
    ] = event;
}

void open_cfw_test_rtos_event_group_set_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_event_group_set_event_count = 0U;
    open_cfw_test_rtos_event_group_set_fail_stop_calls = 0U;
    open_cfw_test_rtos_event_group_set_suspend_calls = 0U;
    open_cfw_test_rtos_event_group_set_resume_calls = 0U;
    open_cfw_test_rtos_event_group_set_read_calls = 0U;
    open_cfw_test_rtos_event_group_set_write_calls = 0U;
    open_cfw_test_rtos_event_group_set_head_calls = 0U;
    open_cfw_test_rtos_event_group_set_next_calls = 0U;
    open_cfw_test_rtos_event_group_set_value_calls = 0U;
    open_cfw_test_rtos_event_group_set_remove_calls = 0U;
    open_cfw_test_rtos_event_group_set_bits = 0U;
    open_cfw_test_rtos_event_group_set_head_index = 7U;
    open_cfw_test_rtos_event_group_set_last_write = 0U;
    open_cfw_test_rtos_event_group_set_remove_mutation_call = 0U;
    open_cfw_test_rtos_event_group_set_remove_mutation_bits = 0U;
    open_cfw_test_rtos_event_group_set_resume_mutation_enabled = 0U;
    open_cfw_test_rtos_event_group_set_resume_mutation_bits = 0U;
    open_cfw_test_rtos_event_group_set_last_group = 0U;
    for (index = 0U; index < 128U; ++index) {
        open_cfw_test_rtos_event_group_set_events[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_event_group_set_items[index].value = 0U;
        open_cfw_test_rtos_event_group_set_items[index].next_index = 7U;
        open_cfw_test_rtos_event_group_set_removed_indices[index] = 0U;
        open_cfw_test_rtos_event_group_set_removed_values[index] = 0U;
    }
}

void open_cfw_test_rtos_event_group_set_set_bits(unsigned int bits)
{
    open_cfw_test_rtos_event_group_set_bits = bits;
}

void open_cfw_test_rtos_event_group_set_set_head(unsigned int index)
{
    open_cfw_test_rtos_event_group_set_head_index = index;
}

void open_cfw_test_rtos_event_group_set_set_item(
    unsigned int index,
    unsigned int value,
    unsigned int next_index
)
{
    open_cfw_test_rtos_event_group_set_items[index].value = value;
    open_cfw_test_rtos_event_group_set_items[index].next_index = next_index;
}

void open_cfw_test_rtos_event_group_set_set_remove_mutation(
    unsigned int call,
    unsigned int bits
)
{
    open_cfw_test_rtos_event_group_set_remove_mutation_call = call;
    open_cfw_test_rtos_event_group_set_remove_mutation_bits = bits;
}

void open_cfw_test_rtos_event_group_set_set_resume_mutation(
    unsigned int enabled,
    unsigned int bits
)
{
    open_cfw_test_rtos_event_group_set_resume_mutation_enabled = enabled;
    open_cfw_test_rtos_event_group_set_resume_mutation_bits = bits;
}

static void open_cfw_test_rtos_event_group_set_suspend(void)
{
    open_cfw_test_rtos_event_group_set_record(20U);
    ++open_cfw_test_rtos_event_group_set_suspend_calls;
}

static unsigned int open_cfw_test_rtos_event_group_set_resume(void)
{
    open_cfw_test_rtos_event_group_set_record(90U);
    ++open_cfw_test_rtos_event_group_set_resume_calls;
    if (
        open_cfw_test_rtos_event_group_set_resume_mutation_enabled != 0U
    ) {
        open_cfw_test_rtos_event_group_set_bits =
            open_cfw_test_rtos_event_group_set_resume_mutation_bits;
    }
    return 0U;
}

static unsigned int open_cfw_test_rtos_event_group_set_read_bits(
    void *group
)
{
    open_cfw_test_rtos_event_group_set_record(30U);
    ++open_cfw_test_rtos_event_group_set_read_calls;
    open_cfw_test_rtos_event_group_set_last_group =
        (open_cfw_test_rtos_event_group_set_uintptr)group;
    return open_cfw_test_rtos_event_group_set_bits;
}

static void open_cfw_test_rtos_event_group_set_write_bits(
    void *group,
    unsigned int bits
)
{
    open_cfw_test_rtos_event_group_set_record(40U);
    ++open_cfw_test_rtos_event_group_set_write_calls;
    open_cfw_test_rtos_event_group_set_last_group =
        (open_cfw_test_rtos_event_group_set_uintptr)group;
    open_cfw_test_rtos_event_group_set_last_write = bits;
    open_cfw_test_rtos_event_group_set_bits = bits;
}

static void *open_cfw_test_rtos_event_group_set_list_end(void *group)
{
    open_cfw_test_rtos_event_group_set_last_group =
        (open_cfw_test_rtos_event_group_set_uintptr)group;
    return &open_cfw_test_rtos_event_group_set_items[7];
}

static void *open_cfw_test_rtos_event_group_set_list_head(void *group)
{
    open_cfw_test_rtos_event_group_set_record(50U);
    ++open_cfw_test_rtos_event_group_set_head_calls;
    open_cfw_test_rtos_event_group_set_last_group =
        (open_cfw_test_rtos_event_group_set_uintptr)group;
    return &open_cfw_test_rtos_event_group_set_items[
        open_cfw_test_rtos_event_group_set_head_index
    ];
}

static void *open_cfw_test_rtos_event_group_set_item_next(void *item)
{
    struct open_cfw_test_rtos_event_group_set_item *typed_item =
        (struct open_cfw_test_rtos_event_group_set_item *)item;

    open_cfw_test_rtos_event_group_set_record(60U);
    ++open_cfw_test_rtos_event_group_set_next_calls;
    return &open_cfw_test_rtos_event_group_set_items[
        typed_item->next_index
    ];
}

static unsigned int open_cfw_test_rtos_event_group_set_item_value(
    void *item
)
{
    open_cfw_test_rtos_event_group_set_record(70U);
    ++open_cfw_test_rtos_event_group_set_value_calls;
    return (
        (struct open_cfw_test_rtos_event_group_set_item *)item
    )->value;
}

static unsigned int open_cfw_test_rtos_event_group_set_remove(
    void *item,
    unsigned int value
)
{
    struct open_cfw_test_rtos_event_group_set_item *typed_item =
        (struct open_cfw_test_rtos_event_group_set_item *)item;
    unsigned int call =
        open_cfw_test_rtos_event_group_set_remove_calls++;
    unsigned int index = (unsigned int)(
        typed_item - open_cfw_test_rtos_event_group_set_items
    );

    open_cfw_test_rtos_event_group_set_record(80U);
    open_cfw_test_rtos_event_group_set_removed_indices[call] = index;
    open_cfw_test_rtos_event_group_set_removed_values[call] = value;
    typed_item->next_index = 7U;
    if (
        open_cfw_test_rtos_event_group_set_remove_mutation_call
        == call + 1U
    ) {
        open_cfw_test_rtos_event_group_set_bits =
            open_cfw_test_rtos_event_group_set_remove_mutation_bits;
    }
    return 0U;
}

static void open_cfw_test_rtos_event_group_set_fail_stop(void)
{
    open_cfw_test_rtos_event_group_set_record(10U);
    ++open_cfw_test_rtos_event_group_set_fail_stop_calls;
}

#define OPEN_CFW_RTOS_EVENT_GROUP_SET_SUSPEND_ALL() \
    open_cfw_test_rtos_event_group_set_suspend()
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_RESUME_ALL() \
    open_cfw_test_rtos_event_group_set_resume()
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_REMOVE(item, value) \
    open_cfw_test_rtos_event_group_set_remove((item), (value))
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_READ_BITS(group) \
    open_cfw_test_rtos_event_group_set_read_bits(group)
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_WRITE_BITS(group, value) \
    open_cfw_test_rtos_event_group_set_write_bits((group), (value))
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_END(group) \
    open_cfw_test_rtos_event_group_set_list_end(group)
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_LIST_HEAD(group) \
    open_cfw_test_rtos_event_group_set_list_head(group)
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_NEXT(item) \
    open_cfw_test_rtos_event_group_set_item_next(item)
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_ITEM_VALUE(item) \
    open_cfw_test_rtos_event_group_set_item_value(item)
#define OPEN_CFW_RTOS_EVENT_GROUP_SET_FAIL_STOP() \
    open_cfw_test_rtos_event_group_set_fail_stop()

#include "../../components/apollo_main/core_overlay/rtos_event_group_set.c"
