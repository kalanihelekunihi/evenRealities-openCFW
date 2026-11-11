#ifndef R1_NATIVE_MODEL_QUANTIZATION_H
#define R1_NATIVE_MODEL_QUANTIZATION_H
#include <stdint.h>
uint32_t r1_goodix_native_quantize_round(float value);
uint32_t r1_goodix_native_quantize_index(float value,float minimum,float maximum);
void r1_goodix_native_quantization_parameters(float minimum,float maximum,void *low,void *high,void *step,void *inverse);
uint32_t r1_goodix_native_graph_quantize(const void *operation,const void *inputs,const void *outputs);
uint32_t r1_goodix_native_graph_quantized_add(const void *operation,const void *inputs,const void *outputs);
uint32_t r1_goodix_native_graph_dequantize(const void *operation,const void *inputs,const void *outputs);
extern const uint32_t r1_goodix_graph_quantizer_executor_address;
extern const uint32_t r1_goodix_graph_pair_executor_address;
extern const uint32_t r1_goodix_graph_vector_executor_address;
#endif
