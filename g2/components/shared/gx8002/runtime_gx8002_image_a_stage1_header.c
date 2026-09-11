/* SPDX-License-Identifier: MIT */
/* Source-authored image-A BINH stage-one header and vector table.
 *
 * The BINH container format and field layout are public and self-verifying
 * (magic, sync pattern, a CRC-32/MPEG-2 trailer over the block body, and
 * self-referential vector addresses); see g2/tools/analyze_g2_codec_fwpk_segments.py
 * parse_binh_image and g2/docs/research/g2-codec-fwpk-segments-recovery.md.
 * The field values (soft version, stage sizes, DRAM load address) are this
 * build's recovered configuration, cross-confirmed elsewhere in the image
 * (FWPK version 0x203, the "0.0.2.3" build string). The two vector targets
 * are this repository's own reconstructed reset chain
 * (runtime_gx8002_spl_reset_entry.S); no NationalChip executable bytes are
 * reproduced by this file, and generating a public container format does not
 * claim ownership of any payload it frames.
 */
#include "runtime_gx8002_image_a_stage1_header.h"

extern void open_cfw_gx8002_spl_reset_entry(void);
extern void open_cfw_gx8002_spl_default_handler(void);

const open_cfw_gx8002_image_a_stage1_header open_cfw_gx8002_image_a_stage1_header_and_vectors
    __attribute__((section(".rodata.open_cfw_gx8002_image_a_stage1_header"))) = {
    .magic = {'B', 'I', 'N', 'H'},
    .medium = 0x55AA55AAU,
    .version = 0x00000203U,
    .stage2_size = 0x0000C800U,
    .stage1_block_size = 0x00003000U,
    .stage1_load_address = 0x20000000U,
    .vectors = {
        [0] = (uint32_t)(uintptr_t)&open_cfw_gx8002_spl_reset_entry,
        [1 ... 63] = (uint32_t)(uintptr_t)&open_cfw_gx8002_spl_default_handler,
    },
};
