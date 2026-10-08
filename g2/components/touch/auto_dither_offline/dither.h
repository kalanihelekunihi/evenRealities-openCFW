#ifndef TOUCH_AUTO_DITHER_OFFLINE_H
#define TOUCH_AUTO_DITHER_OFFLINE_H
#include <stdint.h>
uint32_t touch_configure_auto_dither(uint8_t *);
uint32_t touch_switch_dither_dependency(uint32_t,uint8_t *);
/* Offline composition: generated base, both slot arrays, configure, CPU setup. */
uint32_t touch_prepare_auto_dither(uint8_t *);
#endif
