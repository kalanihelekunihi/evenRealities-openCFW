/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_A_STAGE1_TAIL_H
#define OPEN_CFW_GX8002_IMAGE_A_STAGE1_TAIL_H

#include <stddef.h>
#include <stdint.h>

/*
 * Deterministic tail of the image-A boot region, package
 * [0x0000B58C, 0x0000C590), 4,100 bytes:
 *
 *   [0x0000B58C, 0x0000C588)  4,092 B  BINH stage-1 block zero-fill pad
 *   [0x0000C588, 0x0000C58C)     4 B  BINH stage-1 block CRC-32/MPEG-2 trailer
 *   [0x0000C58C, 0x0000C590)     4 B  BINH stage-2 XIP-text length word
 *
 * None of these bytes carry executable or model content; every byte here is
 * public BINH container bookkeeping (padding, checksum, length) computed
 * from the surrounding format layout, not proprietary payload. See
 * docs/research/gx8002-image-a-stage1-tail-source.md.
 */
#define OPEN_CFW_GX8002_IMAGE_A_STAGE1_TAIL_SIZE ((size_t)4100U)

extern uint8_t open_cfw_gx8002_image_a_stage1_tail[OPEN_CFW_GX8002_IMAGE_A_STAGE1_TAIL_SIZE];

#endif
