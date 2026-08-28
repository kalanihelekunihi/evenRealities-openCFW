/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_GET_GLYPH_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_GET_GLYPH_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

struct open_cfw_ambiq_gpu_glyph_view {
    uint32_t data_offset;
    uint32_t data_length;
    uint32_t segment_offset;
    uint32_t segment_length;
    float advance;
    uint32_t kern_offset;
    uint8_t kern_length;
    int16_t bbox_xmin;
    int16_t bbox_ymin;
    int16_t bbox_xmax;
    int16_t bbox_ymax;
};

struct open_cfw_ambiq_gpu_font_range_view {
    uint32_t first;
    uint32_t last;
    const struct open_cfw_ambiq_gpu_glyph_view *glyphs;
};

struct open_cfw_ambiq_gpu_font_view {
    uint32_t version;
    const struct open_cfw_ambiq_gpu_font_range_view *ranges;
};

typedef uint32_t (*open_cfw_ambiq_gpu_utf8_size_fn)(const uint8_t *utf8);

const struct open_cfw_ambiq_gpu_glyph_view *
open_cfw_ambiq_gpu_get_glyph_candidate(
    const struct open_cfw_ambiq_gpu_font_view *font,
    const char *character,
    open_cfw_ambiq_gpu_utf8_size_fn codepoint_size
);

#endif /* OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_GET_GLYPH_CANDIDATE_H */
