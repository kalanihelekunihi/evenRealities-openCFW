/*
 * SPDX-License-Identifier: GPL-3.0-only
 */

unsigned int open_cfw_test_rtos_timer_initialize_events[16];
unsigned int open_cfw_test_rtos_timer_initialize_event_count;
unsigned int open_cfw_test_rtos_timer_initialize_runtime_calls;
unsigned int open_cfw_test_rtos_timer_initialize_fail_stop_calls;
unsigned int open_cfw_test_rtos_timer_initialize_store_calls;
unsigned int open_cfw_test_rtos_timer_initialize_store_offsets[8];
unsigned int open_cfw_test_rtos_timer_initialize_store_values[8];
unsigned int open_cfw_test_rtos_timer_initialize_or_calls;
unsigned int open_cfw_test_rtos_timer_initialize_or_offset;
unsigned int open_cfw_test_rtos_timer_initialize_or_mask;
unsigned char open_cfw_test_rtos_timer_initialize_object[44];
unsigned char open_cfw_test_rtos_timer_initialize_runtime_snapshot[44];

static void open_cfw_test_rtos_timer_initialize_record(unsigned int event)
{
    open_cfw_test_rtos_timer_initialize_events[
        open_cfw_test_rtos_timer_initialize_event_count++
    ] = event;
}

void open_cfw_test_rtos_timer_initialize_reset(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_initialize_event_count = 0U;
    open_cfw_test_rtos_timer_initialize_runtime_calls = 0U;
    open_cfw_test_rtos_timer_initialize_fail_stop_calls = 0U;
    open_cfw_test_rtos_timer_initialize_store_calls = 0U;
    open_cfw_test_rtos_timer_initialize_or_calls = 0U;
    open_cfw_test_rtos_timer_initialize_or_offset = 0U;
    open_cfw_test_rtos_timer_initialize_or_mask = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtos_timer_initialize_events[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_rtos_timer_initialize_store_offsets[index] = 0U;
        open_cfw_test_rtos_timer_initialize_store_values[index] = 0U;
    }
    for (index = 0U; index < 44U; ++index) {
        open_cfw_test_rtos_timer_initialize_object[index] = 0xA5U;
        open_cfw_test_rtos_timer_initialize_runtime_snapshot[index] = 0U;
    }
}

static void open_cfw_test_rtos_timer_initialize_runtime(void)
{
    unsigned int index;

    open_cfw_test_rtos_timer_initialize_record(1U);
    ++open_cfw_test_rtos_timer_initialize_runtime_calls;
    for (index = 0U; index < 44U; ++index) {
        open_cfw_test_rtos_timer_initialize_runtime_snapshot[index] =
            open_cfw_test_rtos_timer_initialize_object[index];
    }
}

static void open_cfw_test_rtos_timer_initialize_fail_stop(void)
{
    open_cfw_test_rtos_timer_initialize_record(40U);
    ++open_cfw_test_rtos_timer_initialize_fail_stop_calls;
}

static void open_cfw_test_rtos_timer_initialize_store_u32(
    void *object,
    unsigned int offset,
    unsigned int value
)
{
    unsigned char *bytes = (unsigned char *)object + offset;
    unsigned int index = open_cfw_test_rtos_timer_initialize_store_calls;

    open_cfw_test_rtos_timer_initialize_record(10U + index);
    open_cfw_test_rtos_timer_initialize_store_offsets[index] = offset;
    open_cfw_test_rtos_timer_initialize_store_values[index] = value;
    ++open_cfw_test_rtos_timer_initialize_store_calls;
    bytes[0] = (unsigned char)value;
    bytes[1] = (unsigned char)(value >> 8U);
    bytes[2] = (unsigned char)(value >> 16U);
    bytes[3] = (unsigned char)(value >> 24U);
}

static void open_cfw_test_rtos_timer_initialize_or_u8(
    void *object,
    unsigned int offset,
    unsigned int mask
)
{
    open_cfw_test_rtos_timer_initialize_record(30U);
    ++open_cfw_test_rtos_timer_initialize_or_calls;
    open_cfw_test_rtos_timer_initialize_or_offset = offset;
    open_cfw_test_rtos_timer_initialize_or_mask = mask;
    ((unsigned char *)object)[offset] |= (unsigned char)mask;
}

#define OPEN_CFW_RTOS_TIMER_INITIALIZE_RUNTIME() \
    open_cfw_test_rtos_timer_initialize_runtime()
#define OPEN_CFW_RTOS_TIMER_INITIALIZE_FAIL_STOP() \
    open_cfw_test_rtos_timer_initialize_fail_stop()
#define OPEN_CFW_RTOS_TIMER_INITIALIZE_STORE_U32(object, offset, value) \
    open_cfw_test_rtos_timer_initialize_store_u32(object, offset, value)
#define OPEN_CFW_RTOS_TIMER_INITIALIZE_OR_U8(object, offset, mask) \
    open_cfw_test_rtos_timer_initialize_or_u8(object, offset, mask)

#include "../../components/apollo_main/core_overlay/rtos_timer_initialize.c"
