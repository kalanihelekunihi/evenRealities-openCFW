#include "openr1_health_results_zephyr.h"

#include <errno.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "openr1/r1_health.h"
#include "openr1_clock_zephyr.h"
#include "openr1_databases_zephyr.h"
#include "openr1_sensor_stream_zephyr.h"
#include "r1_gh3x2x_algo_bridge.h"

typedef struct {
    int (*initialize)(r1_runtime *);
    uint32_t (*heart_rate_results)(void);
    uint32_t (*spo2_results)(void);
    uint32_t (*hrv_results)(void);
    uint32_t (*suppressed_results)(void);
    uint32_t (*invalid_results)(void);
} openr1_health_results_zephyr_api;

static r1_runtime *health_runtime;
static r1_hrv_producer hrv_producer;
static r1_hrv_producer_session hrv_session;
static atomic_t heart_rate_results;
static atomic_t spo2_results;
static atomic_t hrv_results;
static atomic_t suppressed_results;
static atomic_t invalid_results;

static bool value_is_u8(int32_t value) {
    return value >= 0 && value <= UINT8_MAX;
}

static bool value_is_i8(int32_t value) {
    return value >= INT8_MIN && value <= INT8_MAX;
}

static bool result_has_fields(
    const r1_gh3x2x_algo_result *result, uint8_t minimum_count,
    uint16_t required_mask) {
    return result != NULL && result->updated &&
        result->value_count >= minimum_count &&
        (result->value_mask & required_mask) == required_mask;
}

static bool health_publication_enabled(void) {
    return health_runtime != NULL &&
        health_runtime->device.health_settings[4] != 0u;
}

static void consume_heart_rate(
    const r1_gh3x2x_algo_result *result) {
    /* Public Goodix HR result words are hba_out, valid_score, hba_snr,
     * valid_level, acc_info, and reg_scene. The R1 topic callback consumes
     * heart rate, confidence, and signal; valid_level is the third lane. */
    if (!result_has_fields(result, 4u, UINT16_C(0x000b)) ||
        !value_is_u8(result->values[0]) ||
        !value_is_u8(result->values[1]) ||
        !value_is_u8(result->values[3])) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    if (!openr1_sensor_stream_zephyr_goodix_heart_rate_update(
            result->values)) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    uint32_t timestamp = 0u;
    if (!openr1_clock_zephyr_epoch(&timestamp)) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    const uint8_t record[R1_HEART_RATE_RESULT_RECORD_BYTES] = {
        (uint8_t)result->values[0],
        (uint8_t)result->values[1],
        (uint8_t)result->values[3],
    };
    r1_hr_result_plan plan;
    if (r1_hr_once_result_plan(
            record, sizeof record, health_publication_enabled(),
            timestamp, &plan) != R1_OK) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    if (!plan.publish_event) {
        (void)atomic_inc(&suppressed_results);
        return;
    }
    if (openr1_databases_zephyr_consume_heart_rate_event(
            plan.event_payload, plan.event_payload_length) == R1_OK) {
        (void)atomic_inc(&heart_rate_results);
    } else {
        (void)atomic_inc(&invalid_results);
    }
}

static void consume_spo2(const r1_gh3x2x_algo_result *result) {
    /* The public-democode words exactly match the six recovered R1 topic
     * bytes: SpO2, R value, confidence, signed valid level, mean HR, and
     * invalid marker. A seventh Goodix mask bit is reserved/zero upstream. */
    if (!result_has_fields(result, 6u, UINT16_C(0x003f)) ||
        !value_is_u8(result->values[0]) ||
        !value_is_u8(result->values[1]) ||
        !value_is_u8(result->values[2]) ||
        !value_is_i8(result->values[3]) ||
        !value_is_u8(result->values[4]) ||
        !value_is_u8(result->values[5])) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    const uint8_t record[R1_SPO2_RESULT_RECORD_BYTES] = {
        (uint8_t)result->values[0],
        (uint8_t)result->values[1],
        (uint8_t)result->values[2],
        (uint8_t)(int8_t)result->values[3],
        (uint8_t)result->values[4],
        (uint8_t)result->values[5],
    };
    r1_spo2_result_plan plan;
    if (r1_spo2_once_result_plan(
            record, sizeof record, health_publication_enabled(),
            &plan) != R1_OK) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    if (!plan.publish_event) {
        (void)atomic_inc(&suppressed_results);
        return;
    }
    if (openr1_databases_zephyr_consume_spo2_event(
            plan.event_payload, plan.event_payload_length) == R1_OK) {
        (void)atomic_inc(&spo2_results);
    } else {
        (void)atomic_inc(&invalid_results);
    }
}

static void consume_hrv(const r1_gh3x2x_algo_result *result) {
    /* The recovered HRV root publishes four RR intervals in milliseconds,
     * a quality word, and the number of valid intervals. Retail sets the
     * otherwise-reserved result bit 6, but does not write a seventh word. */
    if (!result_has_fields(result, 6u, UINT16_C(0x003f)) ||
        result->values[5] < 0 || result->values[5] > 4) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    if (!openr1_sensor_stream_zephyr_goodix_hrv_update(result->values)) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    const size_t interval_count = (size_t)result->values[5];
    uint16_t intervals[4] = {0u, 0u, 0u, 0u};
    for (size_t index = 0u; index < interval_count; ++index) {
        if (result->values[index] < 0 ||
            result->values[index] > UINT16_MAX) {
            (void)atomic_inc(&invalid_results);
            return;
        }
        intervals[index] = (uint16_t)result->values[index];
    }
    uint32_t timestamp = 0u;
    if (!openr1_clock_zephyr_epoch(&timestamp)) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    r1_hrv_producer_result producer_result;
    if (r1_hrv_producer_ingest(
            &hrv_producer, &hrv_session, intervals, interval_count,
            false, health_publication_enabled(), timestamp,
            &producer_result) != R1_OK) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    if (!producer_result.publication.published) {
        (void)atomic_inc(&suppressed_results);
        return;
    }
    if (openr1_databases_zephyr_consume_hrv_event(
            producer_result.publication.payload,
            sizeof producer_result.publication.payload) == R1_OK) {
        (void)atomic_inc(&hrv_results);
    } else {
        (void)atomic_inc(&invalid_results);
    }
}

static void observe_result(
    void *context, const r1_gh3x2x_algo_frame *frame,
    const r1_gh3x2x_algo_result *result) {
    (void)context;
    if (health_runtime == NULL || frame == NULL || result == NULL ||
        k_is_in_isr()) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HR) {
        consume_heart_rate(result);
    } else if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_HRV) {
        consume_hrv(result);
    } else if (frame->function_offset == R1_GH3X2X_ALGO_FUNCTION_SPO2) {
        consume_spo2(result);
    } else {
        (void)atomic_inc(&suppressed_results);
    }
}

static void observe_frame(
    void *context, const r1_gh3x2x_algo_frame *frame) {
    (void)context;
    if (health_runtime == NULL || frame == NULL || k_is_in_isr() ||
        frame->function_offset != R1_GH3X2X_ALGO_FUNCTION_HSM ||
        frame->channel_count == 0u || frame->raw_values == NULL) {
        (void)atomic_inc(&invalid_results);
        return;
    }
    if (!openr1_sensor_stream_zephyr_goodix_raw_hr_append(
            frame->raw_values[0])) {
        (void)atomic_inc(&suppressed_results);
    }
}

int openr1_health_results_zephyr_initialize(r1_runtime *runtime) {
    if (runtime == NULL || !openr1_databases_zephyr_health_ready()) {
        return -EINVAL;
    }
    if (health_runtime != NULL || r1_gh3x2x_algo_result_observer_bound() ||
        r1_gh3x2x_algo_frame_observer_bound()) {
        return -EALREADY;
    }
    health_runtime = runtime;
    r1_hrv_producer_initialize(&hrv_producer);
    hrv_session = (r1_hrv_producer_session){
        .subscription_active = true,
    };
    atomic_clear(&heart_rate_results);
    atomic_clear(&spo2_results);
    atomic_clear(&hrv_results);
    atomic_clear(&suppressed_results);
    atomic_clear(&invalid_results);
    r1_gh3x2x_algo_bind_result_observer(observe_result, NULL);
    r1_gh3x2x_algo_bind_frame_observer(observe_frame, NULL);
    return 0;
}

uint32_t openr1_health_results_zephyr_heart_rate_results(void) {
    return (uint32_t)atomic_get(&heart_rate_results);
}

uint32_t openr1_health_results_zephyr_spo2_results(void) {
    return (uint32_t)atomic_get(&spo2_results);
}

uint32_t openr1_health_results_zephyr_hrv_results(void) {
    return (uint32_t)atomic_get(&hrv_results);
}

uint32_t openr1_health_results_zephyr_suppressed_results(void) {
    return (uint32_t)atomic_get(&suppressed_results);
}

uint32_t openr1_health_results_zephyr_invalid_results(void) {
    return (uint32_t)atomic_get(&invalid_results);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_health_results_zephyr_api health_results_zephyr_api = {
    openr1_health_results_zephyr_initialize,
    openr1_health_results_zephyr_heart_rate_results,
    openr1_health_results_zephyr_spo2_results,
    openr1_health_results_zephyr_hrv_results,
    openr1_health_results_zephyr_suppressed_results,
    openr1_health_results_zephyr_invalid_results,
};
