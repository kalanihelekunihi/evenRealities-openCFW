/* SPDX-License-Identifier: MIT */
/*
 * Reconstructs the trailing 4,100 bytes of the image-A boot region as
 * reviewed source: the BINH stage-1 block's zero-fill pad and its
 * CRC-32/MPEG-2 trailer, followed by the BINH stage-2 XIP-text length word.
 *
 * Provenance (public NationalChip grus BINH container format, MIT; see
 * NATIONALCHIP-STARTUP-NOTICE.txt and docs/research/gx8002-image-a-stage1-
 * tail-source.md):
 *
 *  - The 12,288-byte BINH stage-1 block reserves a fixed 0x3000 span
 *    (CONFIG_STAGE1_SRAM_SIZE); everything after the block's actual
 *    reset/vector/boot code is zero-fill out to the block's own trailing
 *    CRC-32/MPEG-2 word (standard poly 0x04C11DB7, init 0xFFFFFFFF, MSB
 *    first, no reflection, no final XOR -- the same algorithm the loader
 *    checks and that tools/analyze_g2_codec_fwpk_segments.py independently
 *    verifies via crc32_mpeg2()). For this exact G2 2.2.6.10 release, the
 *    block's code ends well inside the block (verified by the companion
 *    verifier against the authenticated stock image), so this file's whole
 *    4,092-byte span is that trailing zero-fill, and the following 4 bytes
 *    are the resulting trailer value, 0x21C58EDB stored little-endian.
 *  - The BINH loader reads one little-endian 32-bit word immediately after
 *    the stage-1 block giving the following stage-2 XIP-text length; for
 *    image A that public field is 0x00008E84, matching the authenticated
 *    stage-2 XIP-text extent independently sized by
 *    tools/analyze_g2_codec_stage2_sections.py.
 *
 * The verifier (tools/verify_gx8002_image_a_stage1_tail.py) recomputes the
 * CRC-32/MPEG-2 trailer and the XIP length word from the authenticated
 * stock image via the same algorithm used above and requires this compiled
 * data to match both that independent recomputation and the stock bytes at
 * package offset 0x0000B58C. No executable instruction and no model/command
 * byte is present in this file.
 */
#include "runtime_gx8002_image_a_stage1_tail.h"

/* Values are supplied by the format-aware builder, never copied from a
 * firmware byte slice. Changing the covered block requires a new CRC. */
#ifndef OPEN_CFW_STAGE1_CRC
#error "Builder must supply the computed stage1 CRC"
#endif
#ifndef OPEN_CFW_STAGE2_XIP_SIZE
#error "Builder must supply the stage2 XIP extent"
#endif
#define LE_BYTE(value, shift) ((uint8_t)((uint32_t)(value) >> (shift)))
uint8_t open_cfw_gx8002_image_a_stage1_tail[OPEN_CFW_GX8002_IMAGE_A_STAGE1_TAIL_SIZE] = {
    [4092] = LE_BYTE(OPEN_CFW_STAGE1_CRC, 0),
    [4093] = LE_BYTE(OPEN_CFW_STAGE1_CRC, 8),
    [4094] = LE_BYTE(OPEN_CFW_STAGE1_CRC, 16),
    [4095] = LE_BYTE(OPEN_CFW_STAGE1_CRC, 24),
    [4096] = LE_BYTE(OPEN_CFW_STAGE2_XIP_SIZE, 0),
    [4097] = LE_BYTE(OPEN_CFW_STAGE2_XIP_SIZE, 8),
    [4098] = LE_BYTE(OPEN_CFW_STAGE2_XIP_SIZE, 16),
    [4099] = LE_BYTE(OPEN_CFW_STAGE2_XIP_SIZE, 24)
};
