/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of platform/audio/service_algo.c from the
 * authenticated G2 2.2.6.10 object at 0x005915dc..0x00591d14.
 */

#include "service_algo.h"

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SERVICE_ALGO_LEFT_BUFFER
#define OPEN_CFW_SERVICE_ALGO_LEFT_BUFFER \
    ((int16_t *)(uintptr_t)0x20375400u)
#endif
#ifndef OPEN_CFW_SERVICE_ALGO_RIGHT_BUFFER
#define OPEN_CFW_SERVICE_ALGO_RIGHT_BUFFER \
    ((int16_t *)(uintptr_t)0x20375a40u)
#endif
#ifndef OPEN_CFW_SERVICE_ALGO_MONO_BUFFER
#define OPEN_CFW_SERVICE_ALGO_MONO_BUFFER \
    ((int16_t *)(uintptr_t)0x20376080u)
#endif
#ifndef OPEN_CFW_SERVICE_ALGO_LEFT_ENERGY
#define OPEN_CFW_SERVICE_ALGO_LEFT_ENERGY \
    (*(uint64_t *)(uintptr_t)0x20074168u)
#endif
#ifndef OPEN_CFW_SERVICE_ALGO_RIGHT_ENERGY
#define OPEN_CFW_SERVICE_ALGO_RIGHT_ENERGY \
    (*(uint64_t *)(uintptr_t)0x20074170u)
#endif
#ifndef OPEN_CFW_SERVICE_ALGO_WINDOW_INDEX
#define OPEN_CFW_SERVICE_ALGO_WINDOW_INDEX \
    (*(uint64_t *)(uintptr_t)0x20074178u)
#endif
#ifndef OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOW
#define OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOW \
    ((uint64_t *)(uintptr_t)0x20072d08u)
#endif

#if !defined(OPEN_CFW_SERVICE_ALGO_BUFFER_GET_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_PREPROCESS_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_SSR_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_QUIET_NAN_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_FLOAT_HOOK_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_DELAY_TO_ANGLE_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_CORRELATION_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_SOURCE_ANGLE_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_PROCESS_ONLY) && \
    !defined(OPEN_CFW_SERVICE_ALGO_ENERGY_UPDATE_ONLY)
#define OPEN_CFW_SERVICE_ALGO_BUILD_ALL 1
#endif

static __attribute__((unused)) double open_cfw_service_algo_abs(double value)
{
    return value < 0.0 ? -value : value;
}

static __attribute__((unused, always_inline)) inline double
open_cfw_service_algo_sqrt(double value)
{
    double estimate;
    unsigned int iteration;
    if (value < 0.0) {
        return open_cfw_service_algo_quiet_nan();
    }
    if (value == 0.0) {
        return 0.0;
    }
    estimate = value < 1.0 ? 1.0 : value;
    for (iteration = 0u; iteration < 32u; ++iteration) {
        estimate = 0.5 * (estimate + value / estimate);
    }
    return estimate;
}

static __attribute__((unused)) double open_cfw_service_algo_asin(double value)
{
    double magnitude = open_cfw_service_algo_abs(value);
    double polynomial;
    double result;
    if (magnitude > 1.0) {
        return open_cfw_service_algo_quiet_nan();
    }
    polynomial = ((-0.0187293 * magnitude + 0.0742610) * magnitude
        - 0.2121144) * magnitude + 1.5707288;
    result = 1.57079632679489661923
        - open_cfw_service_algo_sqrt(1.0 - magnitude) * polynomial;
    return value < 0.0 ? -result : result;
}

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_BUFFER_GET_ONLY)
__attribute__((used, noinline))
void open_cfw_service_algo_front_buffer_get(
    int16_t **buffer, uint32_t *size
)
{
    if (buffer != NULL) {
        *buffer = OPEN_CFW_SERVICE_ALGO_MONO_BUFFER;
    }
    if (size != NULL) {
        *size = OPEN_CFW_SERVICE_ALGO_CHANNEL_BYTES;
    }
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_PREPROCESS_ONLY)
__attribute__((used, noinline))
int algo_front_data_preprocess(const void *data, uint32_t size)
{
    const int16_t *stereo = (const int16_t *)data;
    uint64_t left_energy_sum = 0u;
    uint64_t right_energy_sum = 0u;
    uint32_t index;
    if (stereo == NULL || size != OPEN_CFW_SERVICE_ALGO_INPUT_BYTES) {
        return -1;
    }
    for (index = 0u; index < OPEN_CFW_SERVICE_ALGO_FRAMES; ++index) {
        int32_t left = stereo[index * 2u];
        int32_t right = stereo[index * 2u + 1u];
        OPEN_CFW_SERVICE_ALGO_LEFT_BUFFER[index] = (int16_t)left;
        OPEN_CFW_SERVICE_ALGO_RIGHT_BUFFER[index] = (int16_t)right;
        OPEN_CFW_SERVICE_ALGO_MONO_BUFFER[index] =
            (int16_t)(left / 2 + right / 2);
        left_energy_sum += (uint64_t)(int64_t)(left * left);
        right_energy_sum += (uint64_t)(int64_t)(right * right);
    }
    OPEN_CFW_SERVICE_ALGO_LEFT_ENERGY =
        left_energy_sum / OPEN_CFW_SERVICE_ALGO_FRAMES;
    OPEN_CFW_SERVICE_ALGO_RIGHT_ENERGY =
        right_energy_sum / OPEN_CFW_SERVICE_ALGO_FRAMES;
    return 0;
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_SSR_ONLY)
__attribute__((used, noinline))
uint16_t SVC_SSRProcess(const void *data, uint32_t size)
{
    uint64_t baseline = 0u;
    uint64_t current;
    uint32_t index;
    if (data == NULL || size == 0u ||
        OPEN_CFW_SERVICE_ALGO_LEFT_ENERGY == 0u ||
        OPEN_CFW_SERVICE_ALGO_RIGHT_ENERGY == 0u) {
        return 0u;
    }
    current = (OPEN_CFW_SERVICE_ALGO_LEFT_ENERGY
        + OPEN_CFW_SERVICE_ALGO_RIGHT_ENERGY) / 2u;
    for (index = 0u; index < OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOWS; ++index) {
        baseline += OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOW[index];
    }
    baseline /= OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOWS;
    return (uint16_t)((current + 1u) / (baseline + 1u));
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_QUIET_NAN_ONLY)
__attribute__((used, noinline))
double open_cfw_service_algo_quiet_nan(void)
{
    union {
        uint64_t bits;
        double value;
    } result;
    result.bits = UINT64_C(0x7ff8000000000000);
    return result.value;
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_FLOAT_HOOK_ONLY)
__attribute__((used, noinline))
void open_cfw_service_algo_float_hook(void)
{
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_DELAY_TO_ANGLE_ONLY)
__attribute__((used, noinline))
double open_cfw_service_algo_delay_to_angle(
    double delay_seconds, double microphone_spacing, double sound_speed
)
{
    if (microphone_spacing <= 0.0) {
        return open_cfw_service_algo_quiet_nan();
    }
    open_cfw_service_algo_float_hook();
    return open_cfw_service_algo_asin(
        delay_seconds * sound_speed / microphone_spacing
    );
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_CORRELATION_ONLY)
__attribute__((used, noinline))
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
)
{
    int lag;
    int best_lag = 0;
    double left_energy = 0.0;
    double right_energy = 0.0;
    double best = -1.7976931348623157e308;
    double absolute_sum = 0.0;
    double rms;
    double score = 0.0;
    if (sample_count <= 0 || left == NULL || right == NULL) {
        if (angle_radians != NULL) *angle_radians = open_cfw_service_algo_quiet_nan();
        if (normalized_delay != NULL) *normalized_delay = open_cfw_service_algo_quiet_nan();
        if (correlation != NULL) *correlation = 0.0;
        if (maximum_rms != NULL) *maximum_rms = 0.0;
        return;
    }
    if (maximum_lag <= 0) {
        maximum_lag = 8;
    }
    if (maximum_lag >= sample_count) {
        maximum_lag = sample_count - 1;
    }
    for (lag = 0; lag < sample_count; ++lag) {
        double l = (double)left[lag];
        double r = (double)right[lag];
        left_energy += l * l;
        right_energy += r * r;
    }
    rms = open_cfw_service_algo_sqrt(left_energy / sample_count);
    {
        double right_rms = open_cfw_service_algo_sqrt(
            right_energy / sample_count
        );
        if (right_rms > rms) rms = right_rms;
    }
    if (maximum_rms != NULL) *maximum_rms = rms;
    if (rms < minimum_rms) {
        if (angle_radians != NULL) *angle_radians = open_cfw_service_algo_quiet_nan();
        if (normalized_delay != NULL) *normalized_delay = open_cfw_service_algo_quiet_nan();
        if (correlation != NULL) *correlation = 0.0;
        return;
    }
    for (lag = -maximum_lag; lag <= maximum_lag; ++lag) {
        int start = lag < 0 ? -lag : 0;
        int end = lag > 0 ? sample_count - lag : sample_count;
        int sample;
        double sum = 0.0;
        for (sample = start; sample < end; ++sample) {
            sum += (double)right[sample + lag] * (double)left[sample];
        }
        if (sum > best) {
            best = sum;
            best_lag = lag;
        }
        absolute_sum += open_cfw_service_algo_abs(sum);
    }
    absolute_sum /= (double)(maximum_lag * 2 + 1);
    if (absolute_sum > 0.0) {
        score = best / (absolute_sum + 1.0e-12);
    }
    if (correlation != NULL) *correlation = score;
    if (score < minimum_correlation || sample_rate <= 0.0) {
        if (angle_radians != NULL) *angle_radians = open_cfw_service_algo_quiet_nan();
        if (normalized_delay != NULL) *normalized_delay = open_cfw_service_algo_quiet_nan();
        return;
    }
    if (normalized_delay != NULL) {
        *normalized_delay = (double)best_lag / sample_rate;
    }
    if (angle_radians != NULL) {
        *angle_radians = open_cfw_service_algo_delay_to_angle(
            (double)best_lag / sample_rate,
            microphone_spacing,
            sound_speed
        );
    }
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_SOURCE_ANGLE_ONLY)
__attribute__((used, noinline))
int16_t open_cfw_service_algo_source_angle(void)
{
    double angle;
    open_cfw_service_algo_cross_correlation(
        OPEN_CFW_SERVICE_ALGO_LEFT_BUFFER,
        OPEN_CFW_SERVICE_ALGO_RIGHT_BUFFER,
        (int)OPEN_CFW_SERVICE_ALGO_FRAMES,
        OPEN_CFW_SERVICE_ALGO_MAX_LAG,
        16000.0,
        0.14,
        343.0,
        0.0,
        0.0,
        &angle,
        NULL,
        NULL,
        NULL
    );
    if (angle != angle) {
        return 0;
    }
    return (int16_t)(angle * 180.0 / 3.14159265358979323846);
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_PROCESS_ONLY)
__attribute__((used, noinline))
int open_cfw_service_algo_process(
    const void *data,
    uint32_t size,
    uint16_t *ssr,
    int16_t *angle_degrees
)
{
    if (ssr == NULL || angle_degrees == NULL ||
        algo_front_data_preprocess(data, size) != 0) {
        return -1;
    }
    *ssr = SVC_SSRProcess(data, size);
    *angle_degrees = open_cfw_service_algo_source_angle();
    return 0;
}
#endif

#if defined(OPEN_CFW_SERVICE_ALGO_BUILD_ALL) || \
    defined(OPEN_CFW_SERVICE_ALGO_ENERGY_UPDATE_ONLY)
__attribute__((used, noinline))
int open_cfw_service_algo_energy_window_update(
    const int16_t *samples, uint32_t size
)
{
    uint64_t energy = 0u;
    uint32_t sample_count;
    uint32_t index;
    if (samples == NULL || size == 0u || (size & 1u) != 0u) {
        return -1;
    }
    sample_count = size / 2u;
    for (index = 0u; index < sample_count; ++index) {
        int64_t sample = samples[index];
        energy += (uint64_t)(sample * sample);
    }
    OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOW[
        OPEN_CFW_SERVICE_ALGO_WINDOW_INDEX %
            OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOWS
    ] = energy / sample_count;
    OPEN_CFW_SERVICE_ALGO_WINDOW_INDEX =
        (OPEN_CFW_SERVICE_ALGO_WINDOW_INDEX + 1u) %
            OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOWS;
    return 0;
}
#endif
