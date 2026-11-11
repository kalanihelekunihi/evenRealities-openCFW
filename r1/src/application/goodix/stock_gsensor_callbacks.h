#ifndef R1_STOCK_GSENSOR_CALLBACKS_H
#define R1_STOCK_GSENSOR_CALLBACKS_H
#include <stdint.h>
/* Native words at 2002fd28/2c/30. Keep opaque until each consumer's
 * concrete ABI is established; registration stores words without calling. */
struct r1_goodix_gsensor_callbacks {
    uintptr_t start, stop, sample;
};
extern volatile struct r1_goodix_gsensor_callbacks r1_goodix_gsensor_callbacks;
uint32_t r1_goodix_gsensor_register(uintptr_t start, uintptr_t stop,
                                   uintptr_t sample);
void r1_goodix_gsensor_stop(void);
void r1_goodix_gsensor_sample(int16_t *samples, uint16_t *count);
#endif
