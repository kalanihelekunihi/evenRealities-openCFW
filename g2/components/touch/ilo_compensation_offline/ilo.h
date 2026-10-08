#ifndef TOUCH_ILO_COMPENSATION_OFFLINE_H
#define TOUCH_ILO_COMPENSATION_OFFLINE_H
#include <stdint.h>
enum {TOUCH_ILO_SUCCESS=0,TOUCH_ILO_STARTED=0x490004,TOUCH_ILO_BAD_PARAM=0x4a0001,TOUCH_ILO_INVALID_STATE=0x4a0003};
void touch_ilo_start(void);
void touch_ilo_stop(void);
/* Coherent globals/MMIO; supported arithmetic contract SystemCoreClock>=1024. */
uint32_t touch_ilo_measure(uint32_t desired_us,uint32_t *cycles);
uint32_t touch_ilo_compensate(uint8_t *context);
#endif
