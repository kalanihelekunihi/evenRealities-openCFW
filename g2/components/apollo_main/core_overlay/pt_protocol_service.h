/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_SERVICE_H
#define OPEN_CFW_PT_PROTOCOL_SERVICE_H
#include "pt_protocol_handlers_audio.h"
#include "pt_protocol_handlers_basic.h"
#include "pt_protocol_handlers_config.h"
#include "pt_protocol_handlers_data.h"
#include "pt_protocol_handlers_display.h"
#include "pt_protocol_handlers_sensors.h"
#include "pt_protocol_handlers_services.h"
#include "pt_protocol_handlers_transfer.h"

struct open_cfw_pt_all_providers {
 const struct open_cfw_pt_basic_providers *basic;
 const struct open_cfw_pt_config_providers *config;
 const struct open_cfw_pt_data_providers *data;
 const struct open_cfw_pt_display_providers *display;
 const struct open_cfw_pt_sensor_providers *sensors;
 const struct open_cfw_pt_service_providers *services;
 const struct open_cfw_pt_audio_providers *audio;
 const struct open_cfw_pt_transfer_providers *transfer;
};
struct open_cfw_pt_firmware_service {
 struct open_cfw_pt_protocol protocol;
 struct open_cfw_pt_transfer_service transfer;
};
int open_cfw_pt_firmware_service_initialize(
 struct open_cfw_pt_firmware_service *service,
 const struct open_cfw_pt_all_providers *providers,
 uint8_t *transfer_staging, size_t transfer_staging_capacity);
int open_cfw_pt_firmware_service_dispatch(
 struct open_cfw_pt_firmware_service *service,
 const uint8_t *request,uint8_t request_length,uint8_t *response,
 size_t response_capacity,uint8_t *response_length);
#endif
