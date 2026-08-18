#ifndef OPENR1_YHM2710_ZEPHYR_H
#define OPENR1_YHM2710_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_state.h"

int openr1_yhm2710_zephyr_initialize(void);
bool openr1_yhm2710_zephyr_provider_available(void);
bool openr1_yhm2710_zephyr_optical_acquire(void);
bool openr1_yhm2710_zephyr_optical_release(void);
uint8_t openr1_yhm2710_zephyr_active_clients(void);
int openr1_yhm2710_zephyr_charge_state(r1_charge_state *charge);
int openr1_yhm2710_zephyr_last_error(void);

#endif
