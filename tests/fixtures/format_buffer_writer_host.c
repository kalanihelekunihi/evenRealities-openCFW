unsigned int open_cfw_test_format_buffer_prefix_result;
unsigned int open_cfw_test_format_buffer_append_result;
unsigned int open_cfw_test_format_buffer_trace[2];
unsigned int open_cfw_test_format_buffer_trace_count;
void *open_cfw_test_format_buffer_prefix_output;
unsigned long long open_cfw_test_format_buffer_prefix_length;
void *open_cfw_test_format_buffer_append_output;
const void *open_cfw_test_format_buffer_append_data;
unsigned int open_cfw_test_format_buffer_append_length;

void open_cfw_test_format_buffer_reset(void)
{
    open_cfw_test_format_buffer_prefix_result = 1U;
    open_cfw_test_format_buffer_append_result = 1U;
    open_cfw_test_format_buffer_trace[0] = 0U;
    open_cfw_test_format_buffer_trace[1] = 0U;
    open_cfw_test_format_buffer_trace_count = 0U;
    open_cfw_test_format_buffer_prefix_output = (void *)0;
    open_cfw_test_format_buffer_prefix_length = 0U;
    open_cfw_test_format_buffer_append_output = (void *)0;
    open_cfw_test_format_buffer_append_data = (const void *)0;
    open_cfw_test_format_buffer_append_length = 0U;
}

unsigned int open_cfw_test_format_buffer_prefix(
    void *output,
    unsigned long long length
)
{
    open_cfw_test_format_buffer_trace[
        open_cfw_test_format_buffer_trace_count++
    ] = 1U;
    open_cfw_test_format_buffer_prefix_output = output;
    open_cfw_test_format_buffer_prefix_length = length;
    return open_cfw_test_format_buffer_prefix_result;
}

unsigned int open_cfw_test_format_buffer_append(
    void *output,
    const void *data,
    unsigned int length
)
{
    open_cfw_test_format_buffer_trace[
        open_cfw_test_format_buffer_trace_count++
    ] = 2U;
    open_cfw_test_format_buffer_append_output = output;
    open_cfw_test_format_buffer_append_data = data;
    open_cfw_test_format_buffer_append_length = length;
    return open_cfw_test_format_buffer_append_result;
}

#define OPEN_CFW_FORMAT_BUFFER_PREFIX(output, length) \
    open_cfw_test_format_buffer_prefix((output), (length))
#define OPEN_CFW_FORMAT_BUFFER_APPEND(output, data, length) \
    open_cfw_test_format_buffer_append((output), (data), (length))

#include "../../components/apollo_main/core_overlay/format_buffer_writer.c"
