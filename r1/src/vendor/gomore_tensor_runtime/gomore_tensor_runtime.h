#ifndef OPENR1_RECONSTRUCTED_GOMORE_TENSOR_RUNTIME_H
#define OPENR1_RECONSTRUCTED_GOMORE_TENSOR_RUNTIME_H

/* Owner-authorized clean-room reconstruction of nineteen GoMore tensor executors
 * from the SHA-pinned R1 application image.  This is not GoMore source and
 * embeds no graph, model, weights, or opaque executable data. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef float (*gomore_tensor_unary_fn)(float value);
typedef float (*gomore_tensor_binary_fn)(float left, float right);
typedef float (*gomore_tensor_dequant_i16_fn)(int16_t value);
typedef uint32_t (*gomore_tensor_half_bits_fn)(uint16_t value);
typedef void (*gomore_tensor_release_fn)(uintptr_t runtime_binding,
                                         uintptr_t tensor_binding);
typedef struct {
    uintptr_t parameter0;
    uintptr_t parameter1;
    uintptr_t parameter2;
    uintptr_t parameter3;
} gomore_tensor_chain_stage;
typedef uintptr_t (*gomore_tensor_chain_stage_fn)(
    const void *configuration_context,
    uintptr_t runtime_binding, uintptr_t input_binding,
    uintptr_t parameter0, uintptr_t parameter1,
    uintptr_t parameter2, uintptr_t parameter3,
    uintptr_t output_candidate_binding);
typedef bool (*gomore_tensor_cell_slice_pair_fn)(
    const void *context, uintptr_t runtime_binding,
    uintptr_t first_source, uintptr_t second_source,
    uint32_t index, uintptr_t outputs[2]);
typedef uintptr_t (*gomore_tensor_cell_dual_fn)(
    const void *context, uintptr_t runtime_binding,
    uintptr_t input_binding, uintptr_t first_primary,
    uintptr_t first_bias, uintptr_t shared_binding,
    uintptr_t second_primary, uintptr_t second_bias,
    bool add_bias);
typedef uintptr_t (*gomore_tensor_cell_gated_fn)(
    const void *context, uintptr_t runtime_binding,
    uintptr_t input_binding, uintptr_t first_primary,
    uintptr_t first_bias, uintptr_t shared_binding,
    uintptr_t second_primary, uintptr_t second_bias,
    uintptr_t gate_binding, bool add_bias);
typedef uintptr_t (*gomore_tensor_cell_blend_fn)(
    const void *context, uintptr_t runtime_binding,
    uintptr_t factor_binding, uintptr_t first_binding,
    uintptr_t second_binding);
typedef struct {
    bool add_bias;
    uintptr_t primary_sources[2];
    uintptr_t bias_sources[2];
    uintptr_t shared_binding;
} gomore_tensor_cell_configuration;
typedef struct {
    gomore_tensor_cell_slice_pair_fn slice_pair;
    gomore_tensor_cell_dual_fn dual_activate;
    gomore_tensor_cell_gated_fn gated_activate;
    gomore_tensor_cell_blend_fn blend;
    gomore_tensor_release_fn release;
} gomore_tensor_cell_providers;

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
bool gomore_tensor_pool_1d(
    const float *source, size_t source_count,
    size_t source_rows, size_t source_columns,
    float *destination, size_t destination_count,
    size_t destination_rows, size_t destination_columns,
    uint8_t mode, uint8_t window, uint8_t stride, uint8_t padding,
    gomore_tensor_binary_fn maximum);
bool gomore_tensor_batch_normalize_half(
    const float *source, size_t source_count,
    const uint16_t *dimensions, size_t rank,
    uint16_t epsilon_half,
    const uint16_t *scale_half, const uint16_t *offset_half,
    const uint16_t *variance_half, const uint16_t *mean_half,
    size_t parameter_count,
    float *destination, size_t destination_count,
    gomore_tensor_half_bits_fn half_to_float_bits,
    gomore_tensor_unary_fn square_root);
bool gomore_tensor_conv1d_half(
    const float *source, size_t source_count,
    size_t input_channels, size_t input_width,
    const uint16_t *weights_half, size_t weight_count,
    size_t output_channels, size_t kernel_width,
    size_t stride, size_t padding,
    float *weight_scratch, size_t weight_scratch_count,
    float *destination, size_t destination_count,
    size_t *output_width,
    gomore_tensor_half_bits_fn half_to_float_bits);
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
    uintptr_t input_binding, gomore_tensor_release_fn release);
bool gomore_tensor_chain_run(
    const void *configuration_context,
    const gomore_tensor_chain_stage *stages, size_t stage_count,
    uintptr_t runtime_binding, uintptr_t initial_input_binding,
    uintptr_t *output_bindings, size_t output_capacity,
    bool release_initial_input,
    gomore_tensor_chain_stage_fn run_stage,
    gomore_tensor_release_fn release,
    uintptr_t *result_binding);
/* 0x000653E6: three-slice dual/gated recurrent tensor cell. */
bool gomore_tensor_cell_run(
    const void *context,
    const gomore_tensor_cell_configuration *configuration,
    uintptr_t runtime_binding, uintptr_t input_binding,
    const gomore_tensor_cell_providers *providers,
    uintptr_t *result_binding);

#endif
