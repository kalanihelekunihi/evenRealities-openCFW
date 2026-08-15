/*
 * Stock mappings:
 *   0x00091A0E map, 0x00091C80 multiply, 0x00091CCC leaky ReLU,
 *   0x00091EDC softmax, 0x000919BA int16 dequant bias add,
 *   0x00091D30 int8-by-float dot.
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
