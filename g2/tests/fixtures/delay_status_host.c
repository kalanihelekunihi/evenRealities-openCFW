/*
 * SPDX-License-Identifier: MIT
 *
 * Native host substitution for the Apollo510 status-wait helpers.
 */

#define OPEN_CFW_DELAY_STATUS_EVENT_CAPACITY 512U
#define OPEN_CFW_DELAY_STATUS_SEQUENCE_CAPACITY 256U

unsigned int open_cfw_test_delay_status_sequence[
    OPEN_CFW_DELAY_STATUS_SEQUENCE_CAPACITY
];
unsigned int open_cfw_test_delay_status_sequence_count;
unsigned int open_cfw_test_delay_status_sequence_index;
unsigned int open_cfw_test_delay_status_read_count;
unsigned int open_cfw_test_delay_status_delay_count;
unsigned int open_cfw_test_delay_status_event_count;
unsigned int open_cfw_test_delay_status_event_kind[
    OPEN_CFW_DELAY_STATUS_EVENT_CAPACITY
];
unsigned int open_cfw_test_delay_status_event_address[
    OPEN_CFW_DELAY_STATUS_EVENT_CAPACITY
];
unsigned int open_cfw_test_delay_status_event_value[
    OPEN_CFW_DELAY_STATUS_EVENT_CAPACITY
];

static void
open_cfw_test_delay_status_event(
    unsigned int kind,
    unsigned int address,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_delay_status_event_count++;

    if (index < OPEN_CFW_DELAY_STATUS_EVENT_CAPACITY) {
        open_cfw_test_delay_status_event_kind[index] = kind;
        open_cfw_test_delay_status_event_address[index] = address;
        open_cfw_test_delay_status_event_value[index] = value;
    }
}

static unsigned int
open_cfw_test_delay_status_read32(unsigned int address)
{
    unsigned int index = open_cfw_test_delay_status_sequence_index++;
    unsigned int value = 0U;

    if (open_cfw_test_delay_status_sequence_count != 0U) {
        if (index >= open_cfw_test_delay_status_sequence_count) {
            index = open_cfw_test_delay_status_sequence_count - 1U;
        }
        value = open_cfw_test_delay_status_sequence[index];
    }

    ++open_cfw_test_delay_status_read_count;
    open_cfw_test_delay_status_event(1U, address, value);
    return value;
}

static void
open_cfw_test_delay_status_delay_us(unsigned int microseconds)
{
    ++open_cfw_test_delay_status_delay_count;
    open_cfw_test_delay_status_event(2U, 0U, microseconds);
}

#define OPEN_CFW_DELAY_STATUS_READ32(address) \
    open_cfw_test_delay_status_read32((address))
#define OPEN_CFW_DELAY_STATUS_DELAY_US(microseconds) \
    open_cfw_test_delay_status_delay_us((microseconds))

#include "../../components/apollo_main/core_overlay/delay_status.c"

unsigned int open_cfw_test_delay_status_check_raw(
    unsigned int maximum_delay_microseconds,
    unsigned int address,
    unsigned int mask,
    unsigned int value,
    unsigned int is_equal
)
{
    return open_cfw_delay_us_status_check(
        maximum_delay_microseconds,
        address,
        mask,
        value,
        (unsigned char)is_equal
    );
}

void open_cfw_test_delay_status_reset(void)
{
    unsigned int index;

    open_cfw_test_delay_status_sequence_count = 1U;
    open_cfw_test_delay_status_sequence_index = 0U;
    open_cfw_test_delay_status_read_count = 0U;
    open_cfw_test_delay_status_delay_count = 0U;
    open_cfw_test_delay_status_event_count = 0U;

    for (
        index = 0U;
        index < OPEN_CFW_DELAY_STATUS_SEQUENCE_CAPACITY;
        ++index
    ) {
        open_cfw_test_delay_status_sequence[index] = 0U;
    }
    for (
        index = 0U;
        index < OPEN_CFW_DELAY_STATUS_EVENT_CAPACITY;
        ++index
    ) {
        open_cfw_test_delay_status_event_kind[index] = 0U;
        open_cfw_test_delay_status_event_address[index] = 0U;
        open_cfw_test_delay_status_event_value[index] = 0U;
    }
}
