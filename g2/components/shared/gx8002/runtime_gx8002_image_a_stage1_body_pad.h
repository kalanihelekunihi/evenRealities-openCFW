/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_IMAGE_A_STAGE1_BODY_PAD_H
#define OPEN_CFW_GX8002_IMAGE_A_STAGE1_BODY_PAD_H

#include <stddef.h>
#include <stdint.h>

/*
 * Zero-fill span inside the image-A BINH stage-1 block, package
 * [0x0000A837, 0x0000B58C), 3,413 bytes: the block reserves a fixed
 * 0x3000 span (CONFIG_STAGE1_SRAM_SIZE) but the reset/vector/board-init
 * code (runtime_gx8002_spl_reset_entry.S and the retained
 * spl_board_init_r span immediately after it) ends well inside the block.
 * This is the CD-008-owned prefix of that trailing zero run; the run
 * continues past this item's boundary into CD-009's
 * runtime_gx8002_image_a_stage1_tail.c. No executable or model content.
 * See docs/research/gx8002-spl-stage1-reset-source.md.
 */
#define OPEN_CFW_GX8002_IMAGE_A_STAGE1_BODY_PAD_SIZE ((size_t)3413U)

extern const uint8_t
    open_cfw_gx8002_image_a_stage1_body_pad[OPEN_CFW_GX8002_IMAGE_A_STAGE1_BODY_PAD_SIZE];

#endif
