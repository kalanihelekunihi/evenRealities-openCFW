/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room ABI model for three Ambiq GPU-patch
 * accessors.  The public package exposes only the functions' declarations and
 * a GCC archive; the private structures below are recovered from that exact
 * archive's DWARF and instruction offsets.
 */

#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_ACCESSORS_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_ACCESSORS_CANDIDATE_H

#include <stdint.h>

/* Preserve the Apollo5 32-bit layout while permitting deterministic host tests. */
#if defined(OPEN_CFW_AMBIQ_GPU_PATCH_HOST_MODEL)
typedef uint32_t open_cfw_ambiq_gpu_address;
#else
typedef void *open_cfw_ambiq_gpu_address;
#endif

struct open_cfw_ambiq_gpu_vertex {
    float x;
    float y;
};

struct open_cfw_ambiq_gpu_path_bbox {
    struct open_cfw_ambiq_gpu_vertex min;
    struct open_cfw_ambiq_gpu_vertex max;
    struct open_cfw_ambiq_gpu_vertex transformed_p1;
    struct open_cfw_ambiq_gpu_vertex transformed_p2;
    struct open_cfw_ambiq_gpu_vertex transformed_p3;
    struct open_cfw_ambiq_gpu_vertex transformed_p4;
    struct open_cfw_ambiq_gpu_vertex transformed_min;
    struct open_cfw_ambiq_gpu_vertex transformed_max;
    float width;
    float height;
    float transformed_width;
    float transformed_height;
};

struct open_cfw_ambiq_gpu_vbuf_view {
    uint32_t segment_size;
    uint32_t data_size;
    open_cfw_ambiq_gpu_address segments;
    open_cfw_ambiq_gpu_address data;
    struct open_cfw_ambiq_gpu_path_bbox bbox;
};

struct open_cfw_ambiq_gpu_path_view {
    struct open_cfw_ambiq_gpu_vbuf_view shape;
    float matrix[9];
    uint32_t flags;
};

struct open_cfw_ambiq_gpu_paint_texture_view {
    open_cfw_ambiq_gpu_address image;
    open_cfw_ambiq_gpu_address palette;
    float matrix[9];
    uint8_t is_lut_texture;
    uint8_t reserved[3];
};

struct open_cfw_ambiq_gpu_paint_view {
    struct open_cfw_ambiq_gpu_paint_texture_view texture;
    uint8_t private_tail[0xB0];
};

void open_cfw_ambiq_gpu_get_paint_texture_candidate(
    const struct open_cfw_ambiq_gpu_paint_view *paint,
    open_cfw_ambiq_gpu_address *image,
    open_cfw_ambiq_gpu_address *palette
);

void open_cfw_ambiq_gpu_get_path_aabb_candidate(
    const struct open_cfw_ambiq_gpu_path_view *path,
    float *x_min,
    float *y_min,
    float *x_max,
    float *y_max
);

void open_cfw_ambiq_gpu_get_path_vbuf_candidate(
    const struct open_cfw_ambiq_gpu_path_view *path,
    uint32_t *segment_size,
    uint32_t *data_size,
    open_cfw_ambiq_gpu_address *segments,
    open_cfw_ambiq_gpu_address *data
);

#endif /* OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_ACCESSORS_CANDIDATE_H */
