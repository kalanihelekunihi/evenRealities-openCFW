#ifndef OPENR1_RECONSTRUCTED_GOMORE_TENSOR_RUNTIME_H
#define OPENR1_RECONSTRUCTED_GOMORE_TENSOR_RUNTIME_H

/* Owner-authorized clean-room reconstruction of twelve GoMore tensor executors
 * from the SHA-pinned R1 application image.  This is not GoMore source and
 * embeds no graph, model, weights, or opaque executable data. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef float (*gomore_tensor_unary_fn)(float value);
typedef float (*gomore_tensor_dequant_i16_fn)(int16_t value);

bool gomore_tensor_map(const float *source, float *destination, size_t count,
                       gomore_tensor_unary_fn operation);
bool gomore_tensor_multiply(const float *left, const float *right,
                            float *destination, size_t count);
bool gomore_tensor_add(const float *left, const float *right,
                       float *destination, size_t count);
bool gomore_tensor_blend(const float *factor, const float *first,
                         const float *second, float *destination,
                         size_t count);
bool gomore_tensor_leaky_relu(const float *source, float *destination,
                              size_t count, float negative_scale);
bool gomore_tensor_softmax(const float *source, float *destination,
                           size_t count, gomore_tensor_unary_fn exp_provider);
bool gomore_tensor_dequant_bias_add(
    const float *source, const int16_t *bias, float *destination, size_t count,
    gomore_tensor_dequant_i16_fn dequantize);
bool gomore_tensor_int8_float_dot(const int8_t *weights,
                                  size_t rows, size_t columns,
                                  float weight_scale,
                                  const float *input,
                                  float *output);
bool gomore_tensor_int8_float_affine(
    const int8_t *weights, size_t rows, size_t columns,
    float weight_scale, const float *input, const int16_t *bias,
    float *output, gomore_tensor_dequant_i16_fn dequantize);
bool gomore_tensor_dual_affine_activate(
    const int8_t *first_weights, const int8_t *second_weights,
    size_t rows, size_t columns,
    float first_weight_scale, float second_weight_scale,
    const float *input, bool add_bias,
    const int16_t *first_bias, const int16_t *second_bias,
    gomore_tensor_dequant_i16_fn dequantize,
    float *output, float *scratch,
    gomore_tensor_unary_fn activation);
bool gomore_tensor_gated_dual_affine_activate(
    const int8_t *first_weights, const int8_t *second_weights,
    size_t rows, size_t columns,
    float first_weight_scale, float second_weight_scale,
    const float *input, bool add_bias,
    const int16_t *first_bias, const int16_t *second_bias,
    gomore_tensor_dequant_i16_fn dequantize,
    const float *gate, float *output, float *scratch,
    gomore_tensor_unary_fn activation);
bool gomore_tensor_strided_copy_2d(
    const float *source, size_t source_count,
    size_t source_rows, size_t source_columns,
    uint8_t row_stride_selector, uint8_t column_stride_selector,
    float *destination, size_t destination_count,
    size_t destination_rows, size_t destination_columns);

#endif
