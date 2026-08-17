#ifndef OPENR1_TEMPERATURE_ZEPHYR_H
#define OPENR1_TEMPERATURE_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_health.h"

int openr1_temperature_zephyr_initialize(void);
bool openr1_temperature_zephyr_provider_available(void);
int openr1_temperature_zephyr_read_pair(
    int32_t channels[R1_TEMPERATURE_PAIR_SENSOR_COUNT]);
int openr1_temperature_zephyr_read_stream(uint16_t *value);
int openr1_temperature_zephyr_acquire(r1_temperature_pair_result *result);
uint32_t openr1_temperature_zephyr_failure_count(void);
int openr1_temperature_zephyr_last_error(void);

#endif
