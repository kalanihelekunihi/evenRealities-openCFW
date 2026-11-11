#ifndef R1_NATIVE_SPO2_SELECT_H
#define R1_NATIVE_SPO2_SELECT_H
#include <stdint.h>
/* Native0x36f88, consumed by goodix_spo2_calc. */
void r1_goodix_spo2_select(const void *configuration,void *owner,uint32_t iteration,void *output,void *valid_output);
#endif
