#ifndef R1_NATIVE_TOUCH_CALIBRATION_H
#define R1_NATIVE_TOUCH_CALIBRATION_H
#include <stdint.h>
/* Narrow native fields at 0x200067c8 and 0x200067d4. */
extern volatile uint16_t r1_touch_slider_origin;
extern volatile float r1_touch_slider_step;
uint32_t r1_product_sn_letter_decode(void);
void r1_touch_slider_calibration(void);
#endif
