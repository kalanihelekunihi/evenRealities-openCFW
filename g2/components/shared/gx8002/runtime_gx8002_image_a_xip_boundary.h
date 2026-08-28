/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_A_XIP_BOUNDARY_H
#define OPEN_CFW_GX8002_IMAGE_A_XIP_BOUNDARY_H

#include "runtime_gx8002_kws_model_boundary.h"

#define OPEN_CFW_GX8002_IMAGE_A_XIP_SIZE ((size_t)36484U)
#define OPEN_CFW_GX8002_IMAGE_A_XIP_SHA256_HEX \
    "49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584"

typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_image_a_xip_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_image_a_xip_ports;

int32_t open_cfw_gx8002_image_a_xip_load(
    const open_cfw_gx8002_image_a_xip_ports *ports,
    uint8_t *destination,
    size_t capacity);

#endif
