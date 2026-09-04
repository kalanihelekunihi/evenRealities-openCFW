/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_SERVICE_ALGO_H
#define OPEN_CFW_SERVICE_ALGO_H

#include <stdint.h>

#define OPEN_CFW_SERVICE_ALGO_FRAMES 800u
#define OPEN_CFW_SERVICE_ALGO_CHANNEL_BYTES 1600u
#define OPEN_CFW_SERVICE_ALGO_INPUT_BYTES 3200u
#define OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOWS 10u
#define OPEN_CFW_SERVICE_ALGO_MAX_LAG 10

void open_cfw_service_algo_front_buffer_get(
    int16_t **buffer, uint32_t *size
);
int algo_front_data_preprocess(const void *data, uint32_t size);
uint16_t SVC_SSRProcess(const void *data, uint32_t size);
double open_cfw_service_algo_quiet_nan(void);
void open_cfw_service_algo_float_hook(void);
double open_cfw_service_algo_delay_to_angle(
    double delay_seconds, double microphone_spacing, double sound_speed
);
void open_cfw_service_algo_cross_correlation(
    const int16_t *left,
    const int16_t *right,
    int sample_count,
    int maximum_lag,
    double sample_rate,
    double microphone_spacing,
    double sound_speed,
    double minimum_rms,
    double minimum_correlation,
    double *angle_radians,
    double *normalized_delay,
    double *correlation,
    double *maximum_rms
);
int16_t open_cfw_service_algo_source_angle(void);
int open_cfw_service_algo_process(
    const void *data,
    uint32_t size,
    uint16_t *ssr,
    int16_t *angle_degrees
);
int open_cfw_service_algo_energy_window_update(
    const int16_t *samples, uint32_t size
);

#endif
