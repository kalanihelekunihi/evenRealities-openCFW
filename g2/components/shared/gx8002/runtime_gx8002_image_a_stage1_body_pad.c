/* SPDX-License-Identifier: MIT */
/*
 * Reconstructs 3,413 bytes of the image-A BINH stage-1 block as reviewed
 * source: implicit zero-fill between the end of the block's real code
 * (runtime_gx8002_spl_reset_entry.S plus the retained, unreconstructed
 * spl_board_init_r span that follows it) and the start of CD-009's own
 * trailing pad/CRC/length span (runtime_gx8002_image_a_stage1_tail.c).
 * The block reserves a fixed 0x3000-byte span (CONFIG_STAGE1_SRAM_SIZE);
 * the loader/CRC format does not require this middle region to hold any
 * particular content, and this exact G2 2.2.6.10 release leaves it zero
 * (verified against the authenticated stock image by the companion
 * verifier, not assumed). No executable instruction and no model/command
 * byte is present in this file.
 */
#include "runtime_gx8002_image_a_stage1_body_pad.h"

const uint8_t
    open_cfw_gx8002_image_a_stage1_body_pad[OPEN_CFW_GX8002_IMAGE_A_STAGE1_BODY_PAD_SIZE] = {0};
