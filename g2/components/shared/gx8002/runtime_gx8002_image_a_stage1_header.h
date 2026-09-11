/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_A_STAGE1_HEADER_H
#define OPEN_CFW_GX8002_IMAGE_A_STAGE1_HEADER_H

#include <stdint.h>

/* Public BINH container header (see tools/analyze_g2_codec_fwpk_segments.py
 * parse_binh_image) immediately followed by the 64-word C-SKY vector table
 * for the image-A flash-resident stage-one block. 24 + 256 = 280 bytes,
 * package offset 0x0000958C. */
typedef struct __attribute__((packed)) {
    char magic[4];               /* "BINH" */
    uint32_t medium;              /* 0x55AA55AA sync pattern */
    uint32_t version;              /* soft version; matches FWPK version 0x203 */
    uint32_t stage2_size;          /* 0xC800 */
    uint32_t stage1_block_size;    /* 0x3000 */
    uint32_t stage1_load_address;  /* 0x20000000 (DRAM base, public field) */
    uint32_t vectors[64];          /* vectors[0] = reset; vectors[1..63] = trap */
} open_cfw_gx8002_image_a_stage1_header;

#define OPEN_CFW_GX8002_IMAGE_A_STAGE1_HEADER_SIZE ((size_t)280U)

extern const open_cfw_gx8002_image_a_stage1_header
    open_cfw_gx8002_image_a_stage1_header_and_vectors;

#endif
