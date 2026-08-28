/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room expressions of three relocation-free Ambiq
 * GPU-patch accessors.  They are qualified against the exact AmbiqSuite 5.1.0
 * gpu_patch.a archive, not admitted to a production overlay.
 */

#include "runtime_ambiq_gpu_patch_accessors_candidate.h"

#include <stddef.h>
#include <stdint.h>

#if defined(OPEN_CFW_AMBIQ_GPU_PATCH_HOST_MODEL) || UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_vertex) == 0x08U, "vertex ABI changed");
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_path_bbox) == 0x50U, "bbox ABI changed");
_Static_assert(offsetof(struct open_cfw_ambiq_gpu_vbuf_view, bbox) == 0x10U, "bbox offset changed");
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_vbuf_view) == 0x60U, "vbuf ABI changed");
_Static_assert(offsetof(struct open_cfw_ambiq_gpu_path_view, matrix) == 0x60U, "path matrix offset changed");
_Static_assert(offsetof(struct open_cfw_ambiq_gpu_path_view, flags) == 0x84U, "path flags offset changed");
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_path_view) == 0x88U, "path ABI changed");
_Static_assert(offsetof(struct open_cfw_ambiq_gpu_paint_texture_view, is_lut_texture) == 0x2CU, "LUT flag offset changed");
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_paint_texture_view) == 0x30U, "paint texture ABI changed");
_Static_assert(sizeof(struct open_cfw_ambiq_gpu_paint_view) == 0xE0U, "paint ABI changed");
#endif

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_get_paint_texture_candidate(
    const struct open_cfw_ambiq_gpu_paint_view *paint,
    open_cfw_ambiq_gpu_address *image,
    open_cfw_ambiq_gpu_address *palette
)
{
    *image = paint->texture.image;
    *palette = paint->texture.is_lut_texture != 0U
        ? paint->texture.palette
        : (open_cfw_ambiq_gpu_address)0;
}

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_get_path_aabb_candidate(
    const struct open_cfw_ambiq_gpu_path_view *path,
    float *x_min,
    float *y_min,
    float *x_max,
    float *y_max
)
{
    *x_min = path->shape.bbox.min.x;
    *y_min = path->shape.bbox.min.y;
    *x_max = path->shape.bbox.max.x;
    *y_max = path->shape.bbox.max.y;
}

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_get_path_vbuf_candidate(
    const struct open_cfw_ambiq_gpu_path_view *path,
    uint32_t *segment_size,
    uint32_t *data_size,
    open_cfw_ambiq_gpu_address *segments,
    open_cfw_ambiq_gpu_address *data
)
{
    *segment_size = path->shape.segment_size;
    *data_size = path->shape.data_size;
    *segments = path->shape.segments;
    *data = path->shape.data;
}
