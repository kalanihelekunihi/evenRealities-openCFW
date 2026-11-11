#ifndef R1_GOODIX_NATIVE_SPO2_RATIO_H
#define R1_GOODIX_NATIVE_SPO2_RATIO_H
#include <stdint.h>
/* Requires the initialized aggregate and full125-sample optical window. */
uint32_t r1_goodix_spo2_ratio(void *context,uint32_t iteration,const void *descriptor);
#endif
