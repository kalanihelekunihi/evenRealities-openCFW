#include <stdint.h>
#include "../../vendor/quantized_runtime/quantized_runtime.h"

extern const uint32_t r1_goodix_graph_convolution_executor_address;
extern const uint32_t r1_goodix_graph_aligned_executor_address;
extern const uint32_t r1_goodix_graph_pool_executor_address;
extern const uint32_t r1_goodix_graph_operator_executor_address;
extern const uint32_t r1_goodix_graph_quantizer_executor_address;
extern const uint32_t r1_goodix_graph_pair_executor_address;
extern const uint32_t r1_goodix_graph_vector_executor_address;
extern const uint32_t r1_goodix_graph_transform_executor_address;
extern const uint32_t r1_goodix_graph_alternate_pool_executor_address;
extern const uint32_t r1_goodix_graph_tail_vector_executor_address;
extern const uint32_t r1_goodix_graph_merge_executor_address;
extern const uint32_t r1_goodix_model_dense_executor_address;
extern const uint32_t r1_goodix_model_recurrent_executor_address;
extern const uint32_t r1_goodix_model_softmax_executor_address;
extern const uint32_t r1_goodix_model_vector_executor_address;

/* Native graph builders store linked target-ABI C operator addresses. The
 * checked executor uses typed tensor operators with matching descriptor
 * roles. Keep the underlying graph bytes untouched and translate tokens
 * only while constructing a borrowed plan. */
uint32_t r1_goodix_hba_stage_token_rewrite(void *context,uint32_t token)
{
    (void)context;
#define MAP(native_,typed_) \
    if (token==(native_)) return (uint32_t)(uintptr_t)&(typed_)
    MAP(r1_goodix_graph_convolution_executor_address,
        quantized_runtime_float_conv1d_execute_target);
    MAP(r1_goodix_graph_aligned_executor_address,
        quantized_runtime_i8_conv1d_execute_target);
    MAP(r1_goodix_graph_pool_executor_address,
        quantized_runtime_pooling_execute);
    MAP(r1_goodix_graph_operator_executor_address,
        quantized_runtime_float_add_execute);
    MAP(r1_goodix_graph_quantizer_executor_address,
        quantized_runtime_float_to_int8_quantize);
    MAP(r1_goodix_graph_pair_executor_address,
        quantized_runtime_int8_add_execute);
    MAP(r1_goodix_graph_vector_executor_address,
        quantized_runtime_int8_to_float_execute);
    MAP(r1_goodix_graph_transform_executor_address,
        quantized_runtime_float_strided_copy_2d_execute);
    MAP(r1_goodix_graph_alternate_pool_executor_address,
        quantized_runtime_float_pool_1d_execute);
    MAP(r1_goodix_graph_tail_vector_executor_address,
        quantized_runtime_float_multiply_execute);
    MAP(r1_goodix_graph_merge_executor_address,
        quantized_runtime_int8_concatenate_execute);
    MAP(r1_goodix_model_dense_executor_address,
        quantized_runtime_float_dense_execute_target);
    MAP(r1_goodix_model_recurrent_executor_address,
        quantized_runtime_recurrent_execute_target);
    MAP(r1_goodix_model_softmax_executor_address,
        quantized_runtime_float_softmax_execute);
    MAP(r1_goodix_model_vector_executor_address,
        quantized_runtime_float_concatenate_two_execute);
#undef MAP
    return token;
}
