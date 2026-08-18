#ifndef OPENR1_HEALTH_RESULTS_ZEPHYR_H
#define OPENR1_HEALTH_RESULTS_ZEPHYR_H

#include <stdint.h>

#include "openr1/r1_runtime.h"

int openr1_health_results_zephyr_initialize(r1_runtime *runtime);
uint32_t openr1_health_results_zephyr_heart_rate_results(void);
uint32_t openr1_health_results_zephyr_spo2_results(void);
uint32_t openr1_health_results_zephyr_hrv_results(void);
uint32_t openr1_health_results_zephyr_suppressed_results(void);
uint32_t openr1_health_results_zephyr_invalid_results(void);

#endif
