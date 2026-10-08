#ifndef TOUCH_ILO_PM_OFFLINE_H
#define TOUCH_ILO_PM_OFFLINE_H
#include <stdint.h>
/* Callback params are unused in this target specialization. */
uint32_t touch_ilo_deep_sleep_callback(void *params, uint32_t mode);
#endif
