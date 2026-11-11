#ifndef R1_NATIVE_MODEL_RECURRENT_SUPPORT_H
#define R1_NATIVE_MODEL_RECURRENT_SUPPORT_H
#include <stdint.h>
uint32_t r1_goodix_native_recurrent_round(float value);
uint32_t r1_goodix_native_recurrent_zero_point(float value,float minimum,float maximum);
uint32_t r1_goodix_native_recurrent_matrix(const void *inputs,const void *weights,void *outputs,uint32_t ignored,uint32_t columns,uint32_t rows,uint32_t input_zero,uint32_t weight_zero);
uint32_t r1_goodix_native_recurrent_range_adjust(void *minimum,void *maximum,uint32_t policy);
#endif
