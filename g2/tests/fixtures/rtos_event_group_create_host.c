/*
 * SPDX-License-Identifier: MIT
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_event_group_uintptr;

unsigned int open_cfw_test_rtos_event_group_events[16];
unsigned int open_cfw_test_rtos_event_group_event_count;
unsigned int open_cfw_test_rtos_event_group_fail_stop_calls;
unsigned int open_cfw_test_rtos_event_group_size_reads;
unsigned int open_cfw_test_rtos_event_group_bits_writes;
unsigned int open_cfw_test_rtos_event_group_list_initializes;
unsigned int open_cfw_test_rtos_event_group_static_writes;
unsigned int open_cfw_test_rtos_event_group_allocate_calls;
unsigned int open_cfw_test_rtos_event_group_object_size;
unsigned int open_cfw_test_rtos_event_group_allocate_size;
unsigned int open_cfw_test_rtos_event_group_last_bits;
unsigned int open_cfw_test_rtos_event_group_last_static;
open_cfw_test_rtos_event_group_uintptr
    open_cfw_test_rtos_event_group_allocate_result;
open_cfw_test_rtos_event_group_uintptr
    open_cfw_test_rtos_event_group_last_bits_group;
open_cfw_test_rtos_event_group_uintptr
    open_cfw_test_rtos_event_group_last_list;
open_cfw_test_rtos_event_group_uintptr
    open_cfw_test_rtos_event_group_last_static_group;
unsigned char open_cfw_test_rtos_event_group_object[32];

static void open_cfw_test_rtos_event_group_record(unsigned int event)
{
    open_cfw_test_rtos_event_group_events[
        open_cfw_test_rtos_event_group_event_count++
    ] = event;
}

void open_cfw_test_rtos_event_group_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_event_group_event_count = 0U;
    open_cfw_test_rtos_event_group_fail_stop_calls = 0U;
    open_cfw_test_rtos_event_group_size_reads = 0U;
    open_cfw_test_rtos_event_group_bits_writes = 0U;
    open_cfw_test_rtos_event_group_list_initializes = 0U;
    open_cfw_test_rtos_event_group_static_writes = 0U;
    open_cfw_test_rtos_event_group_allocate_calls = 0U;
    open_cfw_test_rtos_event_group_object_size = 0x20U;
    open_cfw_test_rtos_event_group_allocate_size = 0U;
    open_cfw_test_rtos_event_group_last_bits = 0U;
    open_cfw_test_rtos_event_group_last_static = 0U;
    open_cfw_test_rtos_event_group_allocate_result = 0U;
    open_cfw_test_rtos_event_group_last_bits_group = 0U;
    open_cfw_test_rtos_event_group_last_list = 0U;
    open_cfw_test_rtos_event_group_last_static_group = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_event_group_events[index] = 0U;
    }
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_rtos_event_group_object[index] = 0xA5U;
    }
}

void open_cfw_test_rtos_event_group_set_object_size(unsigned int value)
{
    open_cfw_test_rtos_event_group_object_size = value;
}

void open_cfw_test_rtos_event_group_set_allocate_result(
    open_cfw_test_rtos_event_group_uintptr value
)
{
    open_cfw_test_rtos_event_group_allocate_result = value;
}

static unsigned int open_cfw_test_rtos_event_group_read_object_size(void)
{
    open_cfw_test_rtos_event_group_record(20U);
    ++open_cfw_test_rtos_event_group_size_reads;
    return open_cfw_test_rtos_event_group_object_size;
}

static void open_cfw_test_rtos_event_group_write_bits(
    void *group,
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_record(30U);
    ++open_cfw_test_rtos_event_group_bits_writes;
    open_cfw_test_rtos_event_group_last_bits_group =
        (open_cfw_test_rtos_event_group_uintptr)group;
    open_cfw_test_rtos_event_group_last_bits = value;
    *(unsigned int *)group = value;
}

static void open_cfw_test_rtos_event_group_list_initialize(void *list)
{
    open_cfw_test_rtos_event_group_record(40U);
    ++open_cfw_test_rtos_event_group_list_initializes;
    open_cfw_test_rtos_event_group_last_list =
        (open_cfw_test_rtos_event_group_uintptr)list;
}

static void open_cfw_test_rtos_event_group_write_static(
    void *group,
    unsigned int value
)
{
    open_cfw_test_rtos_event_group_record(50U);
    ++open_cfw_test_rtos_event_group_static_writes;
    open_cfw_test_rtos_event_group_last_static_group =
        (open_cfw_test_rtos_event_group_uintptr)group;
    open_cfw_test_rtos_event_group_last_static = value;
    ((unsigned char *)group)[0x1CU] = (unsigned char)value;
}

static void *open_cfw_test_rtos_event_group_allocate(unsigned int size)
{
    open_cfw_test_rtos_event_group_record(60U);
    ++open_cfw_test_rtos_event_group_allocate_calls;
    open_cfw_test_rtos_event_group_allocate_size = size;
    return (void *)open_cfw_test_rtos_event_group_allocate_result;
}

static void open_cfw_test_rtos_event_group_fail_stop(void)
{
    open_cfw_test_rtos_event_group_record(10U);
    ++open_cfw_test_rtos_event_group_fail_stop_calls;
}

#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_LIST_INITIALIZE(list) \
    open_cfw_test_rtos_event_group_list_initialize(list)
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_ALLOCATE(size) \
    open_cfw_test_rtos_event_group_allocate(size)
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_OBJECT_SIZE() \
    open_cfw_test_rtos_event_group_read_object_size()
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_BITS(group, value) \
    open_cfw_test_rtos_event_group_write_bits((group), (value))
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_WRITE_STATIC(group, value) \
    open_cfw_test_rtos_event_group_write_static((group), (value))
#define OPEN_CFW_RTOS_EVENT_GROUP_CREATE_FAIL_STOP() \
    open_cfw_test_rtos_event_group_fail_stop()

#include "../../components/apollo_main/core_overlay/rtos_event_group_create.c"
