#ifndef R1_GOODIX_NATIVE_SPO2_SPECTRAL_H
#define R1_GOODIX_NATIVE_SPO2_SPECTRAL_H
#include <stdint.h>
/* Requires the initialized, full 125-sample rolling window. */
uint32_t r1_goodix_spo2_spectral(void *context, const void *descriptor);
#endif
