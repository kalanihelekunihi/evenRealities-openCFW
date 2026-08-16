/*
 * Stock mappings:
 *   0x00091A0E map, 0x00091C80 multiply, 0x0009196E add,
 *   0x00091CCC leaky ReLU,
 *   0x00091EDC softmax, 0x000919BA int16 dequant bias add,
 *   0x00091D30 int8-by-float dot, 0x00065538 dual-affine/logistic,
 *   0x000655A8 gated dual-affine/tanh,
 *   0x000651CA half-parameter batch normalization,
 *   0x00091B08 half-weight one-dimensional convolution,
 *   0x00065304 half-weight convolution plus per-row half bias,
 *   0x00065376 sequential tensor-stage chain and ownership handoff,
 *   0x000653E6 three-slice dual/gated recurrent tensor cell.
 * Allocation/in-place selection through stock 0x91D9C is replaced by an
 * explicit caller-owned destination.  Arithmetic and iteration order match
 * the recovered bodies.
 */

#include "gomore_tensor_runtime/gomore_tensor_runtime.h"

static bool arrays_valid(const void *source, const void *destination,
                         size_t count) {
    return count == 0u || (source != NULL && destination != NULL);
}

bool gomore_tensor_map(const float *source, float *destination, size_t count,
                       gomore_tensor_unary_fn operation) {
    if (!arrays_valid(source, destination, count) || operation == NULL) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = operation(source[index]);
    }
    return true;
}

bool gomore_tensor_multiply(const float *left, const float *right,
                            float *destination, size_t count) {
    if (!arrays_valid(left, destination, count) ||
            (right == NULL && count != 0u)) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = left[index] * right[index];
    }
    return true;
}

bool gomore_tensor_add(const float *left, const float *right,
                       float *destination, size_t count) {
    if (!arrays_valid(left, destination, count) ||
            (right == NULL && count != 0u)) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = left[index] + right[index];
    }
    return true;
}

bool gomore_tensor_blend(const float *factor, const float *first,
                         const float *second, float *destination,
                         size_t count) {
    if (!arrays_valid(factor, destination, count) ||
            (first == NULL && count != 0u) ||
            (second == NULL && count != 0u)) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        const float weighted_first = factor[index] * first[index];
        const float complement = 1.0f - factor[index];
        const float weighted_second = complement * second[index];
        destination[index] = weighted_first + weighted_second;
    }
    return true;
}

bool gomore_tensor_leaky_relu(const float *source, float *destination,
                              size_t count, float negative_scale) {
    if (!arrays_valid(source, destination, count)) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        const float value = source[index];
        destination[index] = value >= 0.0f ? value : value * negative_scale;
    }
    return true;
}

bool gomore_tensor_softmax(const float *source, float *destination,
                           size_t count, gomore_tensor_unary_fn exp_provider) {
    if (!arrays_valid(source, destination, count) || exp_provider == NULL) {
        return false;
    }
    float sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        sum += exp_provider(source[index]);
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = exp_provider(source[index]) / sum;
    }
    return true;
}

bool gomore_tensor_dequant_bias_add(
    const float *source, const int16_t *bias, float *destination, size_t count,
    gomore_tensor_dequant_i16_fn dequantize) {
    if (!arrays_valid(source, destination, count) ||
            (bias == NULL && count != 0u) || dequantize == NULL) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = source[index] + dequantize(bias[index]);
    }
    return true;
}

bool gomore_tensor_int8_float_dot(const int8_t *weights,
                                  size_t rows, size_t columns,
                                  float weight_scale,
                                  const float *input,
                                  float *output) {
    if ((weights == NULL && rows != 0u && columns != 0u) ||
            (input == NULL && columns != 0u) ||
            (output == NULL && rows != 0u)) {
        return false;
    }
    for (size_t row = 0u; row < rows; ++row) {
        float value = 0.0f;
        for (size_t column = 0u; column < columns; ++column) {
            value += (float)weights[row * columns + column] *
                     weight_scale * input[column];
        }
        output[row] = value;
    }
    return true;
}

bool gomore_tensor_int8_float_affine(
    const int8_t *weights, size_t rows, size_t columns,
    float weight_scale, const float *input, const int16_t *bias,
    float *output, gomore_tensor_dequant_i16_fn dequantize) {
    if (bias != NULL && dequantize == NULL) {
        return false;
    }
    if (!gomore_tensor_int8_float_dot(weights, rows, columns,
                                      weight_scale, input, output)) {
        return false;
    }
    if (bias == NULL) {
        return true;
    }
    for (size_t index = 0u; index < rows; ++index) {
        output[index] += dequantize(bias[index]);
    }
    return true;
}

static bool dual_affine_prepare(
    const int8_t *first_weights, const int8_t *second_weights,
    size_t rows, size_t columns,
    float first_weight_scale, float second_weight_scale,
    const float *input, bool add_bias,
    const int16_t *first_bias, const int16_t *second_bias,
    gomore_tensor_dequant_i16_fn dequantize,
    float *output, float *scratch) {
    if ((rows != 0u && output == scratch) ||
            (add_bias && (first_bias == NULL || second_bias == NULL ||
                          dequantize == NULL))) {
        return false;
    }
    if (!gomore_tensor_int8_float_dot(
            first_weights, rows, columns, first_weight_scale, input, output) ||
            !gomore_tensor_int8_float_dot(
                second_weights, rows, columns, second_weight_scale,
                input, scratch)) {
        return false;
    }
    if (add_bias &&
            (!gomore_tensor_dequant_bias_add(
                output, first_bias, output, rows, dequantize) ||
             !gomore_tensor_dequant_bias_add(
                scratch, second_bias, scratch, rows, dequantize))) {
        return false;
    }
    return true;
}

bool gomore_tensor_dual_affine_activate(
    const int8_t *first_weights, const int8_t *second_weights,
    size_t rows, size_t columns,
    float first_weight_scale, float second_weight_scale,
    const float *input, bool add_bias,
    const int16_t *first_bias, const int16_t *second_bias,
    gomore_tensor_dequant_i16_fn dequantize,
    float *output, float *scratch,
    gomore_tensor_unary_fn activation) {
    if (activation == NULL ||
            !dual_affine_prepare(
                first_weights, second_weights, rows, columns,
                first_weight_scale, second_weight_scale, input, add_bias,
                first_bias, second_bias, dequantize, output, scratch) ||
            !gomore_tensor_add(output, scratch, output, rows)) {
        return false;
    }
    return gomore_tensor_map(output, output, rows, activation);
}

bool gomore_tensor_gated_dual_affine_activate(
    const int8_t *first_weights, const int8_t *second_weights,
    size_t rows, size_t columns,
    float first_weight_scale, float second_weight_scale,
    const float *input, bool add_bias,
    const int16_t *first_bias, const int16_t *second_bias,
    gomore_tensor_dequant_i16_fn dequantize,
    const float *gate, float *output, float *scratch,
    gomore_tensor_unary_fn activation) {
    if (activation == NULL ||
            !dual_affine_prepare(
                first_weights, second_weights, rows, columns,
                first_weight_scale, second_weight_scale, input, add_bias,
                first_bias, second_bias, dequantize, output, scratch) ||
            !gomore_tensor_multiply(scratch, gate, scratch, rows) ||
            !gomore_tensor_add(output, scratch, output, rows)) {
        return false;
    }
    return gomore_tensor_map(output, output, rows, activation);
}

bool gomore_tensor_strided_copy_2d(
    const float *source, size_t source_count,
    size_t source_rows, size_t source_columns,
    uint8_t row_stride_selector, uint8_t column_stride_selector,
    float *destination, size_t destination_count,
    size_t destination_rows, size_t destination_columns) {
    if (row_stride_selector > 2u || column_stride_selector > 2u ||
            (source_rows != 0u && source_columns > SIZE_MAX / source_rows) ||
            (destination_rows != 0u &&
             destination_columns > SIZE_MAX / destination_rows)) {
        return false;
    }
    const size_t output_count = destination_rows * destination_columns;
    if (!arrays_valid(source, destination, output_count) ||
            output_count > destination_count) {
        return false;
    }
    const size_t strides[3] = {
        source_rows * source_columns, source_columns, 1u
    };
    const size_t row_stride = strides[row_stride_selector];
    const size_t column_stride = strides[column_stride_selector];
    for (size_t row = 0u; row < destination_rows; ++row) {
        for (size_t column = 0u; column < destination_columns; ++column) {
            if ((column != 0u && column_stride > SIZE_MAX / column) ||
                    (row != 0u && row_stride > SIZE_MAX / row)) {
                return false;
            }
            const size_t column_offset = column * column_stride;
            const size_t row_offset = row * row_stride;
            if (column_offset > SIZE_MAX - row_offset) {
                return false;
            }
            const size_t source_index = column_offset + row_offset;
            if (source_index >= source_count) {
                return false;
            }
            destination[row * destination_columns + column] =
                source[source_index];
        }
    }
    return true;
}

bool gomore_tensor_pool_1d(
    const float *source, size_t source_count,
    size_t source_rows, size_t source_columns,
    float *destination, size_t destination_count,
    size_t destination_rows, size_t destination_columns,
    uint8_t mode, uint8_t window, uint8_t stride, uint8_t padding,
    gomore_tensor_binary_fn maximum) {
    if ((source_rows != 0u && source_columns > SIZE_MAX / source_rows) ||
            (destination_rows != 0u &&
             destination_columns > SIZE_MAX / destination_rows)) {
        return false;
    }
    const size_t required_source = source_rows * source_columns;
    const size_t required_destination =
        destination_rows * destination_columns;
    if (required_source > source_count ||
            required_destination > destination_count ||
            (required_source != 0u && source == NULL) ||
            (required_destination != 0u && destination == NULL) ||
            destination_rows > source_rows ||
            (mode == 0u && maximum == NULL)) {
        return false;
    }
    if (mode > 1u) {
        return true;
    }
    for (size_t output_column = 0u;
            output_column < destination_columns; ++output_column) {
        if (stride != 0u && output_column > SIZE_MAX / (size_t)stride) {
            return false;
        }
        const size_t unpadded_start = output_column * (size_t)stride;
        if (unpadded_start < (size_t)padding) {
            return false;
        }
        const size_t start = unpadded_start - (size_t)padding;
        size_t end = start + (size_t)window;
        if (end < start || end > source_columns) {
            end = source_columns;
        }
        for (size_t row = 0u; row < destination_rows; ++row) {
            const size_t destination_index =
                row * destination_columns + output_column;
            if (mode == 0u) {
                float value = -3.4028234663852886e38f;
                for (size_t input_column = start;
                        input_column < end; ++input_column) {
                    value = maximum(
                        value, source[row * source_columns + input_column]);
                }
                destination[destination_index] = value;
            } else {
                float sum = 0.0f;
                size_t count = 0u;
                for (size_t input_column = start;
                        input_column < end; ++input_column) {
                    sum += source[row * source_columns + input_column];
                    ++count;
                }
                destination[destination_index] = sum / (float)count;
            }
        }
    }
    return true;
}

static float tensor_bits_float(uint32_t bits) {
    union {
        uint32_t u;
        float f;
    } value;
    value.u = bits;
    return value.f;
}

bool gomore_tensor_batch_normalize_half(
    const float *source, size_t source_count,
    const uint16_t *dimensions, size_t rank,
    uint16_t epsilon_half,
    const uint16_t *scale_half, const uint16_t *offset_half,
    const uint16_t *variance_half, const uint16_t *mean_half,
    size_t parameter_count,
    float *destination, size_t destination_count,
    gomore_tensor_half_bits_fn half_to_float_bits,
    gomore_tensor_unary_fn square_root) {
    if (dimensions == NULL || (rank != 2u && rank != 3u) ||
            half_to_float_bits == NULL || square_root == NULL) {
        return false;
    }
    size_t element_count = 1u;
    for (size_t index = 0u; index < rank; ++index) {
        if (dimensions[index] != 0u &&
                element_count > SIZE_MAX / dimensions[index]) {
            return false;
        }
        element_count *= dimensions[index];
    }
    const size_t channels = dimensions[rank - 2u];
    const size_t width = dimensions[rank - 1u];
    const size_t outer = rank == 2u ? 1u : dimensions[0];
    if (source_count < element_count || destination_count < element_count ||
            parameter_count < channels ||
            (element_count != 0u &&
             (source == NULL || destination == NULL)) ||
            (channels != 0u &&
             (scale_half == NULL || offset_half == NULL ||
              variance_half == NULL || mean_half == NULL))) {
        return false;
    }

    const float epsilon =
        tensor_bits_float(half_to_float_bits(epsilon_half));
    for (size_t outer_index = 0u; outer_index < outer; ++outer_index) {
        for (size_t channel = 0u; channel < channels; ++channel) {
            const float variance =
                tensor_bits_float(half_to_float_bits(
                    variance_half[channel]));
            const float denominator = square_root(variance + epsilon);
            for (size_t column = 0u; column < width; ++column) {
                const size_t index =
                    outer_index * channels * width + channel * width +
                    column;
                const float mean = tensor_bits_float(
                    half_to_float_bits(mean_half[channel]));
                float value = (source[index] - mean) / denominator;
                const float scale = tensor_bits_float(
                    half_to_float_bits(scale_half[channel]));
                value *= scale;
                const float offset = tensor_bits_float(
                    half_to_float_bits(offset_half[channel]));
                destination[index] = value + offset;
            }
        }
    }
    return true;
}

bool gomore_tensor_conv1d_half(
    const float *source, size_t source_count,
    size_t input_channels, size_t input_width,
    const uint16_t *weights_half, size_t weight_count,
    size_t output_channels, size_t kernel_width,
    size_t stride, size_t padding,
    float *weight_scratch, size_t weight_scratch_count,
    float *destination, size_t destination_count,
    size_t *output_width,
    gomore_tensor_half_bits_fn half_to_float_bits) {
    if (stride == 0u || output_width == NULL ||
            half_to_float_bits == NULL ||
            (padding != 0u && padding > (SIZE_MAX - input_width) / 2u)) {
        return false;
    }
    const size_t padded_width = input_width + padding * 2u;
    if (padded_width < kernel_width ||
            (input_channels != 0u &&
             input_width > SIZE_MAX / input_channels) ||
            (input_channels != 0u &&
             kernel_width > SIZE_MAX / input_channels)) {
        return false;
    }
    const size_t required_source = input_channels * input_width;
    const size_t weights_per_output = input_channels * kernel_width;
    if (output_channels != 0u &&
            weights_per_output > SIZE_MAX / output_channels) {
        return false;
    }
    const size_t required_weights = output_channels * weights_per_output;
    const size_t produced_width =
        (padded_width - kernel_width) / stride + 1u;
    if (output_channels != 0u &&
            produced_width > SIZE_MAX / output_channels) {
        return false;
    }
    const size_t required_destination = output_channels * produced_width;
    if (source_count < required_source || weight_count < required_weights ||
            weight_scratch_count < required_weights ||
            destination_count < required_destination ||
            (required_source != 0u && source == NULL) ||
            (required_weights != 0u &&
             (weights_half == NULL || weight_scratch == NULL)) ||
            (required_destination != 0u && destination == NULL)) {
        return false;
    }

    for (size_t index = 0u; index < required_weights; ++index) {
        weight_scratch[index] =
            tensor_bits_float(half_to_float_bits(weights_half[index]));
    }

    size_t output_index = 0u;
    for (size_t output_channel = 0u;
            output_channel < output_channels; ++output_channel) {
        for (size_t position = 0u; position < produced_width; ++position) {
            const size_t unpadded = position * stride;
            float sum = 0.0f;
            for (size_t input_channel = 0u;
                    input_channel < input_channels; ++input_channel) {
                const size_t kernel_begin =
                    unpadded < padding ? padding - unpadded : 0u;
                const size_t input_limit = padding + input_width;
                size_t kernel_end = 0u;
                if (unpadded < input_limit) {
                    const size_t available = input_limit - unpadded;
                    kernel_end = available < kernel_width
                        ? available : kernel_width;
                }
                for (size_t kernel = kernel_begin;
                        kernel < kernel_end; ++kernel) {
                    const size_t source_column =
                        unpadded + kernel - padding;
                    const size_t source_index =
                        input_channel * input_width + source_column;
                    const size_t weight_index =
                        output_channel * weights_per_output +
                        input_channel * kernel_width + kernel;
                    sum += source[source_index] * weight_scratch[weight_index];
                }
            }
            destination[output_index++] = sum;
        }
    }
    *output_width = produced_width;
    return true;
}

bool gomore_tensor_conv1d_half_bias(
    const float *source, size_t source_count,
    size_t input_channels, size_t input_width,
    const uint16_t *weights_half, size_t weight_count,
    size_t output_channels, size_t kernel_width,
    size_t stride, size_t padding,
    const uint16_t *bias_half, size_t bias_count,
    float *weight_scratch, size_t weight_scratch_count,
    float *destination, size_t destination_count,
    size_t *output_width,
    gomore_tensor_half_bits_fn half_to_float_bits,
    bool release_input, uintptr_t runtime_binding,
    uintptr_t input_binding, gomore_tensor_release_fn release) {
    if ((bias_half != NULL && bias_count < output_channels) ||
            (bias_half != NULL && half_to_float_bits == NULL) ||
            (release_input && release == NULL)) {
        return false;
    }
    if (!gomore_tensor_conv1d_half(
            source, source_count, input_channels, input_width,
            weights_half, weight_count, output_channels, kernel_width,
            stride, padding, weight_scratch, weight_scratch_count,
            destination, destination_count, output_width,
            half_to_float_bits)) {
        return false;
    }
    if (bias_half != NULL) {
        for (size_t output_channel = 0u;
                output_channel < output_channels; ++output_channel) {
            for (size_t column = 0u; column < *output_width; ++column) {
                const float bias = tensor_bits_float(
                    half_to_float_bits(bias_half[output_channel]));
                const size_t index = output_channel * *output_width + column;
                destination[index] = bias + destination[index];
            }
        }
    }
    if (release_input) {
        release(runtime_binding, input_binding);
    }
    return true;
}

bool gomore_tensor_chain_run(
    const void *configuration_context,
    const gomore_tensor_chain_stage *stages, size_t stage_count,
    uintptr_t runtime_binding, uintptr_t initial_input_binding,
    uintptr_t *output_bindings, size_t output_capacity,
    bool release_initial_input,
    gomore_tensor_chain_stage_fn run_stage,
    gomore_tensor_release_fn release,
    uintptr_t *result_binding) {
    if (result_binding == NULL || output_capacity < stage_count ||
            (stage_count != 0u &&
             (stages == NULL || output_bindings == NULL ||
              run_stage == NULL || release == NULL))) {
        return false;
    }

    uintptr_t input_binding = initial_input_binding;
    uintptr_t result = 0u;
    for (size_t index = 0u; index < stage_count; ++index) {
        const uintptr_t output_candidate = output_bindings[index];
        result = run_stage(
            configuration_context, runtime_binding, input_binding,
            stages[index].parameter0, stages[index].parameter1,
            stages[index].parameter2, stages[index].parameter3,
            output_candidate);
        release(runtime_binding, output_candidate);
        output_bindings[index] = result;
        if (index == 0u && release_initial_input) {
            release(runtime_binding, initial_input_binding);
        }
        input_binding = result;
    }
    *result_binding = result;
    return true;
}

static void tensor_cell_release_pair(
    const gomore_tensor_cell_providers *providers,
    uintptr_t runtime_binding, const uintptr_t pair[2]) {
    providers->release(runtime_binding, pair[0]);
    providers->release(runtime_binding, pair[1]);
}

static void tensor_cell_release_earlier_activations(
    const gomore_tensor_cell_providers *providers,
    uintptr_t runtime_binding, uint32_t next_index,
    uintptr_t first_activation, uintptr_t second_activation) {
    if (next_index > 0u) {
        providers->release(runtime_binding, first_activation);
    }
    if (next_index > 1u) {
        providers->release(runtime_binding, second_activation);
    }
}

bool gomore_tensor_cell_run(
    const void *context,
    const gomore_tensor_cell_configuration *configuration,
    uintptr_t runtime_binding, uintptr_t input_binding,
    const gomore_tensor_cell_providers *providers,
    uintptr_t *result_binding) {
    if (configuration == NULL || providers == NULL || result_binding == NULL ||
            providers->slice_pair == NULL ||
            providers->dual_activate == NULL ||
            providers->gated_activate == NULL ||
            providers->blend == NULL || providers->release == NULL) {
        return false;
    }

    uintptr_t first_activation = 0u;
    uintptr_t second_activation = 0u;
    uintptr_t third_activation = 0u;
    for (uint32_t index = 0u; index < 3u; ++index) {
        uintptr_t primary[2] = {0u, 0u};
        uintptr_t bias[2] = {0u, 0u};
        if (!providers->slice_pair(
                context, runtime_binding,
                configuration->primary_sources[0],
                configuration->primary_sources[1], index, primary)) {
            tensor_cell_release_earlier_activations(
                providers, runtime_binding, index,
                first_activation, second_activation);
            return false;
        }
        if (configuration->add_bias &&
                !providers->slice_pair(
                    context, runtime_binding,
                    configuration->bias_sources[0],
                    configuration->bias_sources[1], index, bias)) {
            tensor_cell_release_pair(providers, runtime_binding, primary);
            tensor_cell_release_earlier_activations(
                providers, runtime_binding, index,
                first_activation, second_activation);
            return false;
        }

        uintptr_t activation;
        if (index < 2u) {
            activation = providers->dual_activate(
                context, runtime_binding, input_binding,
                primary[0], bias[0], configuration->shared_binding,
                primary[1], bias[1], configuration->add_bias);
        } else {
            activation = providers->gated_activate(
                context, runtime_binding, input_binding,
                primary[0], bias[0], configuration->shared_binding,
                primary[1], bias[1], first_activation,
                configuration->add_bias);
        }

        tensor_cell_release_pair(providers, runtime_binding, primary);
        if (configuration->add_bias) {
            tensor_cell_release_pair(providers, runtime_binding, bias);
        }
        if (index == 0u) {
            first_activation = activation;
        } else if (index == 1u) {
            second_activation = activation;
        } else {
            third_activation = activation;
        }
    }

    providers->release(runtime_binding, first_activation);
    const uintptr_t result = providers->blend(
        context, runtime_binding, configuration->shared_binding,
        second_activation, third_activation);
    providers->release(runtime_binding, second_activation);
    providers->release(runtime_binding, third_activation);
    *result_binding = result;
    return true;
}
