/*
 * Stock mappings:
 *   0x00091A0E map, 0x00091C80 multiply, 0x0009196E add,
 *   0x00091CCC leaky ReLU,
 *   0x00091EDC softmax, 0x000919BA int16 dequant bias add,
 *   0x00091D30 int8-by-float dot, 0x00065538 dual-affine/logistic,
 *   0x000655A8 gated dual-affine/tanh.
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
