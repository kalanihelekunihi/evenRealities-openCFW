/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_KWS_COMMAND_BOUNDARY_H
#define OPEN_CFW_GX8002_KWS_COMMAND_BOUNDARY_H
#include "runtime_gx8002_kws_model_boundary.h"
#define OPEN_CFW_GX8002_KWS_COMMAND_SIZE ((size_t)9164U)
#define OPEN_CFW_GX8002_KWS_COMMAND_SHA256_HEX \
    "c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9"
typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_kws_command_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_kws_command_ports;
int32_t open_cfw_gx8002_kws_command_load(const open_cfw_gx8002_kws_command_ports *ports,
                                         uint8_t *destination, size_t capacity);
#endif
