/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_B_SRAM_DATA_BOUNDARY_H
#define OPEN_CFW_GX8002_IMAGE_B_SRAM_DATA_BOUNDARY_H
#include "runtime_gx8002_kws_model_boundary.h"
#define OPEN_CFW_GX8002_IMAGE_B_SRAM_DATA_SIZE ((size_t)2928U)
#define OPEN_CFW_GX8002_IMAGE_B_SRAM_DATA_SHA256_HEX \
    "4b694344b50969d1e2114d9324cbd53374af3dd07375614a5257f18f3213f884"
typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_image_b_sram_data_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_image_b_sram_data_ports;
int32_t open_cfw_gx8002_image_b_sram_data_load(
    const open_cfw_gx8002_image_b_sram_data_ports *ports,uint8_t *destination,size_t capacity);
#endif
