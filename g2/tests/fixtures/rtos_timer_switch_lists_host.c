/*
 * SPDX-License-Identifier: MIT
 */

struct open_cfw_test_rtos_timer_switch_list {
    unsigned int item_count;
    unsigned int head_expiry;
    unsigned int identity;
};

unsigned int open_cfw_test_rtos_timer_switch_events[128];
unsigned int open_cfw_test_rtos_timer_switch_event_count;
unsigned int open_cfw_test_rtos_timer_switch_current_reads;
unsigned int open_cfw_test_rtos_timer_switch_overflow_reads;
unsigned int open_cfw_test_rtos_timer_switch_count_reads;
unsigned int open_cfw_test_rtos_timer_switch_head_reads;
unsigned int open_cfw_test_rtos_timer_switch_current_writes;
unsigned int open_cfw_test_rtos_timer_switch_overflow_writes;
unsigned int open_cfw_test_rtos_timer_switch_process_calls;
unsigned int open_cfw_test_rtos_timer_switch_process_expiries[16];
unsigned int open_cfw_test_rtos_timer_switch_process_times[16];
unsigned int open_cfw_test_rtos_timer_switch_next_expiries[16];
unsigned int open_cfw_test_rtos_timer_switch_redirect_call;
unsigned int open_cfw_test_rtos_timer_switch_redirect_list;

static struct open_cfw_test_rtos_timer_switch_list
    open_cfw_test_rtos_timer_switch_lists[4];
static struct open_cfw_test_rtos_timer_switch_list
    *open_cfw_test_rtos_timer_switch_current;
static struct open_cfw_test_rtos_timer_switch_list
    *open_cfw_test_rtos_timer_switch_overflow;

static void open_cfw_test_rtos_timer_switch_record(unsigned int event)
{
    open_cfw_test_rtos_timer_switch_events[
        open_cfw_test_rtos_timer_switch_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_switch_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_switch_event_count = 0U;
    open_cfw_test_rtos_timer_switch_current_reads = 0U;
    open_cfw_test_rtos_timer_switch_overflow_reads = 0U;
    open_cfw_test_rtos_timer_switch_count_reads = 0U;
    open_cfw_test_rtos_timer_switch_head_reads = 0U;
    open_cfw_test_rtos_timer_switch_current_writes = 0U;
    open_cfw_test_rtos_timer_switch_overflow_writes = 0U;
    open_cfw_test_rtos_timer_switch_process_calls = 0U;
    open_cfw_test_rtos_timer_switch_redirect_call = 0U;
    open_cfw_test_rtos_timer_switch_redirect_list = 0U;
    open_cfw_test_rtos_timer_switch_current =
        &open_cfw_test_rtos_timer_switch_lists[0];
    open_cfw_test_rtos_timer_switch_overflow =
        &open_cfw_test_rtos_timer_switch_lists[1];
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_rtos_timer_switch_lists[index].item_count = 0U;
        open_cfw_test_rtos_timer_switch_lists[index].head_expiry = 0U;
        open_cfw_test_rtos_timer_switch_lists[index].identity = index;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_switch_process_expiries[index] = 0U;
        open_cfw_test_rtos_timer_switch_process_times[index] = 0U;
        open_cfw_test_rtos_timer_switch_next_expiries[index] = 0U;
    }
    for (index = 0U; index < 128U; ++index) {
        open_cfw_test_rtos_timer_switch_events[index] = 0U;
    }
}

void open_cfw_test_rtos_timer_switch_configure(
    unsigned int index,
    unsigned int item_count,
    unsigned int head_expiry
)
{
    open_cfw_test_rtos_timer_switch_lists[index].item_count = item_count;
    open_cfw_test_rtos_timer_switch_lists[index].head_expiry = head_expiry;
}

void open_cfw_test_rtos_timer_switch_set_current(unsigned int index)
{
    open_cfw_test_rtos_timer_switch_current =
        &open_cfw_test_rtos_timer_switch_lists[index];
}

void open_cfw_test_rtos_timer_switch_set_overflow(unsigned int index)
{
    open_cfw_test_rtos_timer_switch_overflow =
        &open_cfw_test_rtos_timer_switch_lists[index];
}

void open_cfw_test_rtos_timer_switch_set_next_expiry(
    unsigned int process_index,
    unsigned int expiry
)
{
    open_cfw_test_rtos_timer_switch_next_expiries[process_index] = expiry;
}

void open_cfw_test_rtos_timer_switch_set_redirect(
    unsigned int process_call,
    unsigned int list_index
)
{
    open_cfw_test_rtos_timer_switch_redirect_call = process_call;
    open_cfw_test_rtos_timer_switch_redirect_list = list_index;
}

unsigned int open_cfw_test_rtos_timer_switch_current_identity(void)
{
    return open_cfw_test_rtos_timer_switch_current->identity;
}

unsigned int open_cfw_test_rtos_timer_switch_overflow_identity(void)
{
    return open_cfw_test_rtos_timer_switch_overflow->identity;
}

static void *open_cfw_test_rtos_timer_switch_read_current(void)
{
    open_cfw_test_rtos_timer_switch_record(10U);
    ++open_cfw_test_rtos_timer_switch_current_reads;
    return open_cfw_test_rtos_timer_switch_current;
}

static void *open_cfw_test_rtos_timer_switch_read_overflow(void)
{
    open_cfw_test_rtos_timer_switch_record(20U);
    ++open_cfw_test_rtos_timer_switch_overflow_reads;
    return open_cfw_test_rtos_timer_switch_overflow;
}

static unsigned int open_cfw_test_rtos_timer_switch_read_count(void *list)
{
    struct open_cfw_test_rtos_timer_switch_list *typed = list;

    open_cfw_test_rtos_timer_switch_record(30U);
    ++open_cfw_test_rtos_timer_switch_count_reads;
    return typed->item_count;
}

static unsigned int open_cfw_test_rtos_timer_switch_read_head(void *list)
{
    struct open_cfw_test_rtos_timer_switch_list *typed = list;

    open_cfw_test_rtos_timer_switch_record(40U);
    ++open_cfw_test_rtos_timer_switch_head_reads;
    return typed->head_expiry;
}

static void open_cfw_test_rtos_timer_switch_process(
    unsigned int expiry,
    unsigned int time_now
)
{
    unsigned int index = open_cfw_test_rtos_timer_switch_process_calls;
    struct open_cfw_test_rtos_timer_switch_list *processed =
        open_cfw_test_rtos_timer_switch_current;

    open_cfw_test_rtos_timer_switch_record(50U);
    open_cfw_test_rtos_timer_switch_process_expiries[index] = expiry;
    open_cfw_test_rtos_timer_switch_process_times[index] = time_now;
    ++open_cfw_test_rtos_timer_switch_process_calls;
    if (processed->item_count != 0U) {
        --processed->item_count;
        if (processed->item_count != 0U) {
            processed->head_expiry =
                open_cfw_test_rtos_timer_switch_next_expiries[index];
        }
    }
    if (
        open_cfw_test_rtos_timer_switch_redirect_call
        == open_cfw_test_rtos_timer_switch_process_calls
    ) {
        open_cfw_test_rtos_timer_switch_current =
            &open_cfw_test_rtos_timer_switch_lists[
                open_cfw_test_rtos_timer_switch_redirect_list
            ];
    }
}

static void open_cfw_test_rtos_timer_switch_write_current(void *value)
{
    open_cfw_test_rtos_timer_switch_record(60U);
    ++open_cfw_test_rtos_timer_switch_current_writes;
    open_cfw_test_rtos_timer_switch_current = value;
}

static void open_cfw_test_rtos_timer_switch_write_overflow(void *value)
{
    open_cfw_test_rtos_timer_switch_record(70U);
    ++open_cfw_test_rtos_timer_switch_overflow_writes;
    open_cfw_test_rtos_timer_switch_overflow = value;
}

#define OPEN_CFW_RTOS_TIMER_SWITCH_READ_CURRENT() \
    open_cfw_test_rtos_timer_switch_read_current()
#define OPEN_CFW_RTOS_TIMER_SWITCH_READ_OVERFLOW() \
    open_cfw_test_rtos_timer_switch_read_overflow()
#define OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_CURRENT(value) \
    open_cfw_test_rtos_timer_switch_write_current(value)
#define OPEN_CFW_RTOS_TIMER_SWITCH_WRITE_OVERFLOW(value) \
    open_cfw_test_rtos_timer_switch_write_overflow(value)
#define OPEN_CFW_RTOS_TIMER_SWITCH_ITEM_COUNT(list) \
    open_cfw_test_rtos_timer_switch_read_count(list)
#define OPEN_CFW_RTOS_TIMER_SWITCH_HEAD_EXPIRY(list) \
    open_cfw_test_rtos_timer_switch_read_head(list)
#define OPEN_CFW_RTOS_TIMER_SWITCH_PROCESS_EXPIRED(expiry, time_now) \
    open_cfw_test_rtos_timer_switch_process(expiry, time_now)

#include "../../components/apollo_main/core_overlay/rtos_timer_switch_lists.c"

void open_cfw_test_rtos_timer_switch_run(void)
{
    open_cfw_rtos_timer_switch_lists();
}
