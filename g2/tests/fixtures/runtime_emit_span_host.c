/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 runtime byte-span emitter.
 */

#include "../../components/apollo_main/core_overlay/runtime_emit_span.c"

struct open_cfw_runtime_emit_context open_cfw_test_runtime_emit_context;
unsigned int open_cfw_test_runtime_emit_calls;
unsigned int open_cfw_test_runtime_emit_states[256];
unsigned int open_cfw_test_runtime_emit_values[256];
unsigned int open_cfw_test_runtime_emit_results[256];
unsigned int open_cfw_test_runtime_emit_result_count;

static unsigned int open_cfw_test_runtime_emit_callback(
    unsigned int output_state,
    unsigned int byte_value
)
{
    unsigned int index = open_cfw_test_runtime_emit_calls;
    unsigned int result = 0U;

    if (index < 256U) {
        open_cfw_test_runtime_emit_states[index] = output_state;
        open_cfw_test_runtime_emit_values[index] = byte_value;
        if (index < open_cfw_test_runtime_emit_result_count) {
            result = open_cfw_test_runtime_emit_results[index];
        }
    }
    open_cfw_test_runtime_emit_calls = index + 1U;
    return result;
}

void open_cfw_test_runtime_emit_reset(
    unsigned int output_state,
    unsigned int emitted_count
)
{
    open_cfw_test_runtime_emit_context.reserved_00 = 0x00000000U;
    open_cfw_test_runtime_emit_context.reserved_04 = 0x04040404U;
    open_cfw_test_runtime_emit_context.output_state = output_state;
    open_cfw_test_runtime_emit_context.reserved_0c = 0x0c0c0c0cU;
    open_cfw_test_runtime_emit_context.reserved_10 = 0x10101010U;
    open_cfw_test_runtime_emit_context.reserved_14 = 0x14141414U;
    open_cfw_test_runtime_emit_context.reserved_18 = 0x18181818U;
    open_cfw_test_runtime_emit_context.reserved_1c = 0x1c1c1c1cU;
    open_cfw_test_runtime_emit_context.reserved_20 = 0x20202020U;
    open_cfw_test_runtime_emit_context.reserved_24 = 0x24242424U;
    open_cfw_test_runtime_emit_context.reserved_28 = 0x28282828U;
    open_cfw_test_runtime_emit_context.emitted_count = emitted_count;
    open_cfw_test_runtime_emit_calls = 0U;
    open_cfw_test_runtime_emit_result_count = 0U;
}

int open_cfw_test_runtime_emit_execute(
    const unsigned char *source,
    unsigned int length
)
{
    return open_cfw_runtime_emit_span(
        open_cfw_test_runtime_emit_callback,
        &open_cfw_test_runtime_emit_context,
        source,
        length
    );
}
