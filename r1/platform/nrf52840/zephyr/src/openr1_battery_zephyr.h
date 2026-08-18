#ifndef OPENR1_BATTERY_ZEPHYR_H
#define OPENR1_BATTERY_ZEPHYR_H

#include <stdint.h>

#include "openr1/r1_runtime.h"

int openr1_battery_zephyr_initialize(r1_runtime *runtime);
int openr1_battery_zephyr_refresh(void);
uint32_t openr1_battery_zephyr_update_count(void);
int openr1_battery_zephyr_last_error(void);

#endif
