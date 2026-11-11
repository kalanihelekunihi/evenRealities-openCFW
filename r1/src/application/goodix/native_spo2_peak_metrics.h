#ifndef R1_NATIVE_SPO2_PEAK_METRICS_H
#define R1_NATIVE_SPO2_PEAK_METRICS_H
#include <stdint.h>
/* Native0x37a84. Values/indices require one extra sentinel slot. */
void r1_goodix_native_peak_feature_metrics(void *values,void *indices,uint32_t count,uint32_t length,void *rms,void *quality);
#endif
