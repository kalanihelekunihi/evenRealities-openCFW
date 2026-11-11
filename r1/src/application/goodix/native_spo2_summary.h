#ifndef R1_NATIVE_SPO2_SUMMARY_H
#define R1_NATIVE_SPO2_SUMMARY_H
#include <stdint.h>
void r1_goodix_native_i16_mean(const void *input,uint32_t count,void *output);
void r1_goodix_native_float_mean(const void *input,uint32_t count,void *output);
void r1_goodix_native_i16_window_mean(const void *record,void *output);
void r1_goodix_native_float_window_mean(const void *record,void *output);
void r1_goodix_native_sum_squares(const void *input,uint32_t count,void *output);
void r1_goodix_native_dot_product(const void *first,const void *second,uint32_t count,void *output);
void r1_goodix_native_float_min_index(const void *input,uint32_t count,void *minimum,void *index);
float r1_goodix_native_window_correlation(const void *first,const void *second,uint32_t count);
void r1_goodix_native_peak_pair_indices(uint32_t iteration,const void *histories,void *starts,void *ends,void *number);
void r1_goodix_native_spo2_pair_statistics(const void *input,uint32_t count,const void *descriptor,const void *starts,const void *ends,uint32_t pairs,void *output);
void r1_goodix_native_spo2_outlier_count(const void *input,uint32_t count,const void *descriptor,void *output);
uint32_t r1_goodix_native_spo2_channel_statistics(const void *input,uint32_t count,const void *starts,const void *ends,uint32_t pairs,const void *descriptor,void *output);
void r1_goodix_native_spo2_motion_summary(const void *descriptor,const void *aggregate,void *summary);
void r1_goodix_native_spo2_aux_summary(const void *descriptor,const void *aggregate,void *summary,uint32_t incoming);
uint32_t r1_goodix_native_spo2_common_summary(const void *descriptor,const void *aggregate,void *summary);
uint32_t r1_goodix_native_spo2_channel_summary(const void *channel,const void *histories,const void *descriptor,uint32_t iteration,void *summary);
void r1_goodix_spo2_summary(const void *descriptor,void *aggregate,uint32_t iteration,void *summary);
#endif
