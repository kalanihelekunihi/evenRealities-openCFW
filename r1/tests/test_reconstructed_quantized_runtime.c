/*
 * Host tests for the reconstructed shared quantized-neural runtime
 * (family unknown_shared_quantized_neural_runtime_candidate).  Expected
 * values are derived from the recovered stock semantics; see
 * docs/correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md.
 *
 * Exposes `void test_reconstructed_quantized_runtime(void)`; the integrator
 * wave wires it into the shared runner.
 */

#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "quantized_runtime/quantized_runtime.h"

static float test_fminf(float left, float right) {
    return fminf(left, right);
}

static float test_fmaxf(float left, float right) {
    return fmaxf(left, right);
}

static float test_floorf(float value) {
    return floorf(value);
}

static float test_expf(float value) {
    return expf(value);
}

static void test_qsort(void *base, size_t count, size_t size,
                       quantized_runtime_compare_fn compare) {
    qsort(base, count, size, compare);
}

static const quantized_runtime_providers test_providers = {
    test_fminf,
    test_fmaxf,
    test_floorf,
    test_expf,
    test_qsort,
    NULL,
    NULL,
    0u,
    0u,
    0u,
    0u,
};

static void test_rt_reset(quantized_runtime *rt) {
    quantized_runtime_initialize(rt, &test_providers);
}

static uint32_t test_f32_bits(float value) {
    uint32_t bits;
    memcpy(&bits, &value, sizeof(bits));
    return bits;
}

static void test_store_f32(uint8_t *destination, float value) {
    memcpy(destination, &value, sizeof(value));
}

static uint32_t test_load_u32(const uint8_t *source) {
    uint32_t value;
    memcpy(&value, source, sizeof(value));
    return value;
}

typedef struct {
    size_t calls;
    size_t last_bytes;
    int fail;
    size_t fail_on_call;
    size_t releases;
} recurrent_allocation_trace;

typedef struct {
    size_t calls;
    const void *descriptors[64];
    quantized_runtime_exec_tensor inputs[64];
    quantized_runtime_exec_tensor outputs[64];
} stage_trace;

static stage_trace g_stage_trace;
static const void *g_expected_remap_second_data;
static const void *g_expected_layer_temporary;
static const int8_t *g_expected_layer_adjusted_data;
static const int8_t *g_expected_layer_adjusted_values;
static size_t g_expected_layer_adjusted_count;
static const uint8_t *g_expected_second_workspace;

static uint32_t test_stage_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    const size_t index = g_stage_trace.calls;
    assert(index < 64u);
    assert(inputs != NULL && inputs[0] != NULL);
    assert(outputs != NULL && outputs[0] != NULL);
    g_stage_trace.descriptors[index] = descriptor;
    g_stage_trace.inputs[index] = *inputs[0];
    g_stage_trace.outputs[index] = *outputs[0];
    ++g_stage_trace.calls;
    return 0u;
}

static uint32_t test_remap_stage_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    assert(inputs != NULL && inputs[1] != NULL);
    assert(inputs[1]->data == g_expected_remap_second_data);
    return test_stage_execute(descriptor, inputs, outputs);
}

static uint32_t test_layer_input_stage_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    assert(inputs != NULL && inputs[0] != NULL);
    assert(inputs[0]->data == g_expected_layer_adjusted_data);
    assert(memcmp(inputs[0]->data, g_expected_layer_adjusted_values,
                  g_expected_layer_adjusted_count) == 0);
    return test_stage_execute(descriptor, inputs, outputs);
}

static uint32_t test_layer_final_stage_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    assert(inputs != NULL && inputs[2] != NULL && inputs[3] != NULL);
    assert(inputs[2]->data == g_expected_layer_temporary);
    assert(inputs[2]->dims[1] == 1u && inputs[2]->dims[2] == 3u);
    return test_stage_execute(descriptor, inputs, outputs);
}

static uint32_t test_merge_four_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *input_pairs,
    quantized_runtime_exec_tensor *const *outputs,
    uint32_t input_count) {
    assert(input_count == 4u);
    assert(input_pairs != NULL && outputs != NULL);
    assert(input_pairs[0]->data == g_expected_second_workspace);
    assert(input_pairs[2]->data == g_expected_second_workspace + 0xB4u);
    assert(input_pairs[4]->data == g_expected_second_workspace + 0x168u);
    assert(input_pairs[6]->data == g_expected_second_workspace + 0x21Cu);
    assert(outputs[0]->data == g_expected_second_workspace);
    assert(outputs[0]->dims[1] == 4u && outputs[0]->dims[2] == 180u);
    return test_stage_execute(descriptor, input_pairs, outputs);
}

static void *test_recurrent_allocate(void *context, size_t bytes) {
    recurrent_allocation_trace *trace = context;
    trace->calls += 1u;
    trace->last_bytes = bytes;
    if (trace->fail != 0 ||
            (trace->fail_on_call != 0u &&
             trace->calls == trace->fail_on_call)) {
        return NULL;
    }
    void *allocation = malloc(bytes);
    if (allocation != NULL) {
        memset(allocation, 0xA5, bytes);
    }
    return allocation;
}

static void test_recurrent_release(void *context, void *allocation) {
    recurrent_allocation_trace *trace = context;
    trace->releases += 1u;
    free(allocation);
}

static void test_round_helpers(void) {
    static const struct {
        float input;
        int32_t expected;
    } cases[] = {
        {2.5f, 3}, {-2.5f, -3}, {2.4f, 2}, {-2.4f, -2}, {0.5f, 1},
        {-0.5f, -1}, {0.0f, 0}, {-0.4f, 0}, {1.5f, 2}, {-1.5f, -2},
        {127.5f, 128}, {-127.5f, -128},
    };
    for (size_t index = 0u; index < sizeof(cases) / sizeof(cases[0]);
            ++index) {
        assert(quantized_runtime_round_half_away_from_zero_290fe(
                   cases[index].input) == cases[index].expected);
        assert(quantized_runtime_round_half_away_from_zero_29120(
                   cases[index].input) == cases[index].expected);
    }

    quantized_runtime rt;
    test_rt_reset(&rt);
    /* 0x0006FE20 zero-point compute. */
    assert(quantized_runtime_zero_point_compute(&rt, 0.0f, -1.0f, 1.0f) == 128);
    assert(quantized_runtime_zero_point_compute(&rt, 0.0f, 0.0f, 1.0f) == 0);
    assert(quantized_runtime_zero_point_compute(&rt, 0.25f, 0.0f, 0.5f) == 128);
    /* degenerate range clamps to 1e-4f: (0.5 - 0.5) * (255 / 1e-4) = 0. */
    assert(quantized_runtime_zero_point_compute(&rt, 0.5f, 0.5f, 0.5f) == 0);
    assert(quantized_runtime_zero_point_compute(NULL, 0.0f, -1.0f, 1.0f) == 0);
    quantized_runtime unbound;
    quantized_runtime_initialize(&unbound, NULL);
    assert(quantized_runtime_zero_point_compute(&unbound, 0.0f, -1.0f, 1.0f) ==
           0);
}

static void test_recurrent_executor(void) {
    float min_value = -1.0f;
    float max_value = 1.0f;
    assert(quantized_runtime_recurrent_range_adjust(
               &min_value, &max_value, 3u) == 3);
    assert(fabsf(min_value - (-1.0039216f)) < 1e-6f);
    assert(fabsf(max_value - 0.99607843f) < 1e-6f);
    assert(quantized_runtime_recurrent_zero_point(0.0f, -1.0f, 1.0f) ==
           128);
    assert(quantized_runtime_recurrent_range_adjust(
               &min_value, &min_value, 3u) == -1);
    assert(quantized_runtime_recurrent_range_adjust(NULL, &max_value, 3u) ==
           -1);

    const float extrema_values[] = {2.0f, -3.0f, 7.5f, 1.0f};
    float maximum = 0.0f;
    float minimum = 0.0f;
    quantized_runtime_float_min_max(extrema_values, 4u, &maximum, &minimum);
    assert(maximum == 7.5f && minimum == -3.0f);
    quantized_runtime_float_min_max(NULL, 4u, &maximum, &minimum);

    const uint8_t vector[] = {130u, 125u, 128u};
    const uint8_t matrix[] = {
        129u, 130u, 128u,
        127u, 128u, 131u,
    };
    int32_t dot[2] = {0, 0};
    quantized_runtime_u8_matrix_vector(vector, matrix, dot, 3u, 2u, 128,
                                       128);
    assert(dot[0] == -4);
    assert(dot[1] == -2);

    /* One-unit fixture exercises all three input/recurrent rows, both
     * sigmoid gates, the candidate tanh, persistent state, and model-region
     * resolution.  Centered weights make the hand-computed result solely a
     * function of the four recovered bias groups. */
    uint8_t model[8u + 16u * sizeof(float)];
    memset(model, 128, sizeof(model));
    const size_t tail_offset = 8u;
    test_store_f32(model + tail_offset + 0u * sizeof(float), 0.0f);
    test_store_f32(model + tail_offset + 1u * sizeof(float), 0.0f);
    test_store_f32(model + tail_offset + 2u * sizeof(float), 0.25f);
    test_store_f32(model + tail_offset + 3u * sizeof(float), 0.5f);
    test_store_f32(model + tail_offset + 4u * sizeof(float), -1.0f);
    test_store_f32(model + tail_offset + 5u * sizeof(float), 1.0f);
    test_store_f32(model + tail_offset + 6u * sizeof(float), -1.0f);
    test_store_f32(model + tail_offset + 7u * sizeof(float), 1.0f);
    test_store_f32(model + tail_offset + 8u * sizeof(float), 0.0f);
    test_store_f32(model + tail_offset + 9u * sizeof(float), 0.0f);
    for (size_t index = 10u; index < 16u; ++index) {
        test_store_f32(model + tail_offset + index * sizeof(float), 1.0f);
    }

    float state = 0.0f;
    quantized_runtime_recurrent_descriptor descriptor = {
        1u, &state, 0x1000u, 0x1004u, 0x1008u,
        (uintptr_t)&quantized_runtime_recurrent_execute_target,
    };
    quantized_runtime_model_region region = {model, sizeof(model), 0x1000u};
    float input_data = 0.75f;
    float output_data = 0.0f;
    quantized_runtime_exec_tensor input_tensor = {
        0u, {1u, 1u, 1u}, &input_data,
    };
    quantized_runtime_exec_tensor output_tensor = {
        0u, {1u, 1u, 1u}, &output_data,
    };
    quantized_runtime_exec_tensor *inputs[] = {&input_tensor};
    quantized_runtime_exec_tensor *outputs[] = {&output_tensor};
    uint32_t workspace[16] = {0};
    const size_t workspace_bytes =
        quantized_runtime_recurrent_workspace_bytes(1u, 1u);
    assert(workspace_bytes == 49u);
    assert(quantized_runtime_recurrent_execute(
               &descriptor, &region, inputs, outputs, workspace,
               sizeof(workspace)) == QUANTIZED_RUNTIME_STATUS_OK);
    const float candidate = tanhf(0.5f);
    assert(fabsf(state - 0.5f * candidate) < 1e-6f);
    assert(test_f32_bits(output_data) == test_f32_bits(state));

    assert(quantized_runtime_recurrent_execute(
               &descriptor, &region, inputs, outputs, workspace,
               sizeof(workspace)) == QUANTIZED_RUNTIME_STATUS_OK);
    assert(fabsf(state - 0.75f * candidate) < 1e-6f);

    quantized_runtime_model_region short_region = region;
    short_region.size -= 1u;
    assert(quantized_runtime_recurrent_execute(
               &descriptor, &short_region, inputs, outputs, workspace,
               sizeof(workspace)) == QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_recurrent_execute(
               &descriptor, &region, inputs, outputs, workspace,
               workspace_bytes - 1u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);

    test_store_f32(model + tail_offset + 4u * sizeof(float), -2.0f);
    assert(quantized_runtime_recurrent_execute(
               &descriptor, &region, inputs, outputs, workspace,
               sizeof(workspace)) == QUANTIZED_RUNTIME_RECURRENT_RANGE_ERROR);
}

static void test_goodix_stage_pipelines(void) {
    uint32_t descriptor_tags[5] = {0u, 1u, 2u, 3u, 4u};
    quantized_runtime_five_stage_plan five = {0};
    for (size_t index = 0u; index < 5u; ++index) {
        five.stages[index].descriptor = &descriptor_tags[index];
        five.stages[index].execute = test_stage_execute;
    }
    uint8_t input_data[32] = {0};
    quantized_runtime_exec_tensor input = {
        4u, {1u, 1u, 8u}, input_data,
    };
    quantized_runtime_exec_tensor output = {0};
    uint32_t workspace_words[425] = {0};

    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_five_stage_32_execute(
        &five, &input, &output, workspace_words, sizeof(workspace_words)));
    assert(g_stage_trace.calls == 5u);
    for (size_t index = 0u; index < 5u; ++index) {
        assert(g_stage_trace.descriptors[index] == &descriptor_tags[index]);
    }
    assert(g_stage_trace.outputs[0].dims[1] == 12u);
    assert(g_stage_trace.outputs[0].dims[2] == 32u);
    assert(g_stage_trace.outputs[2].data ==
           (uint8_t *)workspace_words + 0x310u);
    assert(g_stage_trace.outputs[3].data ==
           (uint8_t *)workspace_words + 0x620u);
    assert(output.type_flag == 4u && output.dims[0] == 1u &&
           output.dims[1] == 1u && output.dims[2] == 12u &&
           output.data == workspace_words);
    assert(!quantized_runtime_goodix_five_stage_32_execute(
        &five, &input, &output, workspace_words, 1615u));

    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_five_stage_27_execute(
        &five, &input, &output, workspace_words, sizeof(workspace_words)));
    assert(g_stage_trace.outputs[0].dims[2] == 27u);
    assert(g_stage_trace.outputs[2].data ==
           (uint8_t *)workspace_words + 0x510u);
    assert(g_stage_trace.outputs[3].data ==
           (uint8_t *)workspace_words + 0x540u);

    quantized_runtime_three_stage_plan three = {0};
    for (size_t index = 0u; index < 3u; ++index) {
        three.stages[index].descriptor = &descriptor_tags[index];
        three.stages[index].execute = test_stage_execute;
    }
    three.row_padding = 1u;
    three.column_padding = 2u;
    const uint8_t shape[6] = {2u, 3u, 4u, 5u, 6u, 7u};
    quantized_runtime_exec_tensor auxiliary = {0};
    quantized_runtime_exec_tensor *inputs[2] = {&input, &auxiliary};
    quantized_runtime_exec_tensor *outputs[2] = {&output, &auxiliary};

    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_u8_three_stage_execute(
        &three, inputs, outputs, shape, 20u, workspace_words,
        sizeof(workspace_words)));
    assert(g_stage_trace.calls == 3u);
    assert(g_stage_trace.outputs[0].type_flag == 1u);
    assert(g_stage_trace.outputs[1].data ==
           (uint8_t *)workspace_words + 20u);
    assert(output.dims[1] == 6u && output.dims[2] == 7u &&
           output.data == workspace_words);

    three.middle_uses_input_storage = true;
    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_u8_three_stage_execute(
        &three, inputs, outputs, shape, 20u, workspace_words,
        sizeof(workspace_words)));
    assert(g_stage_trace.outputs[1].data == input.data);

    three.middle_uses_input_storage = false;
    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_f32_three_stage_execute(
        &three, &input, &output, shape, 20u, workspace_words,
        sizeof(workspace_words)));
    assert(g_stage_trace.outputs[0].type_flag == 4u);
    assert(g_stage_trace.outputs[1].data ==
           (uint8_t *)workspace_words + 48u);
    assert(output.type_flag == 4u && output.dims[1] == 6u &&
           output.dims[2] == 7u);
    assert(!quantized_runtime_goodix_f32_three_stage_execute(
        &three, &input, &output, shape, 20u, workspace_words, 167u));

    three.row_padding = 0u;
    three.column_padding = 0u;
    const uint8_t nadt_shape[6] = {1u, 15u, 1u, 15u, 8u, 15u};
    uint8_t nadt_workspace[556] = {0};
    quantized_runtime_exec_tensor nadt_output = {
        4u, {1u, 8u, 15u}, nadt_workspace,
    };
    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_nadt_projection_execute(
        &three, &input, &nadt_output, nadt_shape, sizeof(nadt_workspace)));
    assert(g_stage_trace.calls == 3u);
    assert(g_stage_trace.outputs[0].type_flag == 4u &&
           g_stage_trace.outputs[0].dims[1] == 1u &&
           g_stage_trace.outputs[0].dims[2] == 15u &&
           g_stage_trace.outputs[0].data == nadt_workspace);
    assert(g_stage_trace.outputs[1].dims[1] == 1u &&
           g_stage_trace.outputs[1].dims[2] == 15u &&
           g_stage_trace.outputs[1].data == nadt_workspace + 0x1F0u);
    assert(g_stage_trace.outputs[2].dims[1] == 8u &&
           g_stage_trace.outputs[2].dims[2] == 15u &&
           g_stage_trace.outputs[2].data == nadt_workspace);
    assert(nadt_output.type_flag == 4u && nadt_output.dims[0] == 1u &&
           nadt_output.dims[1] == 8u && nadt_output.dims[2] == 15u &&
           nadt_output.data == nadt_workspace);
    nadt_output.data = nadt_workspace;
    assert(!quantized_runtime_goodix_nadt_projection_execute(
        &three, &input, &nadt_output, nadt_shape,
        sizeof(nadt_workspace) - 1u));
    three.row_padding = 1u;
    nadt_output.data = nadt_workspace;
    assert(!quantized_runtime_goodix_nadt_projection_execute(
        &three, &input, &nadt_output, nadt_shape, sizeof(nadt_workspace)));
}

static void bind_test_stages(quantized_runtime_stage *stages, size_t count,
                             uint32_t *descriptor_tags, size_t tag_offset) {
    for (size_t index = 0u; index < count; ++index) {
        stages[index].descriptor = &descriptor_tags[tag_offset + index];
        stages[index].execute = test_stage_execute;
    }
}

static size_t find_stage_call(const uint32_t *descriptor_tag) {
    for (size_t index = 0u; index < g_stage_trace.calls; ++index) {
        if (g_stage_trace.descriptors[index] == descriptor_tag) {
            return index;
        }
    }
    return g_stage_trace.calls;
}

static void test_goodix_executor_mode(uint32_t mode) {
    enum {
        DIRECT_TAG = 0,
        QUANTIZED_49_TAG = 18,
        QUANTIZED_24_TAG = 21,
        FIVE_27_TAG = 24,
        FIVE_32_TAG = 29,
        FLOAT_12_TAG = 34,
        TAG_COUNT = 37
    };
    uint32_t descriptor_tags[TAG_COUNT];
    for (size_t index = 0u; index < TAG_COUNT; ++index) {
        descriptor_tags[index] = (uint32_t)index;
    }

    quantized_runtime_goodix_executor_plan plan;
    memset(&plan, 0, sizeof(plan));
    plan.mode = mode;
    plan.head_width_mode0 = 8u;
    plan.head_width_other = 8u;
    plan.tail_widths[0] = 8u;
    plan.tail_widths[1] = 6u;
    plan.tail_widths[2] = 4u;
    plan.tail_widths[3] = 2u;
    bind_test_stages(plan.stages,
                     QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT,
                     descriptor_tags, DIRECT_TAG);
    bind_test_stages(plan.quantized_49.stages, 3u, descriptor_tags,
                     QUANTIZED_49_TAG);
    bind_test_stages(plan.quantized_24.stages, 3u, descriptor_tags,
                     QUANTIZED_24_TAG);
    bind_test_stages(plan.five_stage_27.stages, 5u, descriptor_tags,
                     FIVE_27_TAG);
    bind_test_stages(plan.five_stage_32.stages, 5u, descriptor_tags,
                     FIVE_32_TAG);
    bind_test_stages(plan.float_12.stages, 3u, descriptor_tags,
                     FLOAT_12_TAG);

    uint8_t workspace[6000];
    uint8_t tail_input[16];
    uint8_t output[16];
    memset(workspace, 0, sizeof(workspace));
    memset(tail_input, 0xA5, sizeof(tail_input));
    memset(output, 0x5A, sizeof(output));
    quantized_runtime_goodix_executor_io io = {
        workspace, sizeof(workspace), tail_input, sizeof(tail_input),
        output, sizeof(output),
    };
    plan.stages[10].execute = test_remap_stage_execute;
    g_expected_remap_second_data = workspace +
        (mode == 0u ? 0x81Cu : 0xDCCu);
    size_t output_bytes = 99u;
    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_executor_execute(&plan, &io,
                                                     &output_bytes));

    const uint32_t expected_mode0[] = {
        0u, 1u, 2u, 18u, 19u, 20u, 3u, 4u, 21u, 22u, 23u, 5u,
        6u, 7u, 24u, 25u, 26u, 27u, 28u, 8u, 34u, 35u, 36u, 9u,
        10u, 11u, 12u, 13u, 14u, 15u, 16u,
    };
    const uint32_t expected_mode1[] = {
        1u, 2u, 18u, 19u, 20u, 3u, 4u, 21u, 22u, 23u, 5u, 6u,
        7u, 29u, 30u, 31u, 32u, 33u, 8u, 34u, 35u, 36u, 9u, 10u,
        11u, 12u, 13u, 14u, 15u, 16u,
    };
    const uint32_t expected_mode2[] = {
        1u, 2u, 18u, 19u, 20u, 3u, 4u, 21u, 22u, 23u, 5u, 6u,
        7u, 29u, 30u, 31u, 32u, 33u, 8u, 34u, 35u, 36u, 9u, 10u,
        11u, 12u, 13u, 14u, 15u, 16u, 17u,
    };
    const uint32_t *expected = mode == 0u ? expected_mode0 :
        (mode == 1u ? expected_mode1 : expected_mode2);
    const size_t expected_count = mode == 1u ? 30u : 31u;
    assert(g_stage_trace.calls == expected_count);
    for (size_t index = 0u; index < expected_count; ++index) {
        assert(g_stage_trace.descriptors[index] ==
               &descriptor_tags[expected[index]]);
    }

    const size_t expand_call = find_stage_call(&descriptor_tags[1]);
    const size_t reduce_49_call = find_stage_call(&descriptor_tags[2]);
    const size_t quantized_49_call =
        find_stage_call(&descriptor_tags[QUANTIZED_49_TAG]);
    const size_t quantized_24_call =
        find_stage_call(&descriptor_tags[QUANTIZED_24_TAG]);
    const size_t float_12_call =
        find_stage_call(&descriptor_tags[FLOAT_12_TAG]);
    const size_t head_merge_call = find_stage_call(&descriptor_tags[12]);
    assert(expand_call < expected_count && reduce_49_call < expected_count &&
           quantized_49_call < expected_count &&
           quantized_24_call < expected_count &&
           float_12_call < expected_count && head_merge_call < expected_count);
    assert(g_stage_trace.outputs[expand_call].dims[1] ==
           (mode == 0u ? 27u : 32u));
    assert(g_stage_trace.outputs[expand_call].dims[2] == 99u);
    assert(g_stage_trace.outputs[reduce_49_call].dims[2] == 49u);
    assert(g_stage_trace.outputs[quantized_49_call].dims[1] ==
           (mode == 0u ? 14u : 1u));
    assert(g_stage_trace.outputs[quantized_49_call].dims[2] == 49u);
    assert(g_stage_trace.outputs[quantized_24_call].dims[1] ==
           (mode == 0u ? 7u : 2u));
    assert(g_stage_trace.outputs[quantized_24_call].dims[2] == 24u);
    assert(g_stage_trace.outputs[float_12_call].dims[1] ==
           (mode == 0u ? 11u : 1u));
    assert(g_stage_trace.outputs[float_12_call].dims[2] == 12u);
    assert(g_stage_trace.outputs[head_merge_call].dims[1] ==
           (mode == 1u ? 56u : 104u));
    assert(output_bytes == 8u);
    uint8_t expected_output[8] = {0};
    if (mode != 2u) {
        memset(expected_output, 0xA5, sizeof(expected_output));
    }
    assert(memcmp(output, expected_output, sizeof(expected_output)) == 0);

    output_bytes = 99u;
    io.output_capacity = 7u;
    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(!quantized_runtime_goodix_executor_execute(&plan, &io,
                                                      &output_bytes));
    assert(output_bytes == 0u);
    g_expected_remap_second_data = NULL;
}

static void test_goodix_executor(void) {
    test_goodix_executor_mode(0u);
    test_goodix_executor_mode(1u);
    test_goodix_executor_mode(2u);

    uint32_t descriptor_tags[QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT];
    quantized_runtime_goodix_executor_plan plan;
    memset(&plan, 0, sizeof(plan));
    bind_test_stages(plan.stages,
                     QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT,
                     descriptor_tags, 0u);
    uint8_t workspace[6000] = {0};
    uint8_t tail_input[16] = {0};
    uint8_t output[16] = {0};
    quantized_runtime_goodix_executor_io io = {
        workspace, sizeof(workspace), tail_input, sizeof(tail_input),
        output, sizeof(output),
    };
    size_t output_bytes = 99u;
    plan.mode = 3u;
    assert(!quantized_runtime_goodix_executor_execute(&plan, &io,
                                                      &output_bytes));
    assert(output_bytes == 0u);
    plan.mode = 0u;
    io.tail_input_size = 15u;
    assert(!quantized_runtime_goodix_executor_execute(&plan, &io,
                                                      &output_bytes));
    io.tail_input_size = sizeof(tail_input);
    io.workspace_size = 100u;
    assert(!quantized_runtime_goodix_executor_execute(&plan, &io,
                                                      &output_bytes));
    io.workspace_size = sizeof(workspace);
    plan.stages[1].execute = NULL;
    assert(!quantized_runtime_goodix_executor_execute(&plan, &io,
                                                      &output_bytes));
}

static void test_goodix_layer_executor_mode(bool optional_preprocess) {
    uint32_t descriptor_tags[QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT];
    quantized_runtime_goodix_layer_plan plan;
    memset(&plan, 0, sizeof(plan));
    plan.optional_preprocess = optional_preprocess;
    plan.output_min = -1.0f;
    plan.output_max = 1.0f;
    plan.expf_fn = test_expf;
    bind_test_stages(plan.stages,
                     QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT,
                     descriptor_tags, 0u);
    plan.stages[4].execute = test_layer_input_stage_execute;
    plan.stages[7].execute = test_layer_final_stage_execute;

    const uint8_t shape[QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES] = {
        2u, 3u, 2u, 1u, 2u, 1u, 2u, 2u, 1u, 2u, 1u, 2u, 1u, 3u,
    };
    uint32_t workspace_words[64] = {0};
    uint8_t *workspace = (uint8_t *)workspace_words;
    static const int8_t source_values[6] = {-128, -64, 0, 0, 64, 127};
    memcpy(workspace, source_values, sizeof(source_values));
    float input_range_values[2] = {-1.0f, 1.0f};
    float output_range_values[2] = {0.0f, 0.0f};
    uint8_t output_data[8] = {0};
    uint8_t temporary[3] = {0};
    quantized_runtime_exec_tensor input = {
        1u, {1u, 2u, 3u}, workspace,
    };
    quantized_runtime_exec_tensor input_range = {
        4u, {1u, 1u, 2u}, input_range_values,
    };
    quantized_runtime_exec_tensor output = {
        1u, {1u, 1u, 1u}, output_data,
    };
    quantized_runtime_exec_tensor output_range = {
        4u, {1u, 1u, 2u}, output_range_values,
    };
    quantized_runtime_exec_tensor *inputs[2] = {&input, &input_range};
    quantized_runtime_exec_tensor *outputs[2] = {&output, &output_range};
    static const int8_t adjusted_values[6] = {
        -128, -128, -128, -128, -96, -64,
    };
    g_expected_layer_temporary = temporary;
    g_expected_layer_adjusted_data = (const int8_t *)workspace;
    g_expected_layer_adjusted_values = adjusted_values;
    g_expected_layer_adjusted_count = sizeof(adjusted_values);
    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    assert(quantized_runtime_goodix_layer_execute(
        &plan, inputs, outputs, shape, workspace, sizeof(workspace_words),
        temporary, sizeof(temporary)));

    assert(g_stage_trace.calls == (optional_preprocess ? 8u : 7u));
    for (size_t index = 0u; index < g_stage_trace.calls; ++index) {
        const size_t tag = optional_preprocess ? index : index + 1u;
        assert(g_stage_trace.descriptors[index] == &descriptor_tags[tag]);
    }
    const size_t base = optional_preprocess ? 1u : 0u;
    assert(g_stage_trace.outputs[base + 0u].dims[1] == 2u &&
           g_stage_trace.outputs[base + 0u].dims[2] == 1u);
    assert(g_stage_trace.outputs[base + 1u].dims[1] == 2u &&
           g_stage_trace.outputs[base + 1u].dims[2] == 1u);
    assert(g_stage_trace.outputs[base + 2u].type_flag == 4u);
    assert(g_stage_trace.outputs[base + 3u].dims[1] == 2u &&
           g_stage_trace.outputs[base + 3u].dims[2] == 2u);
    assert(g_stage_trace.outputs[base + 4u].dims[1] == 1u &&
           g_stage_trace.outputs[base + 4u].dims[2] == 2u);
    assert(g_stage_trace.outputs[base + 5u].dims[1] == 1u &&
           g_stage_trace.outputs[base + 5u].dims[2] == 2u);
    assert(input_range_values[0] == -1.0f && input_range_values[1] == 1.0f);
    g_expected_layer_temporary = NULL;
    g_expected_layer_adjusted_data = NULL;
    g_expected_layer_adjusted_values = NULL;
    g_expected_layer_adjusted_count = 0u;
}

static void test_goodix_layer_executor(void) {
    test_goodix_layer_executor_mode(false);
    test_goodix_layer_executor_mode(true);

    uint32_t descriptor_tags[QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT];
    quantized_runtime_goodix_layer_plan plan;
    memset(&plan, 0, sizeof(plan));
    bind_test_stages(plan.stages,
                     QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT,
                     descriptor_tags, 0u);
    plan.output_min = -1.0f;
    plan.output_max = 1.0f;
    plan.expf_fn = test_expf;
    const uint8_t shape[QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES] = {
        2u, 3u, 2u, 1u, 2u, 1u, 2u, 2u, 1u, 2u, 1u, 2u, 1u, 3u,
    };
    uint32_t workspace_words[64] = {0};
    uint8_t temporary[3] = {0};
    float ranges[2] = {-1.0f, 1.0f};
    uint8_t output_data[4] = {0};
    quantized_runtime_exec_tensor input = {
        1u, {1u, 2u, 3u}, workspace_words,
    };
    quantized_runtime_exec_tensor range = {4u, {1u, 1u, 2u}, ranges};
    quantized_runtime_exec_tensor output = {
        1u, {1u, 1u, 1u}, output_data,
    };
    quantized_runtime_exec_tensor *inputs[2] = {&input, &range};
    quantized_runtime_exec_tensor *outputs[2] = {&output, &range};
    assert(!quantized_runtime_goodix_layer_execute(
        &plan, inputs, outputs, shape, (uint8_t *)workspace_words,
        sizeof(workspace_words), temporary, 2u));
    assert(!quantized_runtime_goodix_layer_execute(
        &plan, inputs, outputs, shape, (uint8_t *)workspace_words, 5u,
        temporary, sizeof(temporary)));
    input.dims[1] = 1u;
    assert(!quantized_runtime_goodix_layer_execute(
        &plan, inputs, outputs, shape, (uint8_t *)workspace_words,
        sizeof(workspace_words), temporary, sizeof(temporary)));
    input.dims[1] = 2u;
    uint8_t zero_shape[QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES];
    memcpy(zero_shape, shape, sizeof(zero_shape));
    zero_shape[9] = 0u;
    assert(!quantized_runtime_goodix_layer_execute(
        &plan, inputs, outputs, zero_shape, (uint8_t *)workspace_words,
        sizeof(workspace_words), temporary, sizeof(temporary)));
    uint8_t short_logistic[QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES];
    memcpy(short_logistic, shape, sizeof(short_logistic));
    short_logistic[4] = 1u;
    assert(!quantized_runtime_goodix_layer_execute(
        &plan, inputs, outputs, short_logistic, (uint8_t *)workspace_words,
        sizeof(workspace_words), temporary, sizeof(temporary)));
    plan.stages[1].execute = NULL;
    assert(!quantized_runtime_goodix_layer_execute(
        &plan, inputs, outputs, shape, (uint8_t *)workspace_words,
        sizeof(workspace_words), temporary, sizeof(temporary)));
}

static void test_goodix_layer_block_builder(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);
    uint32_t model_words[96];
    for (size_t index = 0u;
            index < sizeof(model_words) / sizeof(model_words[0]); ++index) {
        model_words[index] = UINT32_C(0xA5000000) + (uint32_t)index;
    }
    const uint8_t shape[QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_SHAPE_BYTES] = {
        10u, 2u, 10u, 1u, 1u, 1u, 1u,
    };
    quantized_runtime_goodix_layer_block block;
    size_t consumed = 0u;
    uint32_t end = 0u;
    const uint32_t base = UINT32_C(0x20004000);
    assert(quantized_runtime_goodix_layer_block_build(
        &rt, &block, model_words,
        sizeof(model_words) / sizeof(model_words[0]), base, shape,
        &consumed, &end));
    assert(consumed == 90u && end == base + 90u * 4u);
    static const uint8_t first_header[8] = {
        1u, 1u, 0u, 0u, 10u, 2u, 1u, 1u,
    };
    static const uint8_t fourth_header[8] = {
        3u, 1u, 1u, 1u, 1u, 1u, 1u, 1u,
    };
    assert(memcmp(block.bytes, first_header, sizeof(first_header)) == 0);
    assert(memcmp(block.bytes + 0x54u, fourth_header,
                  sizeof(fourth_header)) == 0);
    assert(test_load_u32(block.bytes + 0x30u) == model_words[46]);
    assert(test_load_u32(block.bytes + 0x34u) == model_words[47]);
    assert(test_load_u32(block.bytes + 0x3Cu + 0x0Cu) == base + 48u * 4u);
    assert(test_load_u32(block.bytes + 0x84u) == 1u);
    assert(test_load_u32(block.bytes + 0xA4u) == model_words[88]);
    assert(test_load_u32(block.bytes + 0xA8u) == model_words[89]);

    uint8_t no_optional_shape[
        QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_SHAPE_BYTES];
    memcpy(no_optional_shape, shape, sizeof(no_optional_shape));
    no_optional_shape[6] = 0u;
    assert(quantized_runtime_goodix_layer_block_build(
        &rt, &block, model_words,
        sizeof(model_words) / sizeof(model_words[0]), base,
        no_optional_shape, &consumed, &end));
    assert(consumed == 79u && end == base + 79u * 4u);
    assert(test_load_u32(block.bytes + 0x84u) == 0u);
    for (size_t index = 0x88u; index < 0xA0u; ++index) {
        assert(block.bytes[index] == 0u);
    }
    assert(test_load_u32(block.bytes + 0xA4u) == model_words[77]);
    assert(test_load_u32(block.bytes + 0xA8u) == model_words[78]);

    memset(&block, 0xA5, sizeof(block));
    consumed = 99u;
    end = 99u;
    assert(!quantized_runtime_goodix_layer_block_build(
        &rt, &block, model_words, 89u, base, shape, &consumed, &end));
    assert(consumed == 0u && end == base);
    for (size_t index = 0u; index < sizeof(block.bytes); ++index) {
        assert(block.bytes[index] == 0u);
    }
    assert(!quantized_runtime_goodix_layer_block_build(
        &rt, &block, model_words,
        sizeof(model_words) / sizeof(model_words[0]), UINT32_MAX - 3u,
        shape, &consumed, &end));
}

static void test_goodix_second_graph_builder(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);
    rt.providers.vector_30534 = (uintptr_t)UINT32_C(0x87654321);
    uint32_t model_words[QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS];
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS;
            ++index) {
        model_words[index] = UINT32_C(0xB6000000) + (uint32_t)index;
    }
    quantized_runtime_goodix_second_graph graph;
    size_t consumed = 0u;
    uint32_t end = 0u;
    const uint32_t base = UINT32_C(0x20008000);
    const uintptr_t release_vector = (uintptr_t)UINT32_C(0x24681357);
    assert(quantized_runtime_goodix_second_graph_build(
        &rt, &graph, model_words,
        QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS, base,
        release_vector, &consumed, &end));
    assert(consumed == QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS);
    assert(end == base +
           QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS * 4u);
    assert(test_load_u32(graph.bytes) == 6u);
    assert(test_load_u32(graph.bytes + 0x004u) == model_words[0]);
    assert(test_load_u32(graph.bytes + 0x008u) == model_words[1]);
    static const uint8_t top_header[8] = {
        5u, 1u, 2u, 2u, 4u, 10u, 1u, 0u,
    };
    assert(memcmp(graph.bytes + 0x010u, top_header,
                  sizeof(top_header)) == 0);
    assert(test_load_u32(graph.bytes + 0x01Cu) == base + 8u);
    assert(test_load_u32(graph.bytes + 0x028u + 0x0Cu) ==
           base + 78u * 4u);
    assert(test_load_u32(graph.bytes + 0x028u + 0x30u) ==
           model_words[124]);
    assert(test_load_u32(graph.bytes + 0x028u + 0x84u) == 1u);
    assert(test_load_u32(graph.bytes + 0x0F0u + 0x84u) == 1u);
    assert(test_load_u32(graph.bytes + 0x1BCu + 0x84u) == 0u);
    assert(test_load_u32(graph.bytes + 0x1A0u) ==
           (uint32_t)release_vector);
    assert(test_load_u32(graph.bytes + 0x3CCu) == UINT32_C(0x00030301));
    assert(test_load_u32(graph.bytes + 0x3D4u) == UINT32_C(0x87654321));

    memset(&graph, 0xA5, sizeof(graph));
    consumed = 99u;
    end = 99u;
    assert(!quantized_runtime_goodix_second_graph_build(
        &rt, &graph, model_words,
        QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS - 1u, base,
        release_vector, &consumed, &end));
    assert(consumed == 0u && end == base);
    assert(!quantized_runtime_goodix_second_graph_build(
        &rt, &graph, model_words,
        QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS,
        UINT32_MAX - 3u, release_vector, &consumed, &end));
}

static void test_goodix_second_executor(void) {
    enum {
        DIRECT_TAG = 0,
        MERGE_TAG = 6,
        LAYER_0_TAG = 10,
        LAYER_1_TAG = 20,
        LAYER_2_TAG = 30,
        LAYER_3_TAG = 40,
        LAYER_4_TAG = 50,
        TAG_COUNT = 58
    };
    uint32_t descriptor_tags[TAG_COUNT];
    for (size_t index = 0u; index < TAG_COUNT; ++index) {
        descriptor_tags[index] = (uint32_t)index;
    }
    quantized_runtime_goodix_second_executor_plan plan;
    memset(&plan, 0, sizeof(plan));
    bind_test_stages(
        plan.stages, QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_STAGE_COUNT,
        descriptor_tags, DIRECT_TAG);
    plan.merge_four.descriptor = &descriptor_tags[MERGE_TAG];
    plan.merge_four.execute = test_merge_four_execute;
    const size_t layer_tags[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT] = {
            LAYER_0_TAG, LAYER_1_TAG, LAYER_2_TAG, LAYER_3_TAG, LAYER_4_TAG,
        };
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT;
            ++index) {
        plan.layers[index].output_min = -1.0f;
        plan.layers[index].output_max = 1.0f;
        plan.layers[index].expf_fn = test_expf;
        bind_test_stages(plan.layers[index].stages,
                         QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT,
                         descriptor_tags, layer_tags[index]);
    }

    uint8_t workspace[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_WORKSPACE_BYTES] = {0};
    uint8_t temporary[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_TEMPORARY_BYTES] = {0};
    uint8_t output[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES];
    memset(output, 0xA5, sizeof(output));
    quantized_runtime_goodix_second_executor_io io = {
        workspace, sizeof(workspace), temporary, sizeof(temporary),
        output, sizeof(output),
    };
    static const uint8_t expected_tags[] = {
        0u, 1u,
        11u, 12u, 13u, 14u, 15u, 16u, 17u,
        2u, 21u, 22u, 23u, 24u, 25u, 26u, 27u,
        2u, 21u, 22u, 23u, 24u, 25u, 26u, 27u,
        2u, 21u, 22u, 23u, 24u, 25u, 26u, 27u,
        6u, 3u,
        31u, 32u, 33u, 34u, 35u, 36u, 37u,
        41u, 42u, 43u, 44u, 45u, 46u, 47u,
        51u, 52u, 53u, 54u, 55u, 56u, 57u,
        4u, 5u, 5u,
    };
    size_t output_bytes = 99u;
    memset(&g_stage_trace, 0, sizeof(g_stage_trace));
    g_expected_second_workspace = workspace;
    assert(quantized_runtime_goodix_second_executor_execute(
        &plan, &io, &output_bytes));
    assert(output_bytes == sizeof(output));
    assert(g_stage_trace.calls == sizeof(expected_tags));
    for (size_t index = 0u; index < sizeof(expected_tags); ++index) {
        assert(g_stage_trace.descriptors[index] ==
               &descriptor_tags[expected_tags[index]]);
    }
    assert(memcmp(output, workspace + 0xF0u, sizeof(output)) == 0);
    const size_t layer_2_input_stage = find_stage_call(&descriptor_tags[34]);
    const size_t layer_3_input_stage = find_stage_call(&descriptor_tags[44]);
    const size_t layer_4_input_stage = find_stage_call(&descriptor_tags[54]);
    assert(layer_2_input_stage < g_stage_trace.calls);
    assert(g_stage_trace.outputs[layer_2_input_stage].dims[1] == 15u);
    assert(g_stage_trace.outputs[layer_2_input_stage].dims[2] == 180u);
    assert(g_stage_trace.outputs[layer_3_input_stage].dims[1] == 16u);
    assert(g_stage_trace.outputs[layer_3_input_stage].dims[2] == 180u);
    assert(g_stage_trace.outputs[layer_4_input_stage].dims[1] == 5u);
    assert(g_stage_trace.outputs[layer_4_input_stage].dims[2] == 180u);

    output_bytes = 99u;
    io.workspace_size = sizeof(workspace) - 1u;
    assert(!quantized_runtime_goodix_second_executor_execute(
        &plan, &io, &output_bytes));
    assert(output_bytes == 0u);
    io.workspace_size = sizeof(workspace);
    io.temporary_size = sizeof(temporary) - 1u;
    assert(!quantized_runtime_goodix_second_executor_execute(
        &plan, &io, &output_bytes));
    io.temporary_size = sizeof(temporary);
    io.output_capacity = sizeof(output) - 1u;
    assert(!quantized_runtime_goodix_second_executor_execute(
        &plan, &io, &output_bytes));
    io.output_capacity = sizeof(output);
    plan.layers[0].optional_preprocess = true;
    assert(!quantized_runtime_goodix_second_executor_execute(
        &plan, &io, &output_bytes));
    plan.layers[0].optional_preprocess = false;
    plan.stages[0].execute = NULL;
    assert(!quantized_runtime_goodix_second_executor_execute(
        &plan, &io, &output_bytes));
    g_expected_second_workspace = NULL;
}

static void test_params_derive(void) {
    static const struct {
        float min_input;
        float max_input;
        float min;
        float max;
        float step;
        float scale;
    } cases[] = {
        /* recovered derivation, validated against the stock instruction
         * stream (float32 exact) */
        {0.0f, 1.0f, 0.0f, 1.0f, 0.003921568859368563f, 255.0f},
        {-1.0f, 1.0f, -1.0f, 1.0078740119934082f, 0.007874015718698502f,
         127.0f},
        {-3.0f, 1.0f, -3.0f, 1.0052356719970703f, 0.015706807374954224f,
         63.666664123535156f},
        {-0.1f, 10.0f, -0.1190476194024086f, 10.0f, 0.039682537317276f,
         25.200000762939453f},
        {2.0f, 5.0f, 0.0f, 5.0f, 0.019607843831181526f, 51.0f},
        {-5.0f, -2.0f, -5.0f, 0.0f, 0.019607843831181526f, 51.0f},
    };
    quantized_runtime rt;
    test_rt_reset(&rt);
    for (size_t index = 0u; index < sizeof(cases) / sizeof(cases[0]);
            ++index) {
        float min = 99.0f;
        float max = 99.0f;
        float step = 99.0f;
        float scale = 99.0f;
        quantized_runtime_quantization_params_derive(
            &rt, cases[index].min_input, cases[index].max_input, &min, &max,
            &step, &scale);
        assert(test_f32_bits(min) == test_f32_bits(cases[index].min));
        assert(test_f32_bits(max) == test_f32_bits(cases[index].max));
        assert(test_f32_bits(step) == test_f32_bits(cases[index].step));
        assert(test_f32_bits(scale) == test_f32_bits(cases[index].scale));
    }
    /* bad arguments / unbound providers: no output is touched. */
    float min = 7.0f;
    float max = 7.0f;
    float step = 7.0f;
    float scale = 7.0f;
    quantized_runtime_quantization_params_derive(NULL, -1.0f, 1.0f, &min,
                                                 &max, &step, &scale);
    quantized_runtime_quantization_params_derive(&rt, -1.0f, 1.0f, NULL,
                                                 &max, &step, &scale);
    quantized_runtime unbound;
    quantized_runtime_initialize(&unbound, NULL);
    quantized_runtime_quantization_params_derive(&unbound, -1.0f, 1.0f, &min,
                                                 &max, &step, &scale);
    assert(test_f32_bits(min) == test_f32_bits(7.0f));
    assert(test_f32_bits(max) == test_f32_bits(7.0f));
    assert(test_f32_bits(step) == test_f32_bits(7.0f));
    assert(test_f32_bits(scale) == test_f32_bits(7.0f));
}

static quantized_runtime_exec_tensor test_exec_tensor(uint32_t dim0,
                                                      uint32_t dim1,
                                                      uint32_t dim2,
                                                      void *data) {
    quantized_runtime_exec_tensor tensor;
    tensor.type_flag = 0u;
    tensor.dims[0] = dim0;
    tensor.dims[1] = dim1;
    tensor.dims[2] = dim2;
    tensor.data = data;
    return tensor;
}

static void test_quantize_executor(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);

    float input_values[] = {-1.0f, -0.5f, 0.0f, 0.5f, 1.0f};
    int8_t output_values[5] = {0, 0, 0, 0, 0};
    float output_range[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor input =
        test_exec_tensor(1u, 1u, 5u, input_values);
    quantized_runtime_exec_tensor output =
        test_exec_tensor(0u, 0u, 0u, output_values);
    quantized_runtime_exec_tensor qparams =
        test_exec_tensor(0u, 0u, 0u, output_range);
    quantized_runtime_exec_tensor *inputs[] = {&input};
    quantized_runtime_exec_tensor *outputs[] = {&output, &qparams};
    const float descriptor[2] = {-1.0f, 1.0f};
    assert(quantized_runtime_float_to_int8_quantize(&rt, descriptor, inputs,
                                                    outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t expected[] = {-128, -64, -1, 63, 126};
    assert(memcmp(output_values, expected, sizeof(expected)) == 0);
    /* the adjusted (integer zero-point) range is stored back, not the raw
     * descriptor range */
    assert(test_f32_bits(output_range[0]) == test_f32_bits(-1.0f));
    assert(test_f32_bits(output_range[1]) ==
           test_f32_bits(1.0078740119934082f));
    assert(output.type_flag == 1u);

    float in_place_values[4] = {0.0f, 0.25f, 0.5f, 1.0f};
    assert(quantized_runtime_goodix_in_place_float_to_int8(
               &rt, 1u, 2u, 2u, in_place_values, 4u) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t expected_in_place[4] = {-128, -64, 0, 127};
    assert(memcmp(in_place_values, expected_in_place,
                  sizeof(expected_in_place)) == 0);

    float untouched_values[2] = {0.25f, 0.75f};
    const float untouched_copy[2] = {0.25f, 0.75f};
    assert(quantized_runtime_goodix_in_place_float_to_int8(
               &rt, 0u, 1u, 2u, untouched_values, 2u) ==
           QUANTIZED_RUNTIME_GOODIX_MODE_ERROR);
    assert(memcmp(untouched_values, untouched_copy,
                  sizeof(untouched_values)) == 0);
    const uint32_t configured_shape[2] = {1u, 2u};
    assert(quantized_runtime_goodix_configured_in_place_float_to_int8(
               &rt, 1u, configured_shape, untouched_values, 2u) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t expected_configured[2] = {-64, 63};
    assert(memcmp(untouched_values, expected_configured,
                  sizeof(expected_configured)) == 0);
    assert(quantized_runtime_goodix_in_place_float_to_int8(
               &rt, 1u, 2u, 2u, in_place_values, 3u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_goodix_configured_in_place_float_to_int8(
               &rt, 1u, NULL, in_place_values, 4u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);

    /* saturation at both rails */
    float sat_values[] = {2.0f, -1.0f, 0.5f};
    int8_t sat_output[3] = {0, 0, 0};
    float sat_range[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor sat_input =
        test_exec_tensor(1u, 1u, 3u, sat_values);
    quantized_runtime_exec_tensor sat_out =
        test_exec_tensor(0u, 0u, 0u, sat_output);
    quantized_runtime_exec_tensor sat_qp =
        test_exec_tensor(0u, 0u, 0u, sat_range);
    quantized_runtime_exec_tensor *sat_inputs[] = {&sat_input};
    quantized_runtime_exec_tensor *sat_outputs[] = {&sat_out, &sat_qp};
    const float sat_descriptor[2] = {0.0f, 1.0f};
    assert(quantized_runtime_float_to_int8_quantize(
               &rt, sat_descriptor, sat_inputs, sat_outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t sat_expected[] = {127, -128, 0};
    assert(memcmp(sat_output, sat_expected, sizeof(sat_expected)) == 0);
    assert(test_f32_bits(sat_range[0]) == test_f32_bits(0.0f));
    assert(test_f32_bits(sat_range[1]) == test_f32_bits(1.0f));

    /* bad arguments */
    assert(quantized_runtime_float_to_int8_quantize(
               NULL, descriptor, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_float_to_int8_quantize(&rt, NULL, inputs,
                                                    outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_float_to_int8_quantize(&rt, descriptor, NULL,
                                                    outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_float_to_int8_quantize(&rt, descriptor, inputs,
                                                    NULL) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    quantized_runtime_exec_tensor no_data = test_exec_tensor(1u, 1u, 1u, NULL);
    quantized_runtime_exec_tensor *bad_inputs[] = {&no_data};
    assert(quantized_runtime_float_to_int8_quantize(&rt, descriptor,
                                                    bad_inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    quantized_runtime unbound;
    quantized_runtime_initialize(&unbound, NULL);
    assert(quantized_runtime_float_to_int8_quantize(&unbound, descriptor,
                                                    inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
}

static void test_int8_add_executor(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);

    /* descriptor: word0 unused, out {min, max} floats at +0x04/+0x08 */
    uint8_t descriptor[12];
    memset(descriptor, 0, sizeof(descriptor));

    int8_t in0_data[] = {10, -128};
    int8_t in1_data[] = {-100, -128};
    float qp0[] = {-1.0f, 1.0f};
    float qp1[] = {0.0f, 2.0f};
    int8_t out_data[2] = {0, 0};
    float out_range[2] = {0.0f, 0.0f};
    float out_min = 0.0f;
    float out_max = 4.0f;
    memcpy(descriptor + 4, &out_min, sizeof(out_min));
    memcpy(descriptor + 8, &out_max, sizeof(out_max));
    quantized_runtime_exec_tensor in0 = test_exec_tensor(0u, 1u, 2u, in0_data);
    quantized_runtime_exec_tensor q0 = test_exec_tensor(0u, 0u, 0u, qp0);
    quantized_runtime_exec_tensor in1 = test_exec_tensor(0u, 1u, 2u, in1_data);
    quantized_runtime_exec_tensor q1 = test_exec_tensor(0u, 0u, 0u, qp1);
    quantized_runtime_exec_tensor out = test_exec_tensor(0u, 1u, 2u, out_data);
    quantized_runtime_exec_tensor oqp = test_exec_tensor(0u, 0u, 0u, out_range);
    quantized_runtime_exec_tensor *inputs[] = {&in0, &q0, &in1, &q1};
    quantized_runtime_exec_tensor *outputs[] = {&out, &oqp};
    assert(quantized_runtime_int8_add_execute(&rt, descriptor, inputs,
                                              outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t expected_a[] = {-109, -128};
    assert(memcmp(out_data, expected_a, sizeof(expected_a)) == 0);
    assert(test_f32_bits(out_range[0]) == test_f32_bits(0.0f));
    assert(test_f32_bits(out_range[1]) == test_f32_bits(4.0f));

    /* signed saturation at both rails (recovered SSAT #8) */
    int8_t sat0[] = {127};
    int8_t sat1[] = {127};
    int8_t sat_out_data[1] = {0};
    float sat_range[2] = {0.0f, 0.0f};
    float one = 1.0f;
    memcpy(descriptor + 8, &one, sizeof(one));
    quantized_runtime_exec_tensor s_in0 = test_exec_tensor(0u, 1u, 1u, sat0);
    quantized_runtime_exec_tensor s_in1 = test_exec_tensor(0u, 1u, 1u, sat1);
    quantized_runtime_exec_tensor s_out =
        test_exec_tensor(0u, 1u, 1u, sat_out_data);
    quantized_runtime_exec_tensor s_qp = test_exec_tensor(0u, 0u, 0u, sat_range);
    quantized_runtime_exec_tensor *s_inputs[] = {&s_in0, &q0, &s_in1, &q1};
    quantized_runtime_exec_tensor *s_outputs[] = {&s_out, &s_qp};
    assert(quantized_runtime_int8_add_execute(&rt, descriptor, s_inputs,
                                              s_outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(sat_out_data[0] == 127);
    sat0[0] = -128;
    sat1[0] = -128;
    assert(quantized_runtime_int8_add_execute(&rt, descriptor, s_inputs,
                                              s_outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(sat_out_data[0] == -128);

    /* mixed vector */
    int8_t mix0[] = {5, -5, 0, 100};
    int8_t mix1[] = {5, 5, 0, -100};
    int8_t mix_out_data[4] = {0, 0, 0, 0};
    float four = 4.0f;
    memcpy(descriptor + 8, &four, sizeof(four));
    quantized_runtime_exec_tensor m_in0 = test_exec_tensor(0u, 1u, 4u, mix0);
    quantized_runtime_exec_tensor m_in1 = test_exec_tensor(0u, 1u, 4u, mix1);
    quantized_runtime_exec_tensor m_out =
        test_exec_tensor(0u, 1u, 4u, mix_out_data);
    quantized_runtime_exec_tensor m_qp = test_exec_tensor(0u, 0u, 0u, sat_range);
    quantized_runtime_exec_tensor *m_inputs[] = {&m_in0, &q0, &m_in1, &q1};
    quantized_runtime_exec_tensor *m_outputs[] = {&m_out, &m_qp};
    assert(quantized_runtime_int8_add_execute(&rt, descriptor, m_inputs,
                                              m_outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t expected_mix[] = {-59, -64, -64, -64};
    assert(memcmp(mix_out_data, expected_mix, sizeof(expected_mix)) == 0);

    /* bad arguments / unbound */
    assert(quantized_runtime_int8_add_execute(NULL, descriptor, inputs,
                                              outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_int8_add_execute(&rt, NULL, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_int8_add_execute(&rt, descriptor, NULL,
                                              outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    quantized_runtime unbound;
    quantized_runtime_initialize(&unbound, NULL);
    assert(quantized_runtime_int8_add_execute(&unbound, descriptor, inputs,
                                              outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
}

static uint8_t expected_i8_conv_value(
    const quantized_runtime_i8_conv1d_descriptor *descriptor,
    const int8_t *input, const int8_t *weights, uint32_t output_channel,
    uint32_t position, int32_t input_zero) {
    const uint32_t input_per_group =
        descriptor->input_channels / descriptor->groups;
    const uint32_t output_per_group =
        descriptor->output_channels / descriptor->groups;
    const uint32_t group = output_channel / output_per_group;
    const uint32_t width = 4u;
    int32_t accumulator = 128;
    const size_t weight_base =
        (size_t)output_channel * input_per_group * descriptor->kernel_width;
    for (uint32_t input_channel = 0u; input_channel < input_per_group;
         ++input_channel) {
        const size_t input_base =
            (size_t)(group * input_per_group + input_channel) * width;
        const size_t weight_row =
            weight_base + (size_t)input_channel * descriptor->kernel_width;
        for (uint32_t kernel = 0u; kernel < descriptor->kernel_width;
             ++kernel) {
            const int32_t source =
                (int32_t)position + (int32_t)kernel -
                (int32_t)descriptor->left_padding;
            const int32_t value =
                (source < 0 || source >= (int32_t)width)
                    ? input_zero
                    : input[input_base + (size_t)source];
            accumulator +=
                (value - input_zero) * weights[weight_row + kernel];
        }
    }
    if (accumulator < 0) {
        accumulator = 0;
    } else if (accumulator > 255) {
        accumulator = 255;
    }
    return (uint8_t)(accumulator - 128);
}

static void test_i8_conv1d_executor(void) {
    static const quantized_runtime_i8_conv1d_descriptor cases[] = {
        {5u, 1u, 2u, 2u, 1u, 2u, 1u, 0u, 0.0f},
        {5u, 1u, 2u, 2u, 4u, 2u, 1u, 0u, 0.0f},
        {3u, 1u, 1u, 1u, 3u, 2u, 1u, 0u, 0.0f},
        {3u, 1u, 1u, 1u, 3u, 3u, 3u, 0u, 0.0f},
        {1u, 1u, 0u, 0u, 1u, 2u, 1u, 0u, 0.0f},
        {1u, 1u, 0u, 0u, 2u, 2u, 1u, 0u, 0.0f},
        {1u, 1u, 0u, 0u, 3u, 2u, 1u, 0u, 0.0f},
        {1u, 1u, 0u, 0u, 4u, 2u, 1u, 0u, 0.0f},
        {1u, 1u, 0u, 0u, 6u, 2u, 1u, 0u, 0.0f},
    };
    int8_t input_data[24];
    int8_t weights[48];
    float channel_scales[3];
    int32_t biases[3];
    uint8_t output_data[12];
    uint8_t expected[12];
    float input_range[2];
    float output_range[2];
    uint8_t workspace[12];

    for (size_t case_index = 0u;
         case_index < sizeof(cases) / sizeof(cases[0]); ++case_index) {
        const quantized_runtime_i8_conv1d_descriptor descriptor =
            cases[case_index];
        const size_t input_count = (size_t)descriptor.input_channels * 4u;
        const size_t output_count = (size_t)descriptor.output_channels * 4u;
        const size_t weight_count =
            (size_t)descriptor.output_channels *
            (descriptor.input_channels / descriptor.groups) *
            descriptor.kernel_width;
        assert(weight_count <= sizeof(weights));
        for (size_t index = 0u; index < input_count; ++index) {
            input_data[index] = (int8_t)((int32_t)(index % 11u) - 5);
        }
        for (size_t index = 0u; index < weight_count; ++index) {
            weights[index] = (int8_t)((int32_t)(index % 5u) - 2);
        }
        for (uint32_t channel = 0u;
             channel < descriptor.output_channels; ++channel) {
            channel_scales[channel] = 1.0f;
            biases[channel] = 128;
        }
        const int32_t input_zero = (case_index == 3u) ? -128 : 0;
        input_range[0] = (case_index == 3u) ? 0.0f : -128.0f;
        input_range[1] = (case_index == 3u) ? 255.0f : 127.0f;
        output_range[0] = -1.0f;
        output_range[1] = -1.0f;
        memset(output_data, 0xA5, sizeof(output_data));
        for (uint32_t output_channel = 0u;
             output_channel < descriptor.output_channels; ++output_channel) {
            for (uint32_t position = 0u; position < 4u; ++position) {
                expected[(size_t)output_channel * 4u + position] =
                    expected_i8_conv_value(&descriptor, input_data, weights,
                                           output_channel, position,
                                           input_zero);
            }
        }

        quantized_runtime_i8_conv1d_model model = {
            weights, weight_count, -128.0f, 127.0f,
            channel_scales, descriptor.output_channels,
            biases, descriptor.output_channels,
            0.0f, 0.00000011920928955078125f, 0.0f, 255.0f,
        };
        quantized_runtime_exec_tensor input = {
            1u, {1u, descriptor.input_channels, 4u}, input_data,
        };
        quantized_runtime_exec_tensor input_params = {
            0u, {1u, 1u, 2u}, input_range,
        };
        quantized_runtime_exec_tensor output = {
            1u, {1u, descriptor.output_channels, 4u}, output_data,
        };
        quantized_runtime_exec_tensor output_params = {
            0u, {1u, 1u, 2u}, output_range,
        };
        quantized_runtime_i8_conv1d_io io = {
            &input, &input_params, &output, &output_params,
            input_count, sizeof(input_range), output_count,
            sizeof(output_range), workspace, sizeof(workspace),
        };
        assert(quantized_runtime_i8_conv1d_workspace_bytes(
                   &descriptor, 4u) == output_count);
        assert(quantized_runtime_i8_conv1d_execute(
                   &descriptor, &model, &io) == QUANTIZED_RUNTIME_STATUS_OK);
        assert(memcmp(output_data, expected, output_count) == 0);
        assert(test_f32_bits(output_range[0]) == test_f32_bits(0.0f));
        assert(test_f32_bits(output_range[1]) == test_f32_bits(255.0f));
    }

    /* Exact in-place overlap is rejected without scratch and succeeds with
     * caller-owned output scratch, leaving the final bytes at the requested
     * output address. */
    const quantized_runtime_i8_conv1d_descriptor descriptor =
        cases[4];
    const int8_t overlap_weights[2] = {1, -1};
    const float overlap_scales[2] = {1.0f, 1.0f};
    const int32_t overlap_biases[2] = {128, 128};
    quantized_runtime_i8_conv1d_model model = {
        overlap_weights, 2u, -128.0f, 127.0f,
        overlap_scales, 2u, overlap_biases, 2u,
        0.0f, 0.00000011920928955078125f, 0.0f, 255.0f,
    };
    int8_t overlap[8] = {-3, -2, -1, 0, 0, 0, 0, 0};
    quantized_runtime_exec_tensor input = {1u, {1u, 1u, 4u}, overlap};
    quantized_runtime_exec_tensor input_params = {
        0u, {1u, 1u, 2u}, input_range,
    };
    quantized_runtime_exec_tensor output = {1u, {1u, 2u, 4u}, overlap};
    quantized_runtime_exec_tensor output_params = {
        0u, {1u, 1u, 2u}, output_range,
    };
    input_range[0] = -128.0f;
    input_range[1] = 127.0f;
    quantized_runtime_i8_conv1d_io io = {
        &input, &input_params, &output, &output_params,
        4u, sizeof(input_range), 8u, sizeof(output_range), NULL, 0u,
    };
    assert(quantized_runtime_i8_conv1d_execute(
               &descriptor, &model, &io) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    io.workspace = workspace;
    io.workspace_size = 8u;
    assert(quantized_runtime_i8_conv1d_execute(
               &descriptor, &model, &io) == QUANTIZED_RUNTIME_STATUS_OK);
    for (uint32_t position = 0u; position < 4u; ++position) {
        assert((uint8_t)overlap[position] ==
               expected_i8_conv_value(&descriptor, (const int8_t[]){-3,-2,-1,0},
                                      overlap_weights, 0u, position, 0));
        assert((uint8_t)overlap[4u + position] ==
               expected_i8_conv_value(&descriptor, (const int8_t[]){-3,-2,-1,0},
                                      overlap_weights, 1u, position, 0));
    }

    quantized_runtime_i8_conv1d_descriptor unsupported = cases[0];
    unsupported.input_channels = 2u;
    input.dims[1] = 2u;
    output.data = output_data;
    output.dims[1] = 2u;
    io.input_capacity = 8u;
    io.output_capacity = 8u;
    io.workspace = workspace;
    assert(quantized_runtime_i8_conv1d_execute(
               &unsupported, &model, &io) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_i8_conv1d_workspace_bytes(NULL, 4u) == 0u);
}

static void test_float_dense_executor(void) {
    const float input_data[3] = {1.0f, -2.0f, 0.5f};
    const float weights[6] = {1.0f, 2.0f, 3.0f,
                              -1.0f, 0.5f, 2.0f};
    const float biases[2] = {0.25f, -0.5f};
    quantized_runtime_float_dense_model model = {
        weights, 6u, biases, 2u,
    };
    float output_data[2] = {0.0f, 0.0f};
    float workspace[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor input = {
        0u, {1u, 1u, 3u}, (void *)input_data,
    };
    quantized_runtime_exec_tensor output = {
        0u, {1u, 1u, 2u}, output_data,
    };
    quantized_runtime_float_dense_io io = {
        &input, &output, sizeof(input_data), sizeof(output_data),
        workspace, sizeof(workspace),
    };
    quantized_runtime_float_dense_descriptor descriptor = {
        2u, 0xA5u, 0u, 0.1f,
    };
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) == QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(output_data[0]) == test_f32_bits(-1.25f));
    assert(test_f32_bits(output_data[1]) == test_f32_bits(-1.5f));

    descriptor.activation = 1u;
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) == QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(output_data[0]) ==
           test_f32_bits(-1.25f * descriptor.alpha));
    assert(test_f32_bits(output_data[1]) ==
           test_f32_bits(-1.5f * descriptor.alpha));

    descriptor.activation = 2u;
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) == QUANTIZED_RUNTIME_STATUS_OK);
    assert(fabsf(output_data[0] - 1.0f / (1.0f + expf(1.25f))) < 1e-7f);
    assert(fabsf(output_data[1] - 1.0f / (1.0f + expf(1.5f))) < 1e-7f);

    /* The recovered raw-bit cap limits expf to 88 for sufficiently negative
     * logits. */
    const float zero_weights[3] = {0.0f, 0.0f, 0.0f};
    const float cap_bias[1] = {-100.0f};
    model.weights = zero_weights;
    model.weight_count = 3u;
    model.biases = cap_bias;
    model.bias_count = 1u;
    descriptor.output_count = 1u;
    output.dims[2] = 1u;
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) == QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(output_data[0]) ==
           test_f32_bits(1.0f / (1.0f + expf(88.0f))));

    /* Overlapping source/output storage requires explicit scratch. */
    float overlap[3] = {1.0f, -2.0f, 0.5f};
    input.data = overlap;
    output.data = overlap;
    output.dims[2] = 2u;
    descriptor.output_count = 2u;
    descriptor.activation = 0u;
    model.weights = weights;
    model.weight_count = 6u;
    model.biases = biases;
    model.bias_count = 2u;
    io.input_capacity = sizeof(overlap);
    io.output_capacity = 2u * sizeof(float);
    io.workspace = NULL;
    io.workspace_size = 0u;
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    io.workspace = workspace;
    io.workspace_size = sizeof(workspace);
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) == QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(overlap[0]) == test_f32_bits(-1.25f));
    assert(test_f32_bits(overlap[1]) == test_f32_bits(-1.5f));

    descriptor.activation = 3u;
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    descriptor.activation = 0u;
    model.weight_count = 5u;
    assert(quantized_runtime_float_dense_execute(
               &descriptor, &model, &io) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_float_dense_execute(NULL, &model, &io) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
}

static void test_pooling_executor(void) {
    /* window-2 maximum, two rows, signed values */
    int8_t input_data[] = {1, 5, 3, 2, 7, 4, 6, 0, -5, -2, -9, -1, 0, 0, -3, -4};
    int8_t output_data[8];
    memset(output_data, 0x55, sizeof(output_data));
    quantized_runtime_exec_tensor input =
        test_exec_tensor(0u, 0u, 8u, input_data);
    quantized_runtime_exec_tensor output =
        test_exec_tensor(0u, 2u, 4u, output_data);
    quantized_runtime_exec_tensor *inputs[] = {&input};
    quantized_runtime_exec_tensor *outputs[] = {&output};
    const uint8_t desc_max2[] = {0u, 2u, 2u};
    assert(quantized_runtime_pooling_execute(desc_max2, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t expected_max2[] = {5, 3, 7, 6, -2, -1, 0, -3};
    assert(memcmp(output_data, expected_max2, sizeof(expected_max2)) == 0);

    /* window-4 maximum */
    int8_t in4[] = {1, 9, 2, 8, 5, 3, 7, 6};
    int8_t out4[2];
    memset(out4, 0x55, sizeof(out4));
    quantized_runtime_exec_tensor input4 = test_exec_tensor(0u, 0u, 8u, in4);
    quantized_runtime_exec_tensor output4 = test_exec_tensor(0u, 1u, 2u, out4);
    quantized_runtime_exec_tensor *inputs4[] = {&input4};
    quantized_runtime_exec_tensor *outputs4[] = {&output4};
    const uint8_t desc_max4[] = {0u, 4u, 4u};
    assert(quantized_runtime_pooling_execute(desc_max4, inputs4, outputs4) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const int8_t expected_max4[] = {9, 7};
    assert(memcmp(out4, expected_max4, sizeof(expected_max4)) == 0);

    /* window-3 average with sign-aware half rounding */
    int8_t in_avg[] = {3, 0, -3, 10, -10, 5, -1, -1, -1, -5, 0, 0};
    int8_t out_avg[4];
    memset(out_avg, 0x55, sizeof(out_avg));
    quantized_runtime_exec_tensor input_avg =
        test_exec_tensor(0u, 0u, 12u, in_avg);
    quantized_runtime_exec_tensor output_avg =
        test_exec_tensor(0u, 1u, 4u, out_avg);
    quantized_runtime_exec_tensor *inputs_avg[] = {&input_avg};
    quantized_runtime_exec_tensor *outputs_avg[] = {&output_avg};
    const uint8_t desc_avg[] = {1u, 3u, 3u};
    assert(quantized_runtime_pooling_execute(desc_avg, inputs_avg,
                                             outputs_avg) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    /* sums 0, 5, -3, -5 -> 0, 2, -1, -2 */
    static const int8_t expected_avg[] = {0, 2, -1, -2};
    assert(memcmp(out_avg, expected_avg, sizeof(expected_avg)) == 0);

    /* unsupported descriptors are a silent no-op returning zero (recovered):
     * the output buffer is untouched. */
    static const uint8_t unsupported[][3] = {
        {2u, 2u, 2u}, {0u, 3u, 1u}, {1u, 2u, 3u}, {0u, 1u, 1u}, {1u, 4u, 1u},
    };
    for (size_t index = 0u; index < sizeof(unsupported) / sizeof(unsupported[0]);
            ++index) {
        memset(output_data, 0x55, sizeof(output_data));
        assert(quantized_runtime_pooling_execute(unsupported[index], inputs,
                                                 outputs) ==
               QUANTIZED_RUNTIME_STATUS_OK);
        static const int8_t untouched[8] = {
            0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55};
        assert(memcmp(output_data, untouched, sizeof(untouched)) == 0);
    }

    /* bad arguments */
    assert(quantized_runtime_pooling_execute(NULL, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_pooling_execute(desc_max2, NULL, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_pooling_execute(desc_max2, inputs, NULL) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
}

static void test_softmax_executor(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);

    float input_values[] = {1.0f, 2.0f, 3.0f};
    float output_values[3] = {0.0f, 0.0f, 0.0f};
    quantized_runtime_exec_tensor input =
        test_exec_tensor(0u, 0u, 0u, input_values);
    quantized_runtime_exec_tensor output =
        test_exec_tensor(0u, 3u, 0u, output_values); /* count from dims[1] */
    quantized_runtime_exec_tensor *inputs[] = {&input};
    quantized_runtime_exec_tensor *outputs[] = {&output};
    assert(quantized_runtime_float_softmax_execute(&rt, NULL, inputs,
                                                   outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    static const float expected[] = {0.09003057f, 0.24472848f, 0.66524094f};
    for (size_t index = 0u; index < 3u; ++index) {
        const float delta = fabsf(output_values[index] - expected[index]);
        assert(delta < 1e-6f);
    }

    /* uniform input */
    float uniform[] = {5.0f, 5.0f};
    float uniform_out[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor u_in = test_exec_tensor(0u, 0u, 0u, uniform);
    quantized_runtime_exec_tensor u_out =
        test_exec_tensor(0u, 2u, 0u, uniform_out);
    quantized_runtime_exec_tensor *u_inputs[] = {&u_in};
    quantized_runtime_exec_tensor *u_outputs[] = {&u_out};
    assert(quantized_runtime_float_softmax_execute(&rt, NULL, u_inputs,
                                                   u_outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(uniform_out[0]) == test_f32_bits(0.5f));
    assert(test_f32_bits(uniform_out[1]) == test_f32_bits(0.5f));

    /* recovered quirk: a NaN input takes the 88.0f cap path (its raw bits
     * pass the signed cap check), so expf(88) dominates the sum. */
    float nan_input[] = {nanf(""), 1.0f};
    float nan_out[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor n_in = test_exec_tensor(0u, 0u, 0u, nan_input);
    quantized_runtime_exec_tensor n_out = test_exec_tensor(0u, 2u, 0u, nan_out);
    quantized_runtime_exec_tensor *n_inputs[] = {&n_in};
    quantized_runtime_exec_tensor *n_outputs[] = {&n_out};
    assert(quantized_runtime_float_softmax_execute(&rt, NULL, n_inputs,
                                                   n_outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(nan_out[0]) == test_f32_bits(1.0f));
    assert(nan_out[1] >= 0.0f && nan_out[1] < 1e-37f);

    /* bad arguments / unbound expf */
    assert(quantized_runtime_float_softmax_execute(NULL, NULL, inputs,
                                                   outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_float_softmax_execute(&rt, NULL, NULL, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    quantized_runtime unbound;
    quantized_runtime_initialize(&unbound, NULL);
    assert(quantized_runtime_float_softmax_execute(&unbound, NULL, inputs,
                                                   outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
}

static void test_float_add_executor(void) {
    float input0[] = {1.5f, -2.0f, 3.0f};
    float input1[] = {0.5f, 2.0f, -3.5f};
    float output[3] = {0.0f, 0.0f, 0.0f};
    quantized_runtime_exec_tensor in0 = test_exec_tensor(0u, 3u, 1u, input0);
    quantized_runtime_exec_tensor in1 = test_exec_tensor(0u, 3u, 1u, input1);
    quantized_runtime_exec_tensor out = test_exec_tensor(0u, 3u, 1u, output);
    quantized_runtime_exec_tensor *inputs[] = {&in0, &in1};
    quantized_runtime_exec_tensor *outputs[] = {&out};

    uint8_t descriptor[8];
    memset(descriptor, 0, sizeof(descriptor));

    /* type 0: plain add, no activation */
    assert(quantized_runtime_float_add_execute(descriptor, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(output[0]) == test_f32_bits(2.0f));
    assert(test_f32_bits(output[1]) == test_f32_bits(0.0f));
    assert(test_f32_bits(output[2]) == test_f32_bits(-0.5f));

    /* type 1, alpha 0.0f: ReLU */
    descriptor[0] = 1u;
    assert(quantized_runtime_float_add_execute(descriptor, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(output[2]) == test_f32_bits(0.0f));

    /* type 1, alpha 0.1f: leaky ReLU on negatives */
    float alpha = 0.1f;
    memcpy(descriptor + 4, &alpha, sizeof(alpha));
    assert(quantized_runtime_float_add_execute(descriptor, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(output[0]) == test_f32_bits(2.0f));
    assert(test_f32_bits(output[2]) ==
           test_f32_bits(-0.05000000074505806f));

    /* type 2: no activation */
    descriptor[0] = 2u;
    assert(quantized_runtime_float_add_execute(descriptor, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(test_f32_bits(output[2]) == test_f32_bits(-0.5f));

    /* bad arguments */
    assert(quantized_runtime_float_add_execute(NULL, inputs, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_float_add_execute(descriptor, NULL, outputs) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_float_add_execute(descriptor, inputs, NULL) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
}

static void test_descriptor_constructors(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);

    /* 0x00074C98: 16-byte operator descriptor; the executor vector is the
     * reconstructed in-family float-add executor. */
    uintptr_t op_descriptor[4] = {1u, 1u, 1u, 1u};
    quantized_runtime_operator_descriptor_init(op_descriptor, 0x123u, 2.5f);
    assert(op_descriptor[0] == 0x23u);
    assert(op_descriptor[1] == 0x40200000u);
    assert(op_descriptor[2] == 0u);
    assert(op_descriptor[3] ==
           (uintptr_t)&quantized_runtime_float_add_execute);
    quantized_runtime_operator_descriptor_init(NULL, 0x123u, 2.5f);

    /* 0x00074CDC: in-family softmax executor vector. */
    assert(quantized_runtime_softmax_executor_vector() ==
           (uintptr_t)&quantized_runtime_float_softmax_execute);

    /* 0x00074CE4: quantizer descriptor, default and cursor-driven. */
    uintptr_t quant_descriptor[3] = {1u, 1u, 1u};
    quantized_runtime_quantizer_descriptor_construct(quant_descriptor, NULL);
    assert(quant_descriptor[0] == 0u);
    assert(quant_descriptor[1] == 0x3F800000u);
    assert(quant_descriptor[2] ==
           (uintptr_t)&quantized_runtime_float_to_int8_quantize);
    const uint32_t range_words[] = {0xC0000000u, 0x40400000u};
    const uint32_t *cursor = range_words;
    quantized_runtime_quantizer_descriptor_construct(quant_descriptor,
                                                     &cursor);
    assert(quant_descriptor[0] == 0xC0000000u);
    assert(quant_descriptor[1] == 0x40400000u);
    assert(cursor == range_words + 2);

    /* 0x00074A9C / 0x00074BD8: out-of-family executor vectors are bound
     * tokens; zero when unbound. */
    assert(quantized_runtime_executor_vector_95b20(&rt) == 0u);
    assert(quantized_runtime_executor_vector_36dcc(&rt) == 0u);
    assert(quantized_runtime_executor_vector_95b20(NULL) == 0u);
    quantized_runtime_providers bound_providers = test_providers;
    bound_providers.vector_95b20 = (uintptr_t)0x00095B21u;
    bound_providers.vector_36dcc = (uintptr_t)0x00036DCDu;
    bound_providers.run_76bdc = (uintptr_t)0x00076BDDu;
    bound_providers.vector_30534 = (uintptr_t)0x00030535u;
    quantized_runtime bound;
    quantized_runtime_initialize(&bound, &bound_providers);
    assert(quantized_runtime_executor_vector_95b20(&bound) ==
           (uintptr_t)0x00095B21u);
    assert(quantized_runtime_executor_vector_36dcc(&bound) ==
           (uintptr_t)0x00036DCDu);
    assert(quantized_runtime_executor_vector_30534(&rt) == 0u);
    assert(quantized_runtime_executor_vector_30534(NULL) == 0u);
    assert(quantized_runtime_executor_vector_30534(&bound) ==
           (uintptr_t)0x00030535u);

    /* 0x00074AAC: 24-byte descriptor constructor. */
    uint8_t record[0x18];
    memset(record, 0xAA, sizeof(record));
    uint32_t arena_cursor = 0x1000u;
    quantized_runtime_descriptor_construct(
        &rt, record, 2u, 1u, 3u, 4u, 8u, 6u, 2u, 0xDEADBEEFu, 7u,
        &arena_cursor, 2.5f);
    static const uint8_t expected_prefix[] = {2u, 1u, 3u, 4u, 8u, 6u, 2u, 7u};
    assert(memcmp(record, expected_prefix, sizeof(expected_prefix)) == 0);
    uint32_t word;
    memcpy(&word, record + 8, sizeof(word));
    assert(word == 0x40200000u); /* 2.5f */
    memcpy(&word, record + 0x0C, sizeof(word));
    assert(word == 0x1000u);
    memcpy(&word, record + 0x10, sizeof(word));
    assert(word == 0x10C0u); /* 0x1000 + 6*2*(8/2)*4 */
    memcpy(&word, record + 0x14, sizeof(word));
    assert(word == 0u); /* unbound run token */
    assert(arena_cursor == 0x10D8u); /* 0x1000 + 6*4 + 192 */

    /* recovered udiv-by-zero quirk: byte6 == 0 yields ratio 0 */
    arena_cursor = 0x1000u;
    quantized_runtime_descriptor_construct(&rt, record, 2u, 1u, 3u, 4u, 8u,
                                           6u, 0u, 0u, 7u, &arena_cursor,
                                           2.5f);
    memcpy(&word, record + 0x10, sizeof(word));
    assert(word == 0x1000u);
    assert(arena_cursor == 0x1000u + 24u);

    /* bound run token lands at +0x14 */
    arena_cursor = 0x1000u;
    quantized_runtime_descriptor_construct(&bound, record, 2u, 1u, 3u, 4u,
                                           8u, 6u, 2u, 0u, 7u, &arena_cursor,
                                           2.5f);
    memcpy(&word, record + 0x14, sizeof(word));
    assert(word == 0x00076BDDu);
    quantized_runtime_descriptor_construct(&rt, NULL, 2u, 1u, 3u, 4u, 8u, 6u,
                                           2u, 0u, 7u, &arena_cursor, 2.5f);

    /* 0x00074BE0: 24-byte descriptor record constructor. */
    memset(record, 0xAA, sizeof(record));
    arena_cursor = 0x2000u;
    quantized_runtime_descriptor_record_construct(&rt, record, 3u, 5u, 0xAAu,
                                                  0xBBu, &arena_cursor, -1.5f);
    memcpy(&word, record + 0x00, sizeof(word));
    assert(word == 5u);
    assert(record[4] == 0xAAu);
    assert(record[5] == 0xBBu);
    memcpy(&word, record + 8, sizeof(word));
    assert(word == 0xBFC00000u); /* -1.5f */
    memcpy(&word, record + 0x0C, sizeof(word));
    assert(word == 0x2000u);
    memcpy(&word, record + 0x10, sizeof(word));
    assert(word == 0x203Cu); /* 0x2000 + 3*5*4 */
    memcpy(&word, record + 0x14, sizeof(word));
    assert(word ==
           (uint32_t)(uintptr_t)&quantized_runtime_float_dense_execute_target);
    assert(arena_cursor == 0x2050u); /* 0x2000 + 5*4 + 60 */
    arena_cursor = 0x2000u;
    quantized_runtime_descriptor_record_construct(&bound, record, 3u, 5u,
                                                  0xAAu, 0xBBu, &arena_cursor,
                                                  -1.5f);
    memcpy(&word, record + 0x14, sizeof(word));
    assert(word ==
           (uint32_t)(uintptr_t)&quantized_runtime_float_dense_execute_target);
    quantized_runtime_descriptor_record_construct(&rt, NULL, 3u, 5u, 0xAAu,
                                                  0xBBu, &arena_cursor, -1.5f);

    /* 0x00074A20: Goodix recurrent descriptor and exact arena partition. */
    recurrent_allocation_trace recurrent_trace = {0u, 0u, 0, 0u, 0u};
    quantized_runtime_recurrent_descriptor recurrent;
    memset(&recurrent, 0xAA, sizeof(recurrent));
    arena_cursor = 0x4001u;
    assert(quantized_runtime_recurrent_layer_descriptor_construct(
        &bound, &recurrent, 5u, 7u, &arena_cursor,
        test_recurrent_allocate, &recurrent_trace));
    assert(recurrent_trace.calls == 1u);
    assert(recurrent_trace.last_bytes == 20u);
    assert(recurrent.units == 5u);
    assert(recurrent.state != NULL);
    for (uint32_t index = 0u; index < 5u; ++index) {
        assert(test_f32_bits(recurrent.state[index]) == 0u);
    }
    assert(recurrent.input_weights_offset == 0x4001u);
    assert(recurrent.recurrent_weights_offset == 0x406Du);
    assert(recurrent.bias_offset == 0x40B9u);
    assert(recurrent.execute ==
           (uintptr_t)&quantized_runtime_recurrent_execute_target);
    assert(arena_cursor == 0x4199u);
    free(recurrent.state);

    recurrent_trace.fail = 1;
    arena_cursor = 0x5000u;
    memset(&recurrent, 0xAA, sizeof(recurrent));
    assert(!quantized_runtime_recurrent_layer_descriptor_construct(
        &bound, &recurrent, 4u, 3u, &arena_cursor,
        test_recurrent_allocate, &recurrent_trace));
    assert(recurrent.units == 4u);
    assert(recurrent.state == NULL);
    assert(recurrent.input_weights_offset == 0u);
    assert(recurrent.execute == 0u);
    assert(arena_cursor == 0x5000u);

    /* Checked target-offset overflow fails before allocation. */
    recurrent_trace.fail = 0;
    recurrent_trace.calls = 0u;
    arena_cursor = UINT32_MAX - 4u;
    assert(!quantized_runtime_recurrent_layer_descriptor_construct(
        &bound, &recurrent, 2u, 2u, &arena_cursor,
        test_recurrent_allocate, &recurrent_trace));
    assert(recurrent_trace.calls == 0u);
    assert(arena_cursor == UINT32_MAX - 4u);

    /* 0x0004387C: fixed Goodix graph schema over 439 model words. */
    uint32_t model_words[QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS];
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS; ++index) {
        model_words[index] = UINT32_C(0xA0000000) + (uint32_t)index;
    }
    quantized_runtime_goodix_graph graph;
    memset(&graph, 0xAA, sizeof(graph));
    size_t consumed_words = 0u;
    uint32_t model_end_address = 0u;
    assert(quantized_runtime_goodix_graph_build(
        &bound, &graph, model_words,
        QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS, 0x6000u,
        &consumed_words, &model_end_address));
    assert(consumed_words == QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS);
    assert(model_end_address == 0x66DCu);
    uint32_t graph_word;
    memcpy(&graph_word, graph.bytes + 0x000u, sizeof(graph_word));
    assert(graph_word == model_words[0]);
    memcpy(&graph_word, graph.bytes + 0x004u, sizeof(graph_word));
    assert(graph_word == model_words[1]);
    memcpy(&graph_word, graph.bytes + 0x008u, sizeof(graph_word));
    assert(graph_word ==
           (uint32_t)(uintptr_t)&quantized_runtime_float_to_int8_quantize);
    static const uint8_t graph_first_aligned_prefix[] = {
        5u, 1u, 2u, 2u, 1u, 16u, 1u, 0u,
    };
    assert(memcmp(graph.bytes + 0x00Cu, graph_first_aligned_prefix,
                  sizeof(graph_first_aligned_prefix)) == 0);
    memcpy(&graph_word, graph.bytes + 0x018u, sizeof(graph_word));
    assert(graph_word == 0x6008u);
    memcpy(&graph_word, graph.bytes + 0x01Cu, sizeof(graph_word));
    assert(graph_word == 0x60A0u);
    memcpy(&graph_word, graph.bytes + 0x020u, sizeof(graph_word));
    assert(graph_word ==
           (uint32_t)(uintptr_t)&quantized_runtime_i8_conv1d_execute_target);
    memcpy(&graph_word, graph.bytes + 0x024u, sizeof(graph_word));
    assert(graph_word == 0x00020200u);
    memcpy(&graph_word, graph.bytes + 0x028u, sizeof(graph_word));
    assert(graph_word ==
           (uint32_t)(uintptr_t)&quantized_runtime_pooling_execute);
    memcpy(&graph_word, graph.bytes + 0x074u, sizeof(graph_word));
    assert(graph_word == 0u);
    memcpy(&graph_word, graph.bytes + 0x078u, sizeof(graph_word));
    assert(graph_word == model_words[161]);
    memcpy(&graph_word, graph.bytes + 0x07Cu, sizeof(graph_word));
    assert(graph_word == model_words[162]);
    memcpy(&graph_word, graph.bytes + 0x080u, sizeof(graph_word));
    assert(graph_word ==
           (uint32_t)(uintptr_t)&quantized_runtime_int8_add_execute);
    memcpy(&graph_word, graph.bytes + 0x0D8u, sizeof(graph_word));
    assert(graph_word == model_words[264]);
    memcpy(&graph_word, graph.bytes + 0x0DCu, sizeof(graph_word));
    assert(graph_word == model_words[265]);
    memcpy(&graph_word, graph.bytes + 0x0ECu, sizeof(graph_word));
    assert(graph_word == 0x00030535u);
    static const uint8_t graph_first_descriptor_prefix[] = {
        1u, 1u, 0u, 0u, 16u, 1u, 1u, 1u,
    };
    assert(memcmp(graph.bytes + 0x108u, graph_first_descriptor_prefix,
                  sizeof(graph_first_descriptor_prefix)) == 0);
    memcpy(&graph_word, graph.bytes + 0x114u, sizeof(graph_word));
    assert(graph_word == 0x6428u); /* base + 266 model words */
    memcpy(&graph_word, graph.bytes + 0x150u, sizeof(graph_word));
    assert(graph_word == 1u);
    memcpy(&graph_word, graph.bytes + 0x15Cu, sizeof(graph_word));
    assert(graph_word ==
           (uint32_t)(uintptr_t)&quantized_runtime_float_add_execute);

    assert(!quantized_runtime_goodix_graph_build(
        &bound, &graph, model_words,
        QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS - 1u, 0x6000u,
        NULL, NULL));
    assert(!quantized_runtime_goodix_graph_build(
        &bound, &graph, model_words,
        QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS, 0x6002u,
        NULL, NULL));
    assert(!quantized_runtime_goodix_graph_build(
        &bound, &graph, model_words,
        QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS, UINT32_MAX - 3u,
        NULL, NULL));

    /* 0x00036C26/0x00099014: complete two-graph model instance. */
    uint32_t instance_model_words[
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS];
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS;
            ++index) {
        instance_model_words[index] =
            UINT32_C(0xB0000000) + (uint32_t)index;
    }
    recurrent_allocation_trace instance_trace = {0};
    quantized_runtime_goodix_model_instance *instance = NULL;
    consumed_words = 0u;
    model_end_address = 0u;
    assert(quantized_runtime_goodix_model_instance_create(
        &bound, &instance, instance_model_words,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x8000u,
        test_recurrent_allocate, test_recurrent_release, &instance_trace,
        &consumed_words, &model_end_address));
    assert(instance != NULL);
    assert(instance_trace.calls == 2u); /* outer instance + recurrent state */
    assert(instance_trace.last_bytes == 16u * sizeof(float));
    assert(instance_trace.releases == 0u);
    assert(consumed_words ==
           QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS);
    assert(model_end_address == 0xBD50u);
    assert(instance->reserved_000 == 0u);
    memcpy(&graph_word, instance->graph_a.bytes, sizeof(graph_word));
    assert(graph_word == instance_model_words[0]);
    memcpy(&graph_word, instance->graph_b.bytes, sizeof(graph_word));
    assert(graph_word == instance_model_words[439]);
    memcpy(&graph_word, instance->descriptor_a + 0x00, sizeof(graph_word));
    assert(graph_word == 8u);
    assert(instance->descriptor_a[4] == 1u);
    assert(instance->descriptor_a[5] == 1u);
    memcpy(&graph_word, instance->descriptor_a + 0x0C, sizeof(graph_word));
    assert(graph_word == 0x8DB8u);
    memcpy(&graph_word, instance->descriptor_a + 0x10, sizeof(graph_word));
    assert(graph_word == 0x9CB8u);
    memcpy(&graph_word, instance->descriptor_b + 0x0C, sizeof(graph_word));
    assert(graph_word == 0x9CD8u);
    assert(instance->softmax_execute ==
           (uintptr_t)&quantized_runtime_float_softmax_execute);
    assert(instance->vector_36dcc == (uintptr_t)0x00036DCDu);
    assert(instance->recurrent.units == 16u);
    assert(instance->recurrent.state != NULL);
    for (uint32_t index = 0u; index < 16u; ++index) {
        assert(test_f32_bits(instance->recurrent.state[index]) == 0u);
    }
    assert(instance->recurrent.input_weights_offset == 0x9D44u);
    assert(instance->recurrent.recurrent_weights_offset == 0xB454u);
    assert(instance->recurrent.bias_offset == 0xB754u);
    assert(instance->recurrent.execute ==
           (uintptr_t)&quantized_runtime_recurrent_execute_target);
    memcpy(&graph_word, instance->descriptor_c + 0x0C, sizeof(graph_word));
    assert(graph_word == 0xB9ECu);
    memcpy(&graph_word, instance->descriptor_d + 0x0C, sizeof(graph_word));
    assert(graph_word == 0xBD1Cu);
    quantized_runtime_goodix_model_instance_destroy(
        &instance, test_recurrent_release, &instance_trace);
    assert(instance == NULL);
    assert(instance_trace.releases == 2u);

    /* Bounds fail before allocation; nested-state failure releases outer. */
    recurrent_allocation_trace instance_failure = {0};
    assert(!quantized_runtime_goodix_model_instance_create(
        &bound, &instance, instance_model_words,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS - 1u,
        0x8000u, test_recurrent_allocate, test_recurrent_release,
        &instance_failure, NULL, NULL));
    assert(instance == NULL);
    assert(instance_failure.calls == 0u);
    instance_failure.fail_on_call = 2u;
    assert(!quantized_runtime_goodix_model_instance_create(
        &bound, &instance, instance_model_words,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x8000u,
        test_recurrent_allocate, test_recurrent_release, &instance_failure,
        NULL, NULL));
    assert(instance == NULL);
    assert(instance_failure.calls == 2u);
    assert(instance_failure.releases == 1u);

    /* 0x0002F624: owner configuration wrapper around the model instance. */
    recurrent_allocation_trace owner_trace = {0};
    quantized_runtime_goodix_model_owner owner;
    memset(&owner, 0xAA, sizeof(owner));
    assert(quantized_runtime_goodix_model_owner_initialize(
        &bound, &owner, instance_model_words,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x8000u,
        test_recurrent_allocate, test_recurrent_release, &owner_trace));
    for (size_t index = 0u; index < sizeof(owner.reserved_00); ++index) {
        assert(owner.reserved_00[index] == 0xAAu);
    }
    assert(owner.primary_enabled == 1u);
    assert(owner.primary_stride == 1u);
    assert(owner.primary_window == 125u);
    assert(owner.secondary_enabled == 1u);
    assert(owner.secondary_stride == 1u);
    assert(owner.secondary_window == 125u);
    assert(owner.reserved_0e[0] == 0xAAu);
    assert(owner.reserved_0e[1] == 0xAAu);
    assert(owner.input_channels == 1u);
    assert(owner.graph_count == 2u);
    assert(owner.output_channels == 1u);
    assert(owner.instance != NULL);
    quantized_runtime_goodix_model_owner_destroy(
        &owner, test_recurrent_release, &owner_trace);
    assert(owner.instance == NULL);
    assert(owner_trace.releases == 2u);

    recurrent_allocation_trace owner_failure = {0};
    owner_failure.fail = 1;
    memset(&owner, 0, sizeof(owner));
    assert(!quantized_runtime_goodix_model_owner_initialize(
        &bound, &owner, instance_model_words,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x8000u,
        test_recurrent_allocate, test_recurrent_release, &owner_failure));
    assert(owner.primary_window == 125u);
    assert(owner.secondary_window == 125u);
    assert(owner.graph_count == 2u);
    assert(owner.instance == NULL);

    /* 0x00074B44: Goodix aligned descriptor constructor. */
    memset(record, 0xAA, sizeof(record));
    arena_cursor = 0x3001u;
    quantized_runtime_aligned_descriptor_construct(
        &bound, record, 3u, 4u, 5u, 6u, 10u, 7u, 4u, 0xDEADBEEFu,
        8u, &arena_cursor, 0.25f);
    static const uint8_t aligned_prefix[] = {3u, 4u, 5u, 6u,
                                             10u, 7u, 4u, 8u};
    assert(memcmp(record, aligned_prefix, sizeof(aligned_prefix)) == 0);
    memcpy(&word, record + 8, sizeof(word));
    assert(word == 0x3E800000u); /* 0.25f */
    memcpy(&word, record + 0x0C, sizeof(word));
    assert(word == 0x3001u);
    memcpy(&word, record + 0x10, sizeof(word));
    assert(word == 0x3051u); /* 0x3001 + align4(7*3*(10/4)) + 7*4 + 8 */
    memcpy(&word, record + 0x14, sizeof(word));
    assert(word ==
           (uint32_t)(uintptr_t)&quantized_runtime_i8_conv1d_execute_target);
    assert(arena_cursor == 0x307Du); /* aligned end + 7*8 + 24 */

    /* Recovered udiv-by-zero makes the packed span zero. */
    arena_cursor = 0x3001u;
    quantized_runtime_aligned_descriptor_construct(
        &rt, record, 3u, 4u, 5u, 6u, 10u, 7u, 0u, 0u, 8u,
        &arena_cursor, 0.25f);
    memcpy(&word, record + 0x10, sizeof(word));
    assert(word == 0x3025u); /* weights + 7*4 + 8 */
    memcpy(&word, record + 0x14, sizeof(word));
    assert(word ==
           (uint32_t)(uintptr_t)&quantized_runtime_i8_conv1d_execute_target);
    assert(arena_cursor == 0x3051u); /* weights + 7*8 + 24 */
    quantized_runtime_aligned_descriptor_construct(
        &rt, NULL, 1u, 1u, 1u, 1u, 1u, 1u, 1u, 0u, 0u,
        &arena_cursor, 0.0f);

    /* 0x00074C6C: packed pooling descriptor with local executor vector. */
    uint8_t pool_descriptor[8];
    memset(pool_descriptor, 0xAA, sizeof(pool_descriptor));
    quantized_runtime_packed_pool_descriptor_initialize(
        pool_descriptor, 0x100u, 0x202u, 0x303u, 0x44u);
    memcpy(&word, pool_descriptor, sizeof(word));
    assert(word == 0x44030200u);
    memcpy(&word, pool_descriptor + 4, sizeof(word));
    assert(word == (uint32_t)(uintptr_t)&quantized_runtime_pooling_execute);
    quantized_runtime_packed_pool_descriptor_initialize(NULL, 0u, 0u, 0u,
                                                        0u);

    /* 0x00074CB4: cursor pair plus local int8-add executor vector. */
    const uint32_t add_words[] = {0xBF800000u, 0x40000000u, 0xDEADBEEFu};
    const uint32_t *add_cursor = add_words;
    uint8_t add_descriptor[16];
    memset(add_descriptor, 0xAA, sizeof(add_descriptor));
    quantized_runtime_cursor_pair_add_descriptor_construct(add_descriptor,
                                                           &add_cursor);
    static const uint32_t expected_add_prefix[] = {
        0u, 0xBF800000u, 0x40000000u,
    };
    assert(memcmp(add_descriptor, expected_add_prefix,
                  sizeof(expected_add_prefix)) == 0);
    memcpy(&word, add_descriptor + 0x0C, sizeof(word));
    assert(word ==
           (uint32_t)(uintptr_t)&quantized_runtime_int8_add_execute);
    assert(add_cursor == add_words + 2);
    quantized_runtime_cursor_pair_add_descriptor_construct(NULL, &add_cursor);
    quantized_runtime_cursor_pair_add_descriptor_construct(add_descriptor,
                                                           NULL);
}

static void test_tensor_pool(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);
    quantized_runtime_pool pool;
    quantized_runtime_pool_initialize(&pool);

    /* slot claim: 12 slots, then NULL */
    quantized_runtime_tensor *claimed[QUANTIZED_RUNTIME_TENSOR_SLOTS];
    for (uint32_t index = 0u; index < QUANTIZED_RUNTIME_TENSOR_SLOTS;
            ++index) {
        claimed[index] = quantized_runtime_pool_slot_claim(&pool);
        assert(claimed[index] == &pool.slots[index]);
        assert(pool.in_use[index] == 1u);
    }
    assert(quantized_runtime_pool_slot_claim(&pool) == NULL);
    assert(quantized_runtime_pool_slot_claim(NULL) == NULL);
    quantized_runtime_pool_initialize(&pool);

    /* construct: dims product, flags, NULL data */
    const uint16_t dims_2x3[] = {2u, 3u};
    quantized_runtime_tensor *tensor =
        quantized_runtime_tensor_construct(&pool, 2, dims_2x3);
    assert(tensor == &pool.slots[0]);
    assert(tensor->count == 6u);
    assert(tensor->dims[0] == 2u);
    assert(tensor->dims[1] == 3u);
    assert(tensor->flags ==
           (2u | QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS));
    assert(tensor->data == NULL);
    assert(quantized_runtime_tensor_construct(&pool, 4, dims_2x3) == NULL);
    assert(quantized_runtime_tensor_construct(&pool, -1, dims_2x3) == NULL);
    assert(quantized_runtime_tensor_construct(NULL, 2, dims_2x3) == NULL);
    assert(quantized_runtime_tensor_construct(&pool, 2, NULL) == NULL);

    /* allocate: arena hand-out and watermark */
    const uint16_t dims_4[] = {4u};
    quantized_runtime_tensor *first =
        quantized_runtime_tensor_allocate(&rt, &pool, 1, dims_4);
    assert(first == &pool.slots[1]);
    assert(first->data == pool.arena);
    assert((first->flags & QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS) == 0u);
    assert(pool.used_words == 4u);

    /* create + fill */
    const uint16_t dims_3[] = {3u};
    quantized_runtime_tensor *filled =
        quantized_runtime_tensor_create_fill(&rt, &pool, 1, dims_3, 2.5f);
    assert(filled->data == pool.arena + 4);
    assert(pool.used_words == 7u);
    for (uint32_t index = 0u; index < 3u; ++index) {
        assert(filled->data[index] == 0x40200000u);
    }

    /* reshape: flags/dims updated, count NOT recomputed (recovered quirk) */
    const uint16_t dims_5[] = {5u};
    quantized_runtime_tensor_reshape(tensor, 1, dims_5);
    assert(tensor->dims[0] == 5u);
    assert((tensor->flags & 3u) == 1u);
    assert(tensor->count == 6u);
    quantized_runtime_tensor_reshape(tensor, 4, dims_5);
    assert(tensor->dims[0] == 5u);
    quantized_runtime_tensor_reshape(NULL, 1, dims_5);
    quantized_runtime_tensor_reshape(tensor, 1, NULL);

    /* 0x00091E02: first-dimension view with byte/halfword offset forms. */
    uint32_t quantized_storage[3] = {0u, 0u, 0u};
    quantized_runtime_tensor slice_input;
    memset(&slice_input, 0, sizeof(slice_input));
    slice_input.data = quantized_storage;
    slice_input.count = 12u;
    slice_input.dims[0] = 4u;
    slice_input.dims[1] = 3u;
    slice_input.flags = (uint8_t)(2u | QUANTIZED_RUNTIME_TENSOR_FLAG_INT8);
    slice_input.reserved_10 = 0x3F000000u;
    quantized_runtime_tensor *byte_slice =
        quantized_runtime_tensor_slice(&pool, &slice_input, 1u, 3u);
    assert(byte_slice != NULL && byte_slice->count == 6u);
    assert(byte_slice->dims[0] == 2u && byte_slice->dims[1] == 3u);
    assert((uint8_t *)(void *)byte_slice->data ==
           (uint8_t *)(void *)quantized_storage + 3u);
    assert((byte_slice->flags & QUANTIZED_RUNTIME_TENSOR_FLAG_INT8) != 0u);
    assert(byte_slice->reserved_10 == 0x3F000000u);

    int16_t halfword_storage[12] = {0};
    slice_input.data = (uint32_t *)(void *)halfword_storage;
    slice_input.flags = 2u;
    slice_input.reserved_10 = 0xFFFFFFFFu;
    quantized_runtime_tensor *halfword_slice =
        quantized_runtime_tensor_slice(&pool, &slice_input, 2u, 4u);
    assert(halfword_slice != NULL && halfword_slice->count == 6u);
    assert((uint8_t *)(void *)halfword_slice->data ==
           (uint8_t *)(void *)halfword_storage + 12u);
    assert((halfword_slice->flags & QUANTIZED_RUNTIME_TENSOR_FLAG_INT8) == 0u);
    assert(halfword_slice->reserved_10 == 0u);
    assert(quantized_runtime_tensor_slice(
               &pool, &slice_input, 3u, 5u) == NULL);
    slice_input.flags = 0u;
    assert(quantized_runtime_tensor_slice(
               &pool, &slice_input, 0u, 0u) == NULL);

    /* release: buffer-backed tensors lose their data pointer; the slot is
     * freed */
    quantized_runtime_tensor_release(&pool, first);
    assert(first->data == NULL);
    assert(pool.in_use[1] == 0u);
    /* bufferless tensors keep their data pointer on release */
    quantized_runtime_tensor_release(&pool, tensor);
    assert(pool.in_use[0] == 0u);
    /* foreign descriptor: slot scan misses, nothing changes */
    quantized_runtime_tensor foreign;
    memset(&foreign, 0, sizeof(foreign));
    foreign.flags = QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS;
    foreign.data = pool.arena;
    quantized_runtime_tensor_release(&pool, &foreign);
    assert(foreign.data == pool.arena);
    quantized_runtime_tensor_release(NULL, tensor);
    quantized_runtime_tensor_release(&pool, NULL);

    /* release_many: NULL entries are skipped, array slots are zeroed */
    quantized_runtime_tensor *arranged[3];
    arranged[0] = filled;
    arranged[1] = NULL;
    arranged[2] = quantized_runtime_tensor_construct(&pool, 1, dims_3);
    assert(arranged[2] != NULL);
    const uint32_t filled_slot =
        (uint32_t)(filled - pool.slots);
    const uint32_t arranged_slot =
        (uint32_t)(arranged[2] - pool.slots);
    quantized_runtime_tensor_release_many(&pool, arranged, 3);
    assert(arranged[0] == NULL && arranged[1] == NULL && arranged[2] == NULL);
    assert(pool.in_use[filled_slot] == 0u);
    assert(pool.in_use[arranged_slot] == 0u);
    /* negative count is a no-op (recovered signed loop bound) */
    arranged[0] = quantized_runtime_tensor_construct(&pool, 1, dims_3);
    quantized_runtime_tensor_release_many(&pool, arranged, -1);
    assert(arranged[0] != NULL);
    quantized_runtime_tensor_release_many(NULL, arranged, 1);
    quantized_runtime_tensor_release_many(&pool, NULL, 1);
}

static void test_arena_compaction(void) {
    quantized_runtime rt;
    test_rt_reset(&rt);
    quantized_runtime_pool pool;
    quantized_runtime_pool_initialize(&pool);

    const uint16_t dims_600[] = {600u};
    const uint16_t dims_800[] = {800u};
    quantized_runtime_tensor *first =
        quantized_runtime_tensor_allocate(&rt, &pool, 1, dims_600);
    quantized_runtime_tensor *second =
        quantized_runtime_tensor_create_fill(&rt, &pool, 1, dims_600, 3.5f);
    assert(first != NULL && second != NULL);
    assert(pool.used_words == 1200u);
    quantized_runtime_tensor_release(&pool, first);

    /* 1200 + 800 >= 1700: compaction moves the live buffer down first */
    quantized_runtime_tensor *third =
        quantized_runtime_tensor_allocate(&rt, &pool, 1, dims_800);
    assert(third != NULL);
    assert(second->data == pool.arena);
    for (uint32_t index = 0u; index < 600u; ++index) {
        assert(second->data[index] == 0x40600000u); /* 3.5f */
    }
    assert(third->data == pool.arena + 600);
    assert(pool.used_words == 1400u);

    /* overflow guard: live data alone exceeds the arena */
    quantized_runtime_pool_initialize(&pool);
    const uint16_t dims_1700[] = {1700u};
    const uint16_t dims_1[] = {1u};
    assert(quantized_runtime_tensor_allocate(&rt, &pool, 1, dims_1700) != NULL);
    assert(quantized_runtime_tensor_allocate(&rt, &pool, 1, dims_1) == NULL);
    quantized_runtime_pool_initialize(&pool);
    const uint16_t dims_1701[] = {1701u};
    assert(quantized_runtime_tensor_allocate(&rt, &pool, 1, dims_1701) == NULL);

    /* compaction with an unbound qsort provider fails explicitly */
    quantized_runtime no_qsort_rt;
    quantized_runtime_providers no_qsort_providers = test_providers;
    no_qsort_providers.qsort_fn = NULL;
    quantized_runtime_initialize(&no_qsort_rt, &no_qsort_providers);
    quantized_runtime_pool_initialize(&pool);
    assert(quantized_runtime_tensor_allocate(&no_qsort_rt, &pool, 1,
                                             dims_600) != NULL);
    assert(quantized_runtime_tensor_allocate(&no_qsort_rt, &pool, 1,
                                             dims_600) != NULL);
    assert(quantized_runtime_tensor_allocate(&no_qsort_rt, &pool, 1,
                                             dims_600) == NULL);

    /* bad arguments */
    assert(quantized_runtime_arena_allocate(NULL, &pool, second) == NULL);
    assert(quantized_runtime_arena_allocate(&rt, NULL, second) == NULL);
    assert(quantized_runtime_arena_allocate(&rt, &pool, NULL) == NULL);
    assert(quantized_runtime_tensor_allocate(NULL, &pool, 1, dims_1) == NULL);
    assert(quantized_runtime_tensor_create_fill(NULL, &pool, 1, dims_1, 0.0f) ==
           NULL);
}

typedef struct {
    size_t calls;
    quantized_runtime_pool *pool;
    const quantized_runtime_tensor *inputs[2];
    uint32_t begins[2];
    uint32_t ends[2];
} slice_trace;

static slice_trace g_slice_trace;
static quantized_runtime_tensor *g_slice_results[2];

static quantized_runtime_tensor *tracing_slice(
    quantized_runtime_pool *pool, const quantized_runtime_tensor *input,
    uint32_t begin, uint32_t end) {
    const size_t call = g_slice_trace.calls;
    g_slice_trace.calls += 1u;
    g_slice_trace.pool = pool;
    g_slice_trace.inputs[call] = input;
    g_slice_trace.begins[call] = begin;
    g_slice_trace.ends[call] = end;
    return g_slice_results[call];
}

typedef struct {
    size_t calls;
    float alpha;
    quantized_runtime_pool *pool;
    quantized_runtime_tensor *tensor;
    uint32_t in_place;
    uint32_t result;
} scaled_mul_trace;

static scaled_mul_trace g_scaled_mul_trace;

static uint32_t tracing_scaled_mul(float alpha, quantized_runtime_pool *pool,
                                   quantized_runtime_tensor *tensor,
                                   uint32_t in_place) {
    g_scaled_mul_trace.calls += 1u;
    g_scaled_mul_trace.alpha = alpha;
    g_scaled_mul_trace.pool = pool;
    g_scaled_mul_trace.tensor = tensor;
    g_scaled_mul_trace.in_place = in_place;
    return g_scaled_mul_trace.result;
}

static void test_cross_family_seams(void) {
    /* 0x0005A3D4: two-output thirds slice through the bound GoMore seam */
    quantized_runtime_providers providers = test_providers;
    providers.slice_fn = tracing_slice;
    providers.scaled_mul_fn = tracing_scaled_mul;
    quantized_runtime rt;
    quantized_runtime_initialize(&rt, &providers);
    quantized_runtime_pool pool;
    quantized_runtime_pool_initialize(&pool);

    quantized_runtime_tensor input_a;
    quantized_runtime_tensor input_b;
    memset(&input_a, 0, sizeof(input_a));
    memset(&input_b, 0, sizeof(input_b));
    input_a.dims[0] = 9u;
    input_b.dims[0] = 12u;
    quantized_runtime_tensor marker_a;
    quantized_runtime_tensor marker_b;
    g_slice_results[0] = &marker_a;
    g_slice_results[1] = &marker_b;
    memset(&g_slice_trace, 0, sizeof(g_slice_trace));
    quantized_runtime_tensor *outputs[2] = {NULL, NULL};
    assert(quantized_runtime_two_output_thirds_slice(&rt, &pool, &input_a,
                                                     &input_b, outputs, 2u) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(g_slice_trace.calls == 2u);
    assert(g_slice_trace.pool == &pool);
    assert(g_slice_trace.inputs[0] == &input_a);
    assert(g_slice_trace.inputs[1] == &input_b);
    assert(g_slice_trace.begins[0] == 6u && g_slice_trace.ends[0] == 9u);
    assert(g_slice_trace.begins[1] == 6u && g_slice_trace.ends[1] == 9u);
    assert(outputs[0] == &marker_a && outputs[1] == &marker_b);

    /* integer third: dims[0] = 8 -> third 2 */
    input_a.dims[0] = 8u;
    memset(&g_slice_trace, 0, sizeof(g_slice_trace));
    assert(quantized_runtime_two_output_thirds_slice(&rt, &pool, &input_a,
                                                     &input_b, outputs, 1u) ==
           QUANTIZED_RUNTIME_STATUS_OK);
    assert(g_slice_trace.begins[0] == 2u && g_slice_trace.ends[0] == 4u);

    /* unbound seam fails explicitly */
    quantized_runtime unbound;
    quantized_runtime_initialize(&unbound, NULL);
    outputs[0] = &marker_a;
    outputs[1] = &marker_b;
    assert(quantized_runtime_two_output_thirds_slice(&unbound, &pool, &input_a,
                                                     &input_b, outputs, 0u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(outputs[0] == NULL && outputs[1] == NULL);
    assert(quantized_runtime_two_output_thirds_slice(&rt, NULL, &input_a,
                                                     &input_b, outputs, 0u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_two_output_thirds_slice(NULL, &pool, &input_a,
                                                     &input_b, outputs, 0u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);

    /* 0x00065680: scaled-mul seam with conditional release */
    const uint16_t dims_2[] = {2u};
    quantized_runtime_tensor *tensor =
        quantized_runtime_tensor_construct(&pool, 1, dims_2);
    assert(tensor != NULL);
    const uint32_t slot = (uint32_t)(tensor - pool.slots);
    memset(&g_scaled_mul_trace, 0, sizeof(g_scaled_mul_trace));
    g_scaled_mul_trace.result = 0x2Au;
    float alpha = 0.25f;
    assert(quantized_runtime_scaled_mul_conditional_release(
               &rt, &alpha, &pool, tensor, 1u) == 0x2Au);
    assert(g_scaled_mul_trace.calls == 1u);
    assert(test_f32_bits(g_scaled_mul_trace.alpha) == test_f32_bits(0.25f));
    assert(g_scaled_mul_trace.pool == &pool);
    assert(g_scaled_mul_trace.tensor == tensor);
    assert(g_scaled_mul_trace.in_place == 1u);
    assert(pool.in_use[slot] == 0u); /* released */

    quantized_runtime_tensor *kept =
        quantized_runtime_tensor_construct(&pool, 1, dims_2);
    const uint32_t kept_slot = (uint32_t)(kept - pool.slots);
    assert(quantized_runtime_scaled_mul_conditional_release(
               &rt, &alpha, &pool, kept, 0u) == 0x2Au);
    assert(pool.in_use[kept_slot] == 1u); /* not released */

    assert(quantized_runtime_scaled_mul_conditional_release(
               &unbound, &alpha, &pool, kept, 1u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_scaled_mul_conditional_release(
               &rt, NULL, &pool, kept, 1u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
    assert(quantized_runtime_scaled_mul_conditional_release(
               NULL, &alpha, &pool, kept, 1u) ==
           QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT);
}

void test_reconstructed_quantized_runtime(void) {
    test_round_helpers();
    test_recurrent_executor();
    test_goodix_stage_pipelines();
    test_goodix_layer_block_builder();
    test_goodix_second_graph_builder();
    test_goodix_layer_executor();
    test_goodix_second_executor();
    test_goodix_executor();
    test_params_derive();
    test_quantize_executor();
    test_int8_add_executor();
    test_i8_conv1d_executor();
    test_float_dense_executor();
    test_pooling_executor();
    test_softmax_executor();
    test_float_add_executor();
    test_descriptor_constructors();
    test_tensor_pool();
    test_arena_compaction();
    test_cross_family_seams();
}
