#ifndef R1_NATIVE_SPO2_STATISTICS_H
#define R1_NATIVE_SPO2_STATISTICS_H
#include <stdint.h>
/* Native scalar S0 returns except count (R0) and the void output wrapper. */
float r1_goodix_native_array_sum(const void *input,uint32_t count);
float r1_goodix_native_array_mean(const void *input,uint32_t count);
float r1_goodix_native_array_mean_inline(const void *input,uint32_t count);
float r1_goodix_native_array_variance(const void *input,uint32_t count);
float r1_goodix_native_array_standard_deviation(float count,const void *input);
float r1_goodix_native_incremental_standard_deviation(const void *input,int32_t stride,uint32_t count);
void r1_goodix_native_window_standard_deviation(const void *record,void *output);
float r1_goodix_native_window_last(const void *record);
uint32_t r1_goodix_native_window_count(const void *record);
#endif
