/*
 * SPDX-License-Identifier: MIT
 */

typedef __UINTPTR_TYPE__ open_cfw_test_rtos_timer_insert_uintptr;

unsigned int open_cfw_test_rtos_timer_insert_events[16];
unsigned int open_cfw_test_rtos_timer_insert_event_count;
unsigned int open_cfw_test_rtos_timer_insert_timer[11];
unsigned int open_cfw_test_rtos_timer_insert_period_reads;
unsigned int open_cfw_test_rtos_timer_insert_active_list_reads;
unsigned int open_cfw_test_rtos_timer_insert_overflow_list_reads;
unsigned int open_cfw_test_rtos_timer_insert_list_calls;
void *open_cfw_test_rtos_timer_insert_lists[4];
void *open_cfw_test_rtos_timer_insert_items[4];
unsigned int open_cfw_test_rtos_timer_insert_active_list_tag;
unsigned int open_cfw_test_rtos_timer_insert_overflow_list_tag;

static void open_cfw_test_rtos_timer_insert_record(unsigned int event)
{
    open_cfw_test_rtos_timer_insert_events[
        open_cfw_test_rtos_timer_insert_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_insert_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_insert_event_count = 0U;
    open_cfw_test_rtos_timer_insert_period_reads = 0U;
    open_cfw_test_rtos_timer_insert_active_list_reads = 0U;
    open_cfw_test_rtos_timer_insert_overflow_list_reads = 0U;
    open_cfw_test_rtos_timer_insert_list_calls = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_insert_events[index] = 0U;
    }
    for (index = 0U; index < 11U; ++index) {
        open_cfw_test_rtos_timer_insert_timer[index] = 0U;
    }
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_rtos_timer_insert_lists[index] = (void *)0;
        open_cfw_test_rtos_timer_insert_items[index] = (void *)0;
    }
}

static void open_cfw_test_rtos_timer_insert_write_expiry(
    void *timer,
    unsigned int value
)
{
    open_cfw_test_rtos_timer_insert_record(10U);
    *(unsigned int *)((unsigned char *)timer + 0x04U) = value;
}

static void open_cfw_test_rtos_timer_insert_write_owner(void *timer)
{
    open_cfw_test_rtos_timer_insert_record(20U);
    *(unsigned int *)((unsigned char *)timer + 0x10U) =
        (unsigned int)(open_cfw_test_rtos_timer_insert_uintptr)timer;
}

static unsigned int open_cfw_test_rtos_timer_insert_read_period(
    void *timer
)
{
    open_cfw_test_rtos_timer_insert_record(30U);
    ++open_cfw_test_rtos_timer_insert_period_reads;
    return *(unsigned int *)((unsigned char *)timer + 0x18U);
}

static void *open_cfw_test_rtos_timer_insert_active_list(void)
{
    open_cfw_test_rtos_timer_insert_record(40U);
    ++open_cfw_test_rtos_timer_insert_active_list_reads;
    return &open_cfw_test_rtos_timer_insert_active_list_tag;
}

static void *open_cfw_test_rtos_timer_insert_overflow_list(void)
{
    open_cfw_test_rtos_timer_insert_record(50U);
    ++open_cfw_test_rtos_timer_insert_overflow_list_reads;
    return &open_cfw_test_rtos_timer_insert_overflow_list_tag;
}

static void open_cfw_test_rtos_timer_insert_list(
    void *list,
    void *item
)
{
    unsigned int index = open_cfw_test_rtos_timer_insert_list_calls;

    open_cfw_test_rtos_timer_insert_record(60U);
    open_cfw_test_rtos_timer_insert_lists[index] = list;
    open_cfw_test_rtos_timer_insert_items[index] = item;
    ++open_cfw_test_rtos_timer_insert_list_calls;
}

#define OPEN_CFW_RTOS_TIMER_INSERT_WRITE_EXPIRY(timer, value) \
    open_cfw_test_rtos_timer_insert_write_expiry(timer, value)
#define OPEN_CFW_RTOS_TIMER_INSERT_WRITE_OWNER(timer) \
    open_cfw_test_rtos_timer_insert_write_owner(timer)
#define OPEN_CFW_RTOS_TIMER_INSERT_PERIOD(timer) \
    open_cfw_test_rtos_timer_insert_read_period(timer)
#define OPEN_CFW_RTOS_TIMER_INSERT_ACTIVE_LIST() \
    open_cfw_test_rtos_timer_insert_active_list()
#define OPEN_CFW_RTOS_TIMER_INSERT_OVERFLOW_LIST() \
    open_cfw_test_rtos_timer_insert_overflow_list()
#define OPEN_CFW_RTOS_TIMER_INSERT_LIST_ITEM(timer) \
    ((void *)((unsigned char *)(timer) + 0x04U))
#define OPEN_CFW_RTOS_TIMER_INSERT_LIST(list, item) \
    open_cfw_test_rtos_timer_insert_list(list, item)

#include "../../components/apollo_main/core_overlay/rtos_timer_insert.c"

unsigned int open_cfw_test_rtos_timer_insert_run(
    unsigned int next_expiry,
    unsigned int time_now,
    unsigned int previous_expiry
)
{
    return open_cfw_rtos_timer_insert(
        open_cfw_test_rtos_timer_insert_timer,
        next_expiry,
        time_now,
        previous_expiry
    );
}
