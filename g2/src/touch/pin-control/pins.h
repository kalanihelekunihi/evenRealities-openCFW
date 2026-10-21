#ifndef TOUCH_PIN_CONTROL_OFFLINE_H
#define TOUCH_PIN_CONTROL_OFFLINE_H
#include <stdint.h>
/* Coherent ARM32 GPIO/HSIOM mapping; valid pins0..7, drive/HSIOM0..15. */
void touch_config_pin(volatile uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t);
void touch_config_electrodes(uint32_t,uint32_t,uint32_t,uint32_t,const uint8_t *);
void touch_config_shields(uint32_t,uint32_t,uint32_t,const uint8_t *);
void touch_config_cmod(uint32_t,uint32_t,uint32_t,const uint8_t *);
void touch_mode_ios(uint8_t *);void touch_mode_shield(uint8_t *);void touch_mode_cmod(uint8_t *);
#endif
