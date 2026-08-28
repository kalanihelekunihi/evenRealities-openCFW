/*
 * SPDX-License-Identifier: MIT
 *
 * Native host substitution for the Apollo510 word-copy helper.
 */

#define OPEN_CFW_READ_WORDS_EVENT_CAPACITY 1024U

unsigned int open_cfw_test_read_words_event_count;
unsigned int open_cfw_test_read_words_event_kind[
    OPEN_CFW_READ_WORDS_EVENT_CAPACITY
];
unsigned int open_cfw_test_read_words_event_value[
    OPEN_CFW_READ_WORDS_EVENT_CAPACITY
];

static void
open_cfw_test_read_words_event(unsigned int kind, unsigned int value)
{
    unsigned int index = open_cfw_test_read_words_event_count++;

    if (index < OPEN_CFW_READ_WORDS_EVENT_CAPACITY) {
        open_cfw_test_read_words_event_kind[index] = kind;
        open_cfw_test_read_words_event_value[index] = value;
    }
}

static unsigned int
open_cfw_test_read_words_read32(
    const volatile unsigned int *source
)
{
    unsigned int value = *source;
    open_cfw_test_read_words_event(1U, value);
    return value;
}

static void
open_cfw_test_read_words_write32(
    volatile unsigned int *destination,
    unsigned int value
)
{
    open_cfw_test_read_words_event(2U, value);
    *destination = value;
}

#define OPEN_CFW_READ_WORDS_READ32(source) \
    open_cfw_test_read_words_read32((source))
#define OPEN_CFW_READ_WORDS_WRITE32(destination, value) \
    open_cfw_test_read_words_write32((destination), (value))

#include "../../components/apollo_main/core_overlay/read_words.c"

void open_cfw_test_read_words_reset(void)
{
    unsigned int index;

    open_cfw_test_read_words_event_count = 0U;
    for (index = 0U; index < OPEN_CFW_READ_WORDS_EVENT_CAPACITY; ++index) {
        open_cfw_test_read_words_event_kind[index] = 0U;
        open_cfw_test_read_words_event_value[index] = 0U;
    }
}

