#include <assert.h>
#include <stddef.h>
#include <stdint.h>

#include "gomore_tensor_runtime/gomore_tensor_runtime.h"

static float plus_one(float value) {
    return value + 1.0f;
}

static float positive_exp_fixture(float value) {
    return value + 2.0f;
}

static float maximum_fixture(float left, float right) {
    return left > right ? left : right;
}

static float dequantize_half(int16_t value) {
    return (float)value * 0.5f;
}

static unsigned batch_half_calls;
static unsigned batch_sqrt_calls;
static uint16_t batch_half_values[32];

static uint32_t batch_half_bits(uint16_t value) {
    assert(batch_half_calls <
           sizeof(batch_half_values) / sizeof(batch_half_values[0]));
    batch_half_values[batch_half_calls++] = value;
    switch (value) {
        case UINT16_C(0x0000):
            return UINT32_C(0x00000000);
        case UINT16_C(0x3C00):
            return UINT32_C(0x3F800000);
        case UINT16_C(0x4000):
            return UINT32_C(0x40000000);
        case UINT16_C(0x4200):
            return UINT32_C(0x40400000);
        case UINT16_C(0x4400):
            return UINT32_C(0x40800000);
        default:
            assert(false);
            return 0u;
    }
}

static float batch_square_root(float value) {
    ++batch_sqrt_calls;
    if (value == 1.0f) {
        return 1.0f;
    }
    assert(value == 4.0f);
    return 2.0f;
}

static unsigned tensor_release_calls;
static uintptr_t tensor_release_runtime;
static uintptr_t tensor_release_input;

static void tensor_release(uintptr_t runtime_binding,
                           uintptr_t tensor_binding) {
    ++tensor_release_calls;
    tensor_release_runtime = runtime_binding;
    tensor_release_input = tensor_binding;
}

typedef struct {
    unsigned stage_calls;
    unsigned release_calls;
    const void *contexts[2];
    uintptr_t runtimes[2];
    uintptr_t inputs[2];
    uintptr_t parameters[2][4];
    uintptr_t candidates[2];
    uintptr_t releases[3];
} tensor_chain_trace;

static tensor_chain_trace chain_trace;

static uintptr_t tensor_chain_stage(
    const void *configuration_context,
    uintptr_t runtime_binding, uintptr_t input_binding,
    uintptr_t parameter0, uintptr_t parameter1,
    uintptr_t parameter2, uintptr_t parameter3,
    uintptr_t output_candidate_binding) {
    const unsigned call = chain_trace.stage_calls++;
    assert(call < 2u);
    chain_trace.contexts[call] = configuration_context;
    chain_trace.runtimes[call] = runtime_binding;
    chain_trace.inputs[call] = input_binding;
    chain_trace.parameters[call][0] = parameter0;
    chain_trace.parameters[call][1] = parameter1;
    chain_trace.parameters[call][2] = parameter2;
    chain_trace.parameters[call][3] = parameter3;
    chain_trace.candidates[call] = output_candidate_binding;
    return input_binding + parameter0 + output_candidate_binding;
}

static void tensor_chain_release(uintptr_t runtime_binding,
                                 uintptr_t tensor_binding) {
    assert(runtime_binding == 9u && chain_trace.release_calls < 3u);
    chain_trace.releases[chain_trace.release_calls++] = tensor_binding;
}

typedef struct {
    unsigned slice_calls;
    unsigned dual_calls;
    unsigned gated_calls;
    unsigned blend_calls;
    unsigned release_calls;
    uintptr_t slice_sources[6][2];
    uint32_t slice_indices[6];
    uintptr_t dual_primary[2][2];
    uintptr_t dual_bias[2][2];
    uintptr_t gated_primary[2];
    uintptr_t gated_bias[2];
    uintptr_t gated_gate;
    uintptr_t blend_inputs[3];
    uintptr_t releases[15];
    bool activation_add_bias[3];
    bool fail_second_bias_slice;
} tensor_cell_trace;

static tensor_cell_trace cell_trace;
static const uint32_t cell_context = UINT32_C(0xCAFEBABE);

static bool tensor_cell_slice_pair(
    const void *context, uintptr_t runtime_binding,
    uintptr_t first_source, uintptr_t second_source,
    uint32_t index, uintptr_t outputs[2]) {
    assert(context == &cell_context && runtime_binding == 9u &&
           outputs != NULL && index < 3u && cell_trace.slice_calls < 6u);
    const unsigned call = cell_trace.slice_calls++;
    cell_trace.slice_sources[call][0] = first_source;
    cell_trace.slice_sources[call][1] = second_source;
    cell_trace.slice_indices[call] = index;
    if (first_source == 30u && cell_trace.fail_second_bias_slice &&
            index == 1u) {
        return false;
    }
    const uintptr_t base = first_source == 10u ? 100u : 200u;
    outputs[0] = base + (uintptr_t)index * 10u;
    outputs[1] = outputs[0] + 1u;
    return true;
}

static uintptr_t tensor_cell_dual_activate(
    const void *context, uintptr_t runtime_binding,
    uintptr_t input_binding, uintptr_t first_primary,
    uintptr_t first_bias, uintptr_t shared_binding,
    uintptr_t second_primary, uintptr_t second_bias,
    bool add_bias) {
    assert(context == &cell_context && runtime_binding == 9u &&
           input_binding == 5u && shared_binding == 50u &&
           cell_trace.dual_calls < 2u);
    const unsigned call = cell_trace.dual_calls++;
    cell_trace.dual_primary[call][0] = first_primary;
    cell_trace.dual_primary[call][1] = second_primary;
    cell_trace.dual_bias[call][0] = first_bias;
    cell_trace.dual_bias[call][1] = second_bias;
    cell_trace.activation_add_bias[call] = add_bias;
    return 1000u + call;
}

static uintptr_t tensor_cell_gated_activate(
    const void *context, uintptr_t runtime_binding,
    uintptr_t input_binding, uintptr_t first_primary,
    uintptr_t first_bias, uintptr_t shared_binding,
    uintptr_t second_primary, uintptr_t second_bias,
    uintptr_t gate_binding, bool add_bias) {
    assert(context == &cell_context && runtime_binding == 9u &&
           input_binding == 5u && shared_binding == 50u &&
           cell_trace.gated_calls == 0u);
    ++cell_trace.gated_calls;
    cell_trace.gated_primary[0] = first_primary;
    cell_trace.gated_primary[1] = second_primary;
    cell_trace.gated_bias[0] = first_bias;
    cell_trace.gated_bias[1] = second_bias;
    cell_trace.gated_gate = gate_binding;
    cell_trace.activation_add_bias[2] = add_bias;
    return 2000u;
}

static uintptr_t tensor_cell_blend(
    const void *context, uintptr_t runtime_binding,
    uintptr_t factor_binding, uintptr_t first_binding,
    uintptr_t second_binding) {
    assert(context == &cell_context && runtime_binding == 9u &&
           cell_trace.blend_calls == 0u);
    ++cell_trace.blend_calls;
    cell_trace.blend_inputs[0] = factor_binding;
    cell_trace.blend_inputs[1] = first_binding;
    cell_trace.blend_inputs[2] = second_binding;
    return 3000u;
}

static void tensor_cell_release(uintptr_t runtime_binding,
                                uintptr_t tensor_binding) {
    assert(runtime_binding == 9u && cell_trace.release_calls < 15u);
    cell_trace.releases[cell_trace.release_calls++] = tensor_binding;
}

void test_reconstructed_gomore_tensor_runtime(void) {
    const float source[3] = {-2.0f, 0.0f, 3.0f};
    float output[3] = {0.0f, 0.0f, 0.0f};
    assert(gomore_tensor_map(source, output, 3u, plus_one));
    assert(output[0] == -1.0f && output[1] == 1.0f && output[2] == 4.0f);

    const float right[3] = {2.0f, 4.0f, -1.0f};
    assert(gomore_tensor_multiply(source, right, output, 3u));
    assert(output[0] == -4.0f && output[1] == 0.0f && output[2] == -3.0f);
    assert(gomore_tensor_add(source, right, output, 3u));
    assert(output[0] == 0.0f && output[1] == 4.0f && output[2] == 2.0f);
    const float factor[3] = {0.0f, 0.25f, 1.0f};
    const float first[3] = {10.0f, 20.0f, 30.0f};
    const float second[3] = {2.0f, 4.0f, 6.0f};
    assert(gomore_tensor_blend(factor, first, second, output, 3u));
    assert(output[0] == 2.0f && output[1] == 8.0f && output[2] == 30.0f);
    assert(gomore_tensor_leaky_relu(source, output, 3u, 0.25f));
    assert(output[0] == -0.5f && output[1] == 0.0f && output[2] == 3.0f);

    const float logits[2] = {0.0f, 2.0f};
    float probabilities[2] = {0.0f, 0.0f};
    assert(gomore_tensor_softmax(logits, probabilities, 2u,
                                 positive_exp_fixture));
    assert(probabilities[0] == (2.0f / 6.0f));
    assert(probabilities[1] == (4.0f / 6.0f));

    const int16_t bias[3] = {2, -4, 6};
    assert(gomore_tensor_dequant_bias_add(source, bias, output, 3u,
                                          dequantize_half));
    assert(output[0] == -1.0f && output[1] == -2.0f && output[2] == 6.0f);

    const int8_t weights[6] = {1, 2, -1, 3, 0, 2};
    const float input[3] = {2.0f, 1.0f, 4.0f};
    float dot[2] = {0.0f, 0.0f};
    assert(gomore_tensor_int8_float_dot(weights, 2u, 3u, 0.5f,
                                        input, dot));
    assert(dot[0] == 0.0f && dot[1] == 7.0f);
    const int16_t affine_bias[2] = {2, -4};
    assert(gomore_tensor_int8_float_affine(
        weights, 2u, 3u, 0.5f, input, affine_bias, dot,
        dequantize_half));
    assert(dot[0] == 1.0f && dot[1] == 5.0f);

    const int8_t first_branch_weights[4] = {1, 2, -1, 1};
    const int8_t second_branch_weights[4] = {2, 0, 1, -2};
    const float branch_input[2] = {2.0f, 4.0f};
    const int16_t first_branch_bias[2] = {2, -2};
    const int16_t second_branch_bias[2] = {4, 2};
    float branch_output[2] = {0.0f, 0.0f};
    float branch_scratch[2] = {0.0f, 0.0f};
    assert(gomore_tensor_dual_affine_activate(
        first_branch_weights, second_branch_weights, 2u, 2u,
        0.5f, 0.25f, branch_input, true,
        first_branch_bias, second_branch_bias, dequantize_half,
        branch_output, branch_scratch, plus_one));
    assert(branch_output[0] == 10.0f && branch_output[1] == 0.5f);

    const float gate[2] = {2.0f, 4.0f};
    assert(gomore_tensor_gated_dual_affine_activate(
        first_branch_weights, second_branch_weights, 2u, 2u,
        0.5f, 0.25f, branch_input, true,
        first_branch_bias, second_branch_bias, dequantize_half,
        gate, branch_output, branch_scratch, plus_one));
    assert(branch_output[0] == 13.0f && branch_output[1] == -1.0f);
    assert(!gomore_tensor_dual_affine_activate(
        first_branch_weights, second_branch_weights, 2u, 2u,
        0.5f, 0.25f, branch_input, false,
        NULL, NULL, NULL, branch_output, branch_output, plus_one));
    assert(!gomore_tensor_dual_affine_activate(
        first_branch_weights, second_branch_weights, 2u, 2u,
        0.5f, 0.25f, branch_input, true,
        NULL, second_branch_bias, dequantize_half,
        branch_output, branch_scratch, plus_one));

    const float matrix[6] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f};
    float transposed[6] = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    assert(gomore_tensor_strided_copy_2d(
        matrix, 6u, 2u, 3u, 2u, 1u,
        transposed, 6u, 3u, 2u));
    assert(transposed[0] == 1.0f && transposed[1] == 4.0f &&
           transposed[2] == 2.0f && transposed[3] == 5.0f &&
           transposed[4] == 3.0f && transposed[5] == 6.0f);

    const float pooling_source[12] = {
        1.0f, 5.0f, 3.0f, 4.0f, 2.0f, 6.0f,
        -1.0f, -5.0f, -3.0f, -4.0f, -2.0f, -6.0f,
    };
    float pooled[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    assert(gomore_tensor_pool_1d(
        pooling_source, 12u, 2u, 6u, pooled, 4u, 2u, 2u,
        0u, 3u, 2u, 0u, maximum_fixture));
    assert(pooled[0] == 5.0f && pooled[1] == 4.0f &&
           pooled[2] == -1.0f && pooled[3] == -2.0f);
    assert(gomore_tensor_pool_1d(
        pooling_source, 12u, 2u, 6u, pooled, 4u, 2u, 2u,
        1u, 3u, 2u, 0u, NULL));
    assert(pooled[0] == 3.0f && pooled[1] == 3.0f &&
           pooled[2] == -3.0f && pooled[3] == -3.0f);
    pooled[0] = 42.0f;
    assert(gomore_tensor_pool_1d(
        pooling_source, 12u, 2u, 6u, pooled, 4u, 2u, 2u,
        2u, 3u, 2u, 0u, NULL));
    assert(pooled[0] == 42.0f);
    assert(!gomore_tensor_pool_1d(
        pooling_source, 12u, 2u, 6u, pooled, 4u, 2u, 2u,
        1u, 3u, 2u, 1u, NULL));

    const float batch_source[8] = {
        1.0f, 2.0f, 2.0f, 4.0f,
        3.0f, 4.0f, 6.0f, 8.0f,
    };
    const uint16_t batch_dimensions[3] = {2u, 2u, 2u};
    const uint16_t batch_scale[2] = {
        UINT16_C(0x4000), UINT16_C(0x4400),
    };
    const uint16_t batch_offset[2] = {
        UINT16_C(0x3C00), UINT16_C(0x4200),
    };
    const uint16_t batch_variance[2] = {
        UINT16_C(0x3C00), UINT16_C(0x4400),
    };
    const uint16_t batch_mean[2] = {
        UINT16_C(0x3C00), UINT16_C(0x4000),
    };
    float batch_output[8] = {0.0f};
    batch_half_calls = 0u;
    batch_sqrt_calls = 0u;
    assert(gomore_tensor_batch_normalize_half(
        batch_source, 8u, batch_dimensions, 3u, UINT16_C(0),
        batch_scale, batch_offset, batch_variance, batch_mean, 2u,
        batch_output, 8u, batch_half_bits, batch_square_root));
    static const float expected_batch_output[8] = {
        1.0f, 3.0f, 3.0f, 7.0f,
        5.0f, 7.0f, 11.0f, 15.0f,
    };
    for (size_t index = 0u; index < 8u; ++index) {
        assert(batch_output[index] == expected_batch_output[index]);
    }
    assert(batch_half_calls == 29u && batch_sqrt_calls == 4u &&
           batch_half_values[0] == UINT16_C(0x0000) &&
           batch_half_values[1] == UINT16_C(0x3C00) &&
           batch_half_values[2] == UINT16_C(0x3C00) &&
           batch_half_values[3] == UINT16_C(0x4000) &&
           batch_half_values[4] == UINT16_C(0x3C00) &&
           batch_half_values[8] == UINT16_C(0x4400));

    batch_output[0] = 99.0f;
    batch_half_calls = 0u;
    batch_sqrt_calls = 0u;
    assert(!gomore_tensor_batch_normalize_half(
        batch_source, 8u, batch_dimensions, 3u, UINT16_C(0),
        batch_scale, batch_offset, batch_variance, batch_mean, 2u,
        batch_output, 7u, batch_half_bits, batch_square_root));
    assert(batch_output[0] == 99.0f && batch_half_calls == 0u &&
           batch_sqrt_calls == 0u);
    assert(!gomore_tensor_batch_normalize_half(
        batch_source, 8u, batch_dimensions, 1u, UINT16_C(0),
        batch_scale, batch_offset, batch_variance, batch_mean, 2u,
        batch_output, 8u, batch_half_bits, batch_square_root));

    const float convolution_source[8] = {
        1.0f, 2.0f, 3.0f, 4.0f,
        10.0f, 20.0f, 30.0f, 40.0f,
    };
    const uint16_t convolution_weights[12] = {
        UINT16_C(0x3C00), UINT16_C(0), UINT16_C(0),
        UINT16_C(0), UINT16_C(0x3C00), UINT16_C(0),
        UINT16_C(0), UINT16_C(0x3C00), UINT16_C(0),
        UINT16_C(0), UINT16_C(0), UINT16_C(0x3C00),
    };
    float convolution_weight_scratch[12];
    float convolution_output[8] = {0.0f};
    size_t convolution_output_width = 0u;
    batch_half_calls = 0u;
    assert(gomore_tensor_conv1d_half(
        convolution_source, 8u, 2u, 4u,
        convolution_weights, 12u, 2u, 3u, 1u, 1u,
        convolution_weight_scratch, 12u,
        convolution_output, 8u, &convolution_output_width,
        batch_half_bits));
    static const float expected_convolution_output[8] = {
        10.0f, 21.0f, 32.0f, 43.0f,
        21.0f, 32.0f, 43.0f, 4.0f,
    };
    assert(convolution_output_width == 4u && batch_half_calls == 12u);
    for (size_t index = 0u; index < 8u; ++index) {
        assert(convolution_output[index] ==
               expected_convolution_output[index]);
        assert(convolution_weight_scratch[index] ==
               (convolution_weights[index] == UINT16_C(0x3C00)
                    ? 1.0f : 0.0f));
    }
    for (size_t index = 8u; index < 12u; ++index) {
        assert(convolution_weight_scratch[index] ==
               (convolution_weights[index] == UINT16_C(0x3C00)
                    ? 1.0f : 0.0f));
    }

    convolution_output[0] = 77.0f;
    convolution_output_width = 99u;
    batch_half_calls = 0u;
    assert(!gomore_tensor_conv1d_half(
        convolution_source, 8u, 2u, 4u,
        convolution_weights, 12u, 2u, 3u, 1u, 1u,
        convolution_weight_scratch, 12u,
        convolution_output, 7u, &convolution_output_width,
        batch_half_bits));
    assert(convolution_output[0] == 77.0f &&
           convolution_output_width == 99u && batch_half_calls == 0u);
    assert(!gomore_tensor_conv1d_half(
        convolution_source, 8u, 2u, 4u,
        convolution_weights, 12u, 2u, 3u, 0u, 1u,
        convolution_weight_scratch, 12u,
        convolution_output, 8u, &convolution_output_width,
        batch_half_bits));

    const uint16_t convolution_bias[2] = {
        UINT16_C(0x3C00), UINT16_C(0x4000),
    };
    batch_half_calls = 0u;
    tensor_release_calls = 0u;
    assert(gomore_tensor_conv1d_half_bias(
        convolution_source, 8u, 2u, 4u,
        convolution_weights, 12u, 2u, 3u, 1u, 1u,
        convolution_bias, 2u,
        convolution_weight_scratch, 12u,
        convolution_output, 8u, &convolution_output_width,
        batch_half_bits, true, UINT32_C(0x20002000),
        UINT32_C(0x20003000), tensor_release));
    static const float expected_biased_convolution[8] = {
        11.0f, 22.0f, 33.0f, 44.0f,
        23.0f, 34.0f, 45.0f, 6.0f,
    };
    for (size_t index = 0u; index < 8u; ++index) {
        assert(convolution_output[index] ==
               expected_biased_convolution[index]);
    }
    assert(convolution_output_width == 4u && batch_half_calls == 20u &&
           tensor_release_calls == 1u &&
           tensor_release_runtime == UINT32_C(0x20002000) &&
           tensor_release_input == UINT32_C(0x20003000));
    convolution_output[0] = 88.0f;
    batch_half_calls = 0u;
    tensor_release_calls = 0u;
    assert(!gomore_tensor_conv1d_half_bias(
        convolution_source, 8u, 2u, 4u,
        convolution_weights, 12u, 2u, 3u, 1u, 1u,
        convolution_bias, 1u,
        convolution_weight_scratch, 12u,
        convolution_output, 8u, &convolution_output_width,
        batch_half_bits, true, 1u, 2u, tensor_release));
    assert(convolution_output[0] == 88.0f && batch_half_calls == 0u &&
           tensor_release_calls == 0u);

    const gomore_tensor_chain_stage chain_stages[2] = {
        {1u, 2u, 3u, 4u},
        {11u, 12u, 13u, 14u},
    };
    uintptr_t chain_outputs[2] = {100u, 200u};
    uintptr_t chain_result = UINT32_C(0xFFFFFFFF);
    const uint32_t chain_context = UINT32_C(0x12345678);
    chain_trace = (tensor_chain_trace){0};
    assert(gomore_tensor_chain_run(
        &chain_context, chain_stages, 2u, 9u, 5u,
        chain_outputs, 2u, true,
        tensor_chain_stage, tensor_chain_release, &chain_result));
    assert(chain_trace.stage_calls == 2u &&
           chain_trace.release_calls == 3u &&
           chain_trace.contexts[0] == &chain_context &&
           chain_trace.contexts[1] == &chain_context &&
           chain_trace.runtimes[0] == 9u && chain_trace.runtimes[1] == 9u &&
           chain_trace.inputs[0] == 5u && chain_trace.inputs[1] == 106u &&
           chain_trace.parameters[0][0] == 1u &&
           chain_trace.parameters[0][3] == 4u &&
           chain_trace.parameters[1][0] == 11u &&
           chain_trace.parameters[1][3] == 14u &&
           chain_trace.candidates[0] == 100u &&
           chain_trace.candidates[1] == 200u &&
           chain_trace.releases[0] == 100u &&
           chain_trace.releases[1] == 5u &&
           chain_trace.releases[2] == 200u &&
           chain_outputs[0] == 106u && chain_outputs[1] == 317u &&
           chain_result == 317u);
    chain_trace = (tensor_chain_trace){0};
    chain_outputs[0] = 100u;
    chain_outputs[1] = 200u;
    assert(!gomore_tensor_chain_run(
        &chain_context, chain_stages, 2u, 9u, 5u,
        chain_outputs, 1u, true,
        tensor_chain_stage, tensor_chain_release, &chain_result));
    assert(chain_trace.stage_calls == 0u &&
           chain_trace.release_calls == 0u &&
           chain_outputs[0] == 100u && chain_outputs[1] == 200u);
    chain_result = 99u;
    assert(gomore_tensor_chain_run(
        NULL, NULL, 0u, 9u, 5u, NULL, 0u, false,
        NULL, NULL, &chain_result));
    assert(chain_result == 0u);

    const gomore_tensor_cell_configuration cell_configuration = {
        true, {10u, 20u}, {30u, 40u}, 50u,
    };
    const gomore_tensor_cell_providers cell_providers = {
        tensor_cell_slice_pair,
        tensor_cell_dual_activate,
        tensor_cell_gated_activate,
        tensor_cell_blend,
        tensor_cell_release,
    };
    uintptr_t cell_result = 99u;
    cell_trace = (tensor_cell_trace){0};
    assert(gomore_tensor_cell_run(
        &cell_context, &cell_configuration, 9u, 5u,
        &cell_providers, &cell_result));
    assert(cell_result == 3000u && cell_trace.slice_calls == 6u &&
           cell_trace.dual_calls == 2u &&
           cell_trace.gated_calls == 1u &&
           cell_trace.blend_calls == 1u &&
           cell_trace.release_calls == 15u);
    for (unsigned stage = 0u; stage < 3u; ++stage) {
        const unsigned primary_call = stage * 2u;
        const unsigned bias_call = primary_call + 1u;
        assert(cell_trace.slice_sources[primary_call][0] == 10u &&
               cell_trace.slice_sources[primary_call][1] == 20u &&
               cell_trace.slice_sources[bias_call][0] == 30u &&
               cell_trace.slice_sources[bias_call][1] == 40u &&
               cell_trace.slice_indices[primary_call] == stage &&
               cell_trace.slice_indices[bias_call] == stage &&
               cell_trace.activation_add_bias[stage]);
    }
    assert(cell_trace.dual_primary[0][0] == 100u &&
           cell_trace.dual_primary[0][1] == 101u &&
           cell_trace.dual_bias[0][0] == 200u &&
           cell_trace.dual_bias[0][1] == 201u &&
           cell_trace.dual_primary[1][0] == 110u &&
           cell_trace.dual_primary[1][1] == 111u &&
           cell_trace.dual_bias[1][0] == 210u &&
           cell_trace.dual_bias[1][1] == 211u &&
           cell_trace.gated_primary[0] == 120u &&
           cell_trace.gated_primary[1] == 121u &&
           cell_trace.gated_bias[0] == 220u &&
           cell_trace.gated_bias[1] == 221u &&
           cell_trace.gated_gate == 1000u &&
           cell_trace.blend_inputs[0] == 50u &&
           cell_trace.blend_inputs[1] == 1001u &&
           cell_trace.blend_inputs[2] == 2000u);
    static const uintptr_t expected_cell_releases[15] = {
        100u, 101u, 200u, 201u,
        110u, 111u, 210u, 211u,
        120u, 121u, 220u, 221u,
        1000u, 1001u, 2000u,
    };
    for (unsigned index = 0u; index < 15u; ++index) {
        assert(cell_trace.releases[index] == expected_cell_releases[index]);
    }

    gomore_tensor_cell_configuration no_bias_configuration =
        cell_configuration;
    no_bias_configuration.add_bias = false;
    cell_result = 99u;
    cell_trace = (tensor_cell_trace){0};
    assert(gomore_tensor_cell_run(
        &cell_context, &no_bias_configuration, 9u, 5u,
        &cell_providers, &cell_result));
    assert(cell_result == 3000u && cell_trace.slice_calls == 3u &&
           cell_trace.dual_calls == 2u &&
           cell_trace.gated_calls == 1u &&
           cell_trace.release_calls == 9u);
    for (unsigned stage = 0u; stage < 3u; ++stage) {
        assert(cell_trace.slice_sources[stage][0] == 10u &&
               cell_trace.slice_sources[stage][1] == 20u &&
               cell_trace.slice_indices[stage] == stage &&
               !cell_trace.activation_add_bias[stage]);
    }
    assert(cell_trace.dual_bias[0][0] == 0u &&
           cell_trace.dual_bias[0][1] == 0u &&
           cell_trace.dual_bias[1][0] == 0u &&
           cell_trace.dual_bias[1][1] == 0u &&
           cell_trace.gated_bias[0] == 0u &&
           cell_trace.gated_bias[1] == 0u);
    static const uintptr_t expected_no_bias_releases[9] = {
        100u, 101u, 110u, 111u, 120u, 121u,
        1000u, 1001u, 2000u,
    };
    for (unsigned index = 0u; index < 9u; ++index) {
        assert(cell_trace.releases[index] ==
               expected_no_bias_releases[index]);
    }

    cell_result = 99u;
    cell_trace = (tensor_cell_trace){0};
    cell_trace.fail_second_bias_slice = true;
    assert(!gomore_tensor_cell_run(
        &cell_context, &cell_configuration, 9u, 5u,
        &cell_providers, &cell_result));
    assert(cell_result == 99u && cell_trace.slice_calls == 4u &&
           cell_trace.dual_calls == 1u &&
           cell_trace.gated_calls == 0u &&
           cell_trace.blend_calls == 0u &&
           cell_trace.release_calls == 7u &&
           cell_trace.releases[4] == 110u &&
           cell_trace.releases[5] == 111u &&
           cell_trace.releases[6] == 1000u);

    gomore_tensor_cell_providers incomplete_cell_providers = cell_providers;
    incomplete_cell_providers.blend = NULL;
    cell_result = 99u;
    cell_trace = (tensor_cell_trace){0};
    assert(!gomore_tensor_cell_run(
        &cell_context, &cell_configuration, 9u, 5u,
        &incomplete_cell_providers, &cell_result));
    assert(cell_result == 99u && cell_trace.slice_calls == 0u &&
           cell_trace.release_calls == 0u);

    assert(gomore_tensor_map(NULL, NULL, 0u, plus_one));
    assert(!gomore_tensor_map(NULL, output, 1u, plus_one));
    assert(!gomore_tensor_softmax(source, output, 3u, NULL));
}
