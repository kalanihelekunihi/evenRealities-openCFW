#ifndef OPENR1_SENSOR_STREAM_ZEPHYR_H
#define OPENR1_SENSOR_STREAM_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "sensor_stream/sensor_stream.h"

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
bool openr1_sensor_stream_zephyr_gomore_accelerometer_stage_active(void);
uint32_t openr1_sensor_stream_zephyr_gomore_accelerometer_stage_batches(void);
uint32_t openr1_sensor_stream_zephyr_gomore_accelerometer_stage_failures(void);
uint32_t openr1_sensor_stream_zephyr_motion_batches(void);
uint32_t openr1_sensor_stream_zephyr_motion_failures(void);
uint32_t openr1_sensor_stream_zephyr_temperature_samples(void);
uint32_t openr1_sensor_stream_zephyr_temperature_failures(void);

#endif
