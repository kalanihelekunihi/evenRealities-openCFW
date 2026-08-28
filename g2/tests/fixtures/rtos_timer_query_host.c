/*
 * SPDX-License-Identifier: MIT
 */

unsigned int open_cfw_test_rtos_timer_query_events[8];
unsigned int open_cfw_test_rtos_timer_query_event_count;
unsigned int open_cfw_test_rtos_timer_query_item_count;
unsigned int open_cfw_test_rtos_timer_query_head_expiry;
unsigned int open_cfw_test_rtos_timer_query_item_count_reads;
unsigned int open_cfw_test_rtos_timer_query_head_expiry_reads;

static void open_cfw_test_rtos_timer_query_record(unsigned int event)
{
    open_cfw_test_rtos_timer_query_events[
        open_cfw_test_rtos_timer_query_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_query_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_query_event_count = 0U;
    open_cfw_test_rtos_timer_query_item_count = 0U;
    open_cfw_test_rtos_timer_query_head_expiry = 0U;
    open_cfw_test_rtos_timer_query_item_count_reads = 0U;
    open_cfw_test_rtos_timer_query_head_expiry_reads = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_timer_query_events[index] = 0U;
    }
}

static unsigned int open_cfw_test_rtos_timer_query_read_item_count(void)
{
    open_cfw_test_rtos_timer_query_record(10U);
    ++open_cfw_test_rtos_timer_query_item_count_reads;
    return open_cfw_test_rtos_timer_query_item_count;
}

static unsigned int open_cfw_test_rtos_timer_query_read_head_expiry(void)
{
    open_cfw_test_rtos_timer_query_record(20U);
    ++open_cfw_test_rtos_timer_query_head_expiry_reads;
    return open_cfw_test_rtos_timer_query_head_expiry;
}

#define OPEN_CFW_RTOS_TIMER_QUERY_ITEM_COUNT() \
    open_cfw_test_rtos_timer_query_read_item_count()
#define OPEN_CFW_RTOS_TIMER_QUERY_HEAD_EXPIRY() \
    open_cfw_test_rtos_timer_query_read_head_expiry()

#include "../../components/apollo_main/core_overlay/rtos_timer_query.c"
