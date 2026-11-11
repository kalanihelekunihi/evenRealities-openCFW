#ifndef R1_NATIVE_SPO2_QUALITY_H
#define R1_NATIVE_SPO2_QUALITY_H
#include <stdint.h>
uint32_t r1_goodix_spo2_quality(const void *descriptor,void *context,uint32_t iteration,void *summary);
float r1_goodix_native_quality_logistic(float value,float pivot,float below,float above);
#endif
