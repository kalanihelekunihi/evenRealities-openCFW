#include <stdint.h>

typedef unsigned int (*open_cfw_format_extension_callback_fn)(
    void *output,
    const void *record
);

struct open_cfw_test_format_extension_record {
    struct open_cfw_test_format_extension_record *next;
    unsigned int custom;
    unsigned int index;
};

unsigned int open_cfw_test_format_extension_init_result;
unsigned int open_cfw_test_format_extension_regular_result;
unsigned int open_cfw_test_format_extension_callback_result;
unsigned int open_cfw_test_format_extension_init_calls;
unsigned int open_cfw_test_format_extension_regular_calls;
unsigned int open_cfw_test_format_extension_callback_calls;
unsigned int open_cfw_test_format_extension_error_calls;
unsigned int open_cfw_test_format_extension_last_error;
unsigned int open_cfw_test_format_extension_event_count;
unsigned int open_cfw_test_format_extension_events[8];
const void *open_cfw_test_format_extension_head;
void *open_cfw_test_format_extension_init_iterator;
const void *open_cfw_test_format_extension_init_field;
void *open_cfw_test_format_extension_last_output;
const void *open_cfw_test_format_extension_last_record;
struct open_cfw_test_format_extension_record
    open_cfw_test_format_extension_records[3];

static void open_cfw_test_format_extension_record_event(
    unsigned int event
)
{
    if (open_cfw_test_format_extension_event_count < 8U) {
        open_cfw_test_format_extension_events[
            open_cfw_test_format_extension_event_count
        ] = event;
    }
    open_cfw_test_format_extension_event_count += 1U;
}

void open_cfw_test_format_extension_reset(void)
{
    unsigned int index;

    open_cfw_test_format_extension_init_result = 1U;
    open_cfw_test_format_extension_regular_result = 1U;
    open_cfw_test_format_extension_callback_result = 1U;
    open_cfw_test_format_extension_init_calls = 0U;
    open_cfw_test_format_extension_regular_calls = 0U;
    open_cfw_test_format_extension_callback_calls = 0U;
    open_cfw_test_format_extension_error_calls = 0U;
    open_cfw_test_format_extension_last_error = 0U;
    open_cfw_test_format_extension_event_count = 0U;
    open_cfw_test_format_extension_head = (const void *)0;
    open_cfw_test_format_extension_init_iterator = (void *)0;
    open_cfw_test_format_extension_init_field = (const void *)0;
    open_cfw_test_format_extension_last_output = (void *)0;
    open_cfw_test_format_extension_last_record = (const void *)0;
    for (index = 0U; index < 8U; index += 1U) {
        open_cfw_test_format_extension_events[index] = 0U;
    }
    for (index = 0U; index < 3U; index += 1U) {
        open_cfw_test_format_extension_records[index].next =
            index < 2U
                ? &open_cfw_test_format_extension_records[index + 1U]
                : (struct open_cfw_test_format_extension_record *)0;
        open_cfw_test_format_extension_records[index].custom = 0U;
        open_cfw_test_format_extension_records[index].index = index;
    }
}

unsigned int open_cfw_test_format_extension_iterator_init(
    void *iterator,
    const void *field
)
{
    open_cfw_test_format_extension_init_calls += 1U;
    open_cfw_test_format_extension_init_iterator = iterator;
    open_cfw_test_format_extension_init_field = field;
    open_cfw_test_format_extension_record_event(1U);
    return open_cfw_test_format_extension_init_result;
}

unsigned int open_cfw_format_regular_field_encode(
    void *output,
    const void *field
)
{
    open_cfw_test_format_extension_regular_calls += 1U;
    open_cfw_test_format_extension_last_output = output;
    open_cfw_test_format_extension_last_record = field;
    open_cfw_test_format_extension_record_event(2U);
    return open_cfw_test_format_extension_regular_result;
}

unsigned int open_cfw_test_format_extension_callback(
    void *output,
    const void *record
)
{
    open_cfw_test_format_extension_callback_calls += 1U;
    open_cfw_test_format_extension_last_output = output;
    open_cfw_test_format_extension_last_record = record;
    open_cfw_test_format_extension_record_event(3U);
    return open_cfw_test_format_extension_callback_result;
}

open_cfw_format_extension_callback_fn
open_cfw_test_format_extension_read_callback(const void *record)
{
    const struct open_cfw_test_format_extension_record *item =
        (const struct open_cfw_test_format_extension_record *)record;

    return item->custom != 0U
        ? open_cfw_test_format_extension_callback
        : (open_cfw_format_extension_callback_fn)0;
}

void open_cfw_test_format_extension_set_error(
    void *output,
    unsigned int error
)
{
    unsigned int *current =
        (unsigned int *)(void *)((unsigned char *)output + 0x10U);

    open_cfw_test_format_extension_error_calls += 1U;
    open_cfw_test_format_extension_last_error = error;
    if (*current == 0U) {
        *current = error;
    }
}

#define OPEN_CFW_FORMAT_EXTENSION_ITERATOR_INIT(iterator, field) \
    open_cfw_test_format_extension_iterator_init((iterator), (field))
#define OPEN_CFW_FORMAT_EXTENSION_HEAD(field) \
    ((void)(field), open_cfw_test_format_extension_head)
#define OPEN_CFW_FORMAT_EXTENSION_NEXT(record) \
    (((const struct open_cfw_test_format_extension_record *)(record))->next)
#define OPEN_CFW_FORMAT_EXTENSION_CALLBACK(record) \
    open_cfw_test_format_extension_read_callback((record))
#define OPEN_CFW_FORMAT_EXTENSION_SET_ERROR(output, error) \
    open_cfw_test_format_extension_set_error((output), (error))

#include "../../components/apollo_main/core_overlay/format_extension.c"
