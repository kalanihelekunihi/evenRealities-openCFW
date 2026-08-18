#ifndef OPENR1_SENSOR_STREAM_ZEPHYR_H
#define OPENR1_SENSOR_STREAM_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "gomore_primitives/gomore_primitives.h"
#include "sensor_stream/sensor_stream.h"

typedef bool (*openr1_gomore_topic_consume_fn)(
    void *context, const gomore_primitives_topic_input_state *input);

int openr1_sensor_stream_zephyr_initialize(void);
uint32_t openr1_sensor_stream_zephyr_poll(void);
bool openr1_sensor_stream_zephyr_is_ready(void);
sensor_stream *openr1_sensor_stream_zephyr_framework(void);
sensor_stream_listener *openr1_sensor_stream_zephyr_register_accelerometer(
    const char *listener_name, sensor_stream_listener_callback callback,
    uint8_t mode);
void openr1_sensor_stream_zephyr_unregister_accelerometer(
    sensor_stream_listener *listener);
sensor_stream_listener *openr1_sensor_stream_zephyr_register_temperature(
    const char *listener_name, sensor_stream_listener_callback callback,
    uint8_t mode);
void openr1_sensor_stream_zephyr_unregister_temperature(
    sensor_stream_listener *listener);
int openr1_sensor_stream_zephyr_temperature_once_set(bool enabled);
bool openr1_sensor_stream_zephyr_temperature_once_active(void);
uint32_t openr1_sensor_stream_zephyr_temperature_once_successes(void);
uint32_t openr1_sensor_stream_zephyr_temperature_once_timeouts(void);
int openr1_sensor_stream_zephyr_gomore_accelerometer_stage_set(bool enabled);
int openr1_sensor_stream_zephyr_gomore_health_stage_set(bool enabled);
void openr1_sensor_stream_zephyr_health_policy_request(bool enabled);
int openr1_sensor_stream_zephyr_gomore_authorization_set(
    uint32_t slot, bool enabled);
uint8_t openr1_sensor_stream_zephyr_gomore_active_slot_mask(void);
bool openr1_sensor_stream_zephyr_gomore_health_stage_active(void);
int openr1_sensor_stream_zephyr_gomore_consume_ready(
    openr1_gomore_topic_consume_fn consume, void *context);
bool openr1_sensor_stream_zephyr_goodix_raw_hr_append(uint32_t value);
bool openr1_sensor_stream_zephyr_goodix_heart_rate_update(
    const int32_t values[4]);
bool openr1_sensor_stream_zephyr_goodix_hrv_update(
    const int32_t values[6]);
bool openr1_sensor_stream_zephyr_gomore_accelerometer_stage_active(void);
uint32_t openr1_sensor_stream_zephyr_gomore_accelerometer_stage_batches(void);
uint32_t openr1_sensor_stream_zephyr_gomore_accelerometer_stage_failures(void);
uint32_t openr1_sensor_stream_zephyr_motion_batches(void);
uint32_t openr1_sensor_stream_zephyr_motion_failures(void);
uint32_t openr1_sensor_stream_zephyr_temperature_samples(void);
uint32_t openr1_sensor_stream_zephyr_temperature_failures(void);

#endif
