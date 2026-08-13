#include <stdint.h>

#define OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT 8U

unsigned int open_cfw_test_format_message_begin_result;
unsigned int open_cfw_test_format_message_length;
unsigned int open_cfw_test_format_message_position;
unsigned int open_cfw_test_format_message_begin_calls;
unsigned int open_cfw_test_format_message_next_calls;
unsigned int open_cfw_test_format_message_field_calls;
unsigned int open_cfw_test_format_message_extension_calls;
unsigned int open_cfw_test_format_message_event_count;
unsigned int open_cfw_test_format_message_types[
    OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT
];
unsigned int open_cfw_test_format_message_field_results[
    OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT
];
unsigned int open_cfw_test_format_message_extension_results[
    OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT
];
unsigned int open_cfw_test_format_message_events[
    OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT * 2U
];
void *open_cfw_test_format_message_begin_iterator;
const void *open_cfw_test_format_message_begin_descriptor;
const void *open_cfw_test_format_message_begin_source;
void *open_cfw_test_format_message_last_output;
const void *open_cfw_test_format_message_last_iterator;

static void open_cfw_test_format_message_record(unsigned int event)
{
    if (
        open_cfw_test_format_message_event_count
        < (OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT * 2U)
    ) {
        open_cfw_test_format_message_events[
            open_cfw_test_format_message_event_count
        ] = event;
    }
    open_cfw_test_format_message_event_count += 1U;
}

static void open_cfw_test_format_message_set_type(void *iterator)
{
    unsigned int position = open_cfw_test_format_message_position;

    if (position >= OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT) {
        position = OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT - 1U;
    }
    ((unsigned char *)iterator)[0x16] =
        (unsigned char)open_cfw_test_format_message_types[position];
}

void open_cfw_test_format_message_reset(void)
{
    unsigned int index;

    open_cfw_test_format_message_begin_result = 1U;
    open_cfw_test_format_message_length = 1U;
    open_cfw_test_format_message_position = 0U;
    open_cfw_test_format_message_begin_calls = 0U;
    open_cfw_test_format_message_next_calls = 0U;
    open_cfw_test_format_message_field_calls = 0U;
    open_cfw_test_format_message_extension_calls = 0U;
    open_cfw_test_format_message_event_count = 0U;
    open_cfw_test_format_message_begin_iterator = (void *)0;
    open_cfw_test_format_message_begin_descriptor = (const void *)0;
    open_cfw_test_format_message_begin_source = (const void *)0;
    open_cfw_test_format_message_last_output = (void *)0;
    open_cfw_test_format_message_last_iterator = (const void *)0;
    for (index = 0U; index < OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT; index += 1U) {
        open_cfw_test_format_message_types[index] = 0U;
        open_cfw_test_format_message_field_results[index] = 1U;
        open_cfw_test_format_message_extension_results[index] = 1U;
    }
    for (
        index = 0U;
        index < (OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT * 2U);
        index += 1U
    ) {
        open_cfw_test_format_message_events[index] = 0U;
    }
}

unsigned int open_cfw_test_format_message_begin(
    void *iterator,
    const void *descriptor,
    const void *source
)
{
    open_cfw_test_format_message_begin_calls += 1U;
    open_cfw_test_format_message_begin_iterator = iterator;
    open_cfw_test_format_message_begin_descriptor = descriptor;
    open_cfw_test_format_message_begin_source = source;
    open_cfw_test_format_message_record(1U);
    if (open_cfw_test_format_message_begin_result != 0U) {
        open_cfw_test_format_message_set_type(iterator);
    }
    return open_cfw_test_format_message_begin_result;
}

unsigned int open_cfw_test_format_message_next(void *iterator)
{
    open_cfw_test_format_message_next_calls += 1U;
    open_cfw_test_format_message_record(4U);
    open_cfw_test_format_message_position += 1U;
    if (
        open_cfw_test_format_message_position
        >= open_cfw_test_format_message_length
    ) {
        return 0U;
    }
    open_cfw_test_format_message_set_type(iterator);
    return 1U;
}

unsigned int open_cfw_test_format_message_field(
    void *output,
    const void *iterator
)
{
    unsigned int position = open_cfw_test_format_message_position;

    if (position >= OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT) {
        position = OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT - 1U;
    }
    open_cfw_test_format_message_field_calls += 1U;
    open_cfw_test_format_message_last_output = output;
    open_cfw_test_format_message_last_iterator = iterator;
    open_cfw_test_format_message_record(2U);
    return open_cfw_test_format_message_field_results[position];
}

unsigned int open_cfw_test_format_message_extension(
    void *output,
    const void *iterator
)
{
    unsigned int position = open_cfw_test_format_message_position;

    if (position >= OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT) {
        position = OPEN_CFW_TEST_FORMAT_MESSAGE_LIMIT - 1U;
    }
    open_cfw_test_format_message_extension_calls += 1U;
    open_cfw_test_format_message_last_output = output;
    open_cfw_test_format_message_last_iterator = iterator;
    open_cfw_test_format_message_record(3U);
    return open_cfw_test_format_message_extension_results[position];
}

#define OPEN_CFW_FORMAT_MESSAGE_ITERATOR_BEGIN( \
    iterator, \
    descriptor, \
    source \
) \
    open_cfw_test_format_message_begin( \
        (iterator), \
        (descriptor), \
        (source) \
    )
#define OPEN_CFW_FORMAT_MESSAGE_ITERATOR_NEXT(iterator) \
    open_cfw_test_format_message_next((iterator))
#define OPEN_CFW_FORMAT_MESSAGE_FIELD_ENCODE(output, iterator) \
    open_cfw_test_format_message_field((output), (iterator))
#define OPEN_CFW_FORMAT_MESSAGE_EXTENSION_ENCODE(output, iterator) \
    open_cfw_test_format_message_extension((output), (iterator))

#include "../../components/apollo_main/core_overlay/format_message.c"
