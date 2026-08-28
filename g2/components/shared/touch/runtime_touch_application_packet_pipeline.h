/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_APPLICATION_PACKET_PIPELINE_H
#define OPENCFW_TOUCH_APPLICATION_PACKET_PIPELINE_H

#include <stdint.h>

uint32_t open_cfw_touch_packet_2248_build_entry(
    uint32_t group, uint32_t item_index, uint8_t *output,
    const uint8_t *context);
void open_cfw_touch_packet_23a4_build_group(
    uint32_t group, uint8_t *context);

#endif
