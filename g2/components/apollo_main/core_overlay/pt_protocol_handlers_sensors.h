/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_SENSORS_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_SENSORS_H

#include <stddef.h>
#include <stdint.h>

#include "pt_protocol_procsr.h"

typedef int (*open_cfw_pt_sensor_read_bytes_fn)(
    uint8_t *data, size_t length, void *context);
typedef int (*open_cfw_pt_sensor_touch_fn)(
    int16_t differences[5], void *context);
typedef int (*open_cfw_pt_sensor_calibration_fn)(
    int *calibration_matches, uint8_t orientation_xyz[12], void *context);
typedef int (*open_cfw_pt_sensor_id_fn)(
    uint8_t selector, uint32_t *identifier, void *context);

struct open_cfw_pt_sensor_providers {
    open_cfw_pt_sensor_read_bytes_fn read_latest_imu_sample_36;
    open_cfw_pt_sensor_touch_fn read_touch_differences;
    open_cfw_pt_sensor_calibration_fn read_calibration_and_orientation;
    open_cfw_pt_sensor_id_fn read_hardware_identifier;
    open_cfw_pt_sensor_id_fn read_platform_identifier;
    void *context;
};

int open_cfw_pt_bind_sensor_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_sensor_providers *providers
);

#endif
