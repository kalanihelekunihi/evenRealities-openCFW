#ifndef R1_NATIVE_MODEL_I8_CONVOLUTION_H
#define R1_NATIVE_MODEL_I8_CONVOLUTION_H
#include <stdint.h>
uint32_t r1_goodix_native_i8_round(float value);
uint32_t r1_goodix_native_i8_range_adjust(void *minimum,void *maximum,uint32_t policy);
uint32_t r1_goodix_native_i8_clip(uint32_t code);
uint32_t r1_goodix_native_graph_i8_convolution(const void *operation,const void *inputs,const void *outputs);
extern const uint32_t r1_goodix_graph_aligned_executor_address;
#endif
