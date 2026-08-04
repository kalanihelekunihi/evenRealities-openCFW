#include <stdint.h>

struct open_cfw_test_format_default_field;

struct open_cfw_test_format_default_list {
    const struct open_cfw_test_format_default_field *items;
    unsigned int count;
};

struct open_cfw_test_format_default_field {
    unsigned int type;
    unsigned int length;
    const void *data;
    const void *auxiliary;
    unsigned int metadata_guard;
    unsigned int metadata_callback;
    const struct open_cfw_test_format_default_list *subdescriptor;
    const struct open_cfw_test_format_default_list *iterator_list;
    unsigned int iterator_index;
};

unsigned int open_cfw_test_format_default_bool_result;
unsigned int open_cfw_test_format_default_bool_calls;
unsigned int open_cfw_test_format_default_begin_calls;
unsigned int open_cfw_test_format_default_next_calls;
unsigned int open_cfw_test_format_default_begin_result;
const void *open_cfw_test_format_default_last_bool;
void *open_cfw_test_format_default_last_iterator;
const void *open_cfw_test_format_default_last_descriptor;
const void *open_cfw_test_format_default_last_source;

void open_cfw_test_format_default_reset(void)
{
    open_cfw_test_format_default_bool_result = 0U;
    open_cfw_test_format_default_bool_calls = 0U;
    open_cfw_test_format_default_begin_calls = 0U;
    open_cfw_test_format_default_next_calls = 0U;
    open_cfw_test_format_default_begin_result = 1U;
    open_cfw_test_format_default_last_bool = (const void *)0;
    open_cfw_test_format_default_last_iterator = (void *)0;
    open_cfw_test_format_default_last_descriptor = (const void *)0;
    open_cfw_test_format_default_last_source = (const void *)0;
}

unsigned int open_cfw_format_read_bool(const void *value)
{
    open_cfw_test_format_default_bool_calls += 1U;
    open_cfw_test_format_default_last_bool = value;
    return open_cfw_test_format_default_bool_result;
}

unsigned int open_cfw_test_format_default_iterator_begin(
    void *iterator,
    const void *descriptor,
    const void *source
)
{
    struct open_cfw_test_format_default_field *state =
        (struct open_cfw_test_format_default_field *)iterator;
    const struct open_cfw_test_format_default_list *list =
        (const struct open_cfw_test_format_default_list *)descriptor;

    open_cfw_test_format_default_begin_calls += 1U;
    open_cfw_test_format_default_last_iterator = iterator;
    open_cfw_test_format_default_last_descriptor = descriptor;
    open_cfw_test_format_default_last_source = source;
    if (
        (open_cfw_test_format_default_begin_result == 0U)
        || (list == (const struct open_cfw_test_format_default_list *)0)
        || (list->count == 0U)
    ) {
        return 0U;
    }
    *state = list->items[0];
    state->iterator_list = list;
    state->iterator_index = 0U;
    return 1U;
}

unsigned int open_cfw_test_format_default_iterator_next(void *iterator)
{
    struct open_cfw_test_format_default_field *state =
        (struct open_cfw_test_format_default_field *)iterator;
    const struct open_cfw_test_format_default_list *list =
        state->iterator_list;
    unsigned int next = state->iterator_index + 1U;

    open_cfw_test_format_default_next_calls += 1U;
    if (next >= list->count) {
        return 0U;
    }
    *state = list->items[next];
    state->iterator_list = list;
    state->iterator_index = next;
    return 1U;
}

#define OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BYTES \
    sizeof(struct open_cfw_test_format_default_field)
#define OPEN_CFW_FORMAT_DEFAULT_TYPE(field) \
    (((const struct open_cfw_test_format_default_field *)(field))->type)
#define OPEN_CFW_FORMAT_DEFAULT_LENGTH(field) \
    (((const struct open_cfw_test_format_default_field *)(field))->length)
#define OPEN_CFW_FORMAT_DEFAULT_DATA(field) \
    (((const struct open_cfw_test_format_default_field *)(field))->data)
#define OPEN_CFW_FORMAT_DEFAULT_AUX(field) \
    (((const struct open_cfw_test_format_default_field *)(field))->auxiliary)
#define OPEN_CFW_FORMAT_DEFAULT_SUBDESCRIPTOR(field) \
    (((const struct open_cfw_test_format_default_field *)(field))->subdescriptor)
#define OPEN_CFW_FORMAT_DEFAULT_METADATA_GUARD(field) \
    (((const struct open_cfw_test_format_default_field *)(field))->metadata_guard)
#define OPEN_CFW_FORMAT_DEFAULT_METADATA_CALLBACK(field) \
    (((const struct open_cfw_test_format_default_field *)(field))->metadata_callback)
#define OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BEGIN(iterator, descriptor, source) \
    open_cfw_test_format_default_iterator_begin( \
        (iterator), \
        (descriptor), \
        (source) \
    )
#define OPEN_CFW_FORMAT_DEFAULT_ITERATOR_NEXT(iterator) \
    open_cfw_test_format_default_iterator_next((iterator))

#include "../../components/apollo_main/core_overlay/format_default.c"
