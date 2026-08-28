/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_A_SRAM_TEXT_BOUNDARY_H
#define OPEN_CFW_GX8002_IMAGE_A_SRAM_TEXT_BOUNDARY_H

#include "runtime_gx8002_kws_model_boundary.h"

#define OPEN_CFW_GX8002_IMAGE_A_SRAM_TEXT_SIZE ((size_t)12516U)
#define OPEN_CFW_GX8002_IMAGE_A_SRAM_TEXT_SHA256_HEX \
    "3780ea0bd9c11bb94cd72bfc6a1e8924f2f3e72e9a31ec49a185a18799c9a5f8"

typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_image_a_sram_text_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_image_a_sram_text_ports;

int32_t open_cfw_gx8002_image_a_sram_text_load(
    const open_cfw_gx8002_image_a_sram_text_ports *ports,
    uint8_t *destination,
    size_t capacity);

#endif
