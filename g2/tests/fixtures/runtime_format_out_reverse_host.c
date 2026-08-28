/*
 * SPDX-License-Identifier: MIT
 *
 * Host callback trace for the source-owned reverse-output formatter.
 */

unsigned int open_cfw_test_format_out_reverse_event_count;
unsigned int open_cfw_test_format_out_reverse_characters[256];
unsigned int open_cfw_test_format_out_reverse_indices[256];
unsigned int open_cfw_test_format_out_reverse_maximum_lengths[256];
__UINTPTR_TYPE__ open_cfw_test_format_out_reverse_callback_tokens[256];
void *open_cfw_test_format_out_reverse_buffers[256];

static void open_cfw_test_format_out_reverse_call_output(
    __UINTPTR_TYPE__ callback,
    unsigned int character,
    unsigned char *buffer,
    unsigned int index,
    unsigned int maximum_length
)
{
    unsigned int event = open_cfw_test_format_out_reverse_event_count;

    if (event < 256U) {
        open_cfw_test_format_out_reverse_characters[event] = character;
        open_cfw_test_format_out_reverse_indices[event] = index;
        open_cfw_test_format_out_reverse_maximum_lengths[event] =
            maximum_length;
        open_cfw_test_format_out_reverse_callback_tokens[event] = callback;
        open_cfw_test_format_out_reverse_buffers[event] = buffer;
    }
    open_cfw_test_format_out_reverse_event_count = event + 1U;
    if (buffer != (unsigned char *)0 && index < maximum_length) {
        buffer[index] = (unsigned char)character;
    }
}

#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE_CALL_OUTPUT( \
    callback, \
    character, \
    buffer, \
    index, \
    maximum_length \
) \
    open_cfw_test_format_out_reverse_call_output( \
        (__UINTPTR_TYPE__)(callback), \
        (character), \
        (buffer), \
        (index), \
        (maximum_length) \
    )

#include "../../components/apollo_main/core_overlay/runtime_format_out_reverse.c"

void open_cfw_test_format_out_reverse_reset(void)
{
    unsigned int index;

    open_cfw_test_format_out_reverse_event_count = 0U;
    for (index = 0U; index < 256U; index += 1U) {
        open_cfw_test_format_out_reverse_characters[index] = 0U;
        open_cfw_test_format_out_reverse_indices[index] = 0U;
        open_cfw_test_format_out_reverse_maximum_lengths[index] = 0U;
        open_cfw_test_format_out_reverse_callback_tokens[index] = 0U;
        open_cfw_test_format_out_reverse_buffers[index] = (void *)0;
    }
}
