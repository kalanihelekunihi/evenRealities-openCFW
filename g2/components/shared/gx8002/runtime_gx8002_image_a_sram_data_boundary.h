/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_A_SRAM_DATA_BOUNDARY_H
#define OPEN_CFW_GX8002_IMAGE_A_SRAM_DATA_BOUNDARY_H
#include "runtime_gx8002_kws_model_boundary.h"
#define OPEN_CFW_GX8002_IMAGE_A_SRAM_DATA_SIZE ((size_t)2196U)
#define OPEN_CFW_GX8002_IMAGE_A_SRAM_DATA_SHA256_HEX \
    "e0a88003909bb45ae966bfedcbf6e21a5bc83137d26bd36c7f81114fa0034384"
typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_image_a_sram_data_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_image_a_sram_data_ports;
int32_t open_cfw_gx8002_image_a_sram_data_load(
    const open_cfw_gx8002_image_a_sram_data_ports *ports,uint8_t *destination,size_t capacity);
#endif
