#ifndef R1_NATIVE_MODEL_OPERATORS_H
#define R1_NATIVE_MODEL_OPERATORS_H
#include <stdint.h>
uint32_t r1_goodix_native_graph_pool(const void *operation,const void *inputs,const void *outputs);
uint32_t r1_goodix_native_graph_float_add(const void *operation,const void *inputs,const void *outputs);
extern const uint32_t r1_goodix_graph_pool_executor_address;
extern const uint32_t r1_goodix_graph_operator_executor_address;
#endif
