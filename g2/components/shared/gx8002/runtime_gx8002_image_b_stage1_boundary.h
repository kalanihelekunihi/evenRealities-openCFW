/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_B_STAGE1_BOUNDARY_H
#define OPEN_CFW_GX8002_IMAGE_B_STAGE1_BOUNDARY_H

#include "runtime_gx8002_kws_model_boundary.h"

#define OPEN_CFW_GX8002_IMAGE_B_STAGE1_SIZE ((size_t)12288U)
#define OPEN_CFW_GX8002_IMAGE_B_STAGE1_SHA256_HEX \
    "a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c"

typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_image_b_stage1_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_image_b_stage1_ports;

int32_t open_cfw_gx8002_image_b_stage1_load(
    const open_cfw_gx8002_image_b_stage1_ports *ports,
    uint8_t *destination,
    size_t capacity);

#endif
