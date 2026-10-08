#ifndef TOUCH_LP_APPLICATION_OFFLINE_H
#define TOUCH_LP_APPLICATION_OFFLINE_H
#include <stdint.h>
typedef struct {uint32_t (*enter)(void);void (*restore)(uint32_t);uint32_t (*sleep)(void);} touch_lp_pm_dependencies;
uint32_t touch_start_all_lp(uint8_t *context);
/* Reconstructed app state3 slice; stops before logs/common loop/configuration.
 * Fixed project RAM globals are supplied explicitly to this offline interface. */
void touch_app_lp_phase(uint8_t *context,uint8_t *state,uint32_t *budget,const touch_lp_pm_dependencies *pm);
#endif
