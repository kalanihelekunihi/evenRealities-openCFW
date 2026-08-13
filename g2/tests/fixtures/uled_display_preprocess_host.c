#include <string.h>

#include "uled_display_preprocess_host.h"

int open_cfw_test_uled_start_result;
uint32_t open_cfw_test_uled_assert_count;
uint32_t open_cfw_test_uled_diagnostic_count;
uint32_t open_cfw_test_uled_call_count;
uint32_t open_cfw_test_uled_descriptor[7];
uint32_t open_cfw_test_uled_region[4];
uintptr_t open_cfw_test_uled_source;
uint32_t open_cfw_test_uled_source_args[5];
uint32_t open_cfw_test_uled_offset[2];
uint32_t open_cfw_test_uled_sequence[6];
char open_cfw_test_uled_assert_expression[80];

void open_cfw_test_uled_assert(const char *expression)
{
    ++open_cfw_test_uled_assert_count;
    strcpy(open_cfw_test_uled_assert_expression, expression);
}

int open_cfw_test_uled_gpu_start(
    const void *destination, const void *region, uint32_t flags
)
{
    (void)flags;
    memcpy(open_cfw_test_uled_descriptor, destination, 28u);
    memcpy(open_cfw_test_uled_region, region, 16u);
    return open_cfw_test_uled_start_result;
}

void open_cfw_test_uled_destination_configure(uint32_t channel, uint32_t enabled)
{
    open_cfw_test_uled_sequence[open_cfw_test_uled_call_count++] =
        0x100u | channel | (enabled << 4);
}

void open_cfw_test_uled_destination_mode(uint32_t channel)
{
    open_cfw_test_uled_sequence[open_cfw_test_uled_call_count++] = 0x200u | channel;
}

void open_cfw_test_uled_destination_enable(uint32_t channel, uint32_t enabled)
{
    open_cfw_test_uled_sequence[open_cfw_test_uled_call_count++] =
        0x300u | channel | (enabled << 4);
}

void open_cfw_test_uled_source_configure(
    const void *source, uint32_t width, uint32_t height,
    uint32_t format, uint32_t stride, uint32_t flags
)
{
    open_cfw_test_uled_sequence[open_cfw_test_uled_call_count++] = 0x400u;
    open_cfw_test_uled_source = (uintptr_t)source;
    open_cfw_test_uled_source_args[0] = width;
    open_cfw_test_uled_source_args[1] = height;
    open_cfw_test_uled_source_args[2] = format;
    open_cfw_test_uled_source_args[3] = stride;
    open_cfw_test_uled_source_args[4] = flags;
}

void open_cfw_test_uled_offset_configure(uint32_t x, uint32_t y)
{
    open_cfw_test_uled_sequence[open_cfw_test_uled_call_count++] = 0x500u;
    open_cfw_test_uled_offset[0] = x;
    open_cfw_test_uled_offset[1] = y;
}

void open_cfw_test_uled_commit(uint32_t enabled)
{
    open_cfw_test_uled_sequence[open_cfw_test_uled_call_count++] =
        0x600u | enabled;
}

void open_cfw_test_uled_diagnostic(uint32_t result)
{
    ++open_cfw_test_uled_diagnostic_count;
    open_cfw_test_uled_sequence[0] = result;
}

void open_cfw_test_uled_reset(void)
{
    open_cfw_test_uled_start_result = 1;
    open_cfw_test_uled_assert_count = 0;
    open_cfw_test_uled_diagnostic_count = 0;
    open_cfw_test_uled_call_count = 0;
    memset(open_cfw_test_uled_descriptor, 0, sizeof(open_cfw_test_uled_descriptor));
    memset(open_cfw_test_uled_region, 0, sizeof(open_cfw_test_uled_region));
    open_cfw_test_uled_source = 0;
    memset(open_cfw_test_uled_source_args, 0, sizeof(open_cfw_test_uled_source_args));
    memset(open_cfw_test_uled_offset, 0, sizeof(open_cfw_test_uled_offset));
    memset(open_cfw_test_uled_sequence, 0, sizeof(open_cfw_test_uled_sequence));
    memset(open_cfw_test_uled_assert_expression, 0, sizeof(open_cfw_test_uled_assert_expression));
}
