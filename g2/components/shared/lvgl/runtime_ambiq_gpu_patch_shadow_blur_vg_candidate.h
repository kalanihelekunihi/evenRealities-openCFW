/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SHADOW_BLUR_VG_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SHADOW_BLUR_VG_CANDIDATE_H
#include <stdint.h>

struct open_cfw_ambiq_gpu_vg_color { float red, green, blue, alpha; };
struct open_cfw_ambiq_gpu_vg_context_snapshot {
    uint32_t clip_x, clip_y, clip_width, clip_height;
    uintptr_t texture_address;
    uint32_t texture_width, texture_height, texture_stride, texture_format;
};
struct open_cfw_ambiq_gpu_shadow_blur_vg_ports {
    void *context;
    void (*get_context_snapshot)(struct open_cfw_ambiq_gpu_vg_context_snapshot *, void *);
    void (*bind_texture)(uint8_t, uintptr_t, uint32_t, uint32_t, uint32_t, int32_t, uint32_t, void *);
    void (*set_blend)(uint32_t, uint32_t, uint32_t, uint32_t, void *);
    void (*set_clip)(int32_t, int32_t, uint32_t, uint32_t, void *);
    void (*set_raster_color)(uint32_t, void *);
    void (*raster_rect)(int32_t, int32_t, uint32_t, uint32_t, void *);
    void (*vg_set_fill_rule)(uint8_t, void *);
    void (*vg_set_blend)(uint32_t, void *);
    void (*vg_grad_set)(void *, int, const float *, const struct open_cfw_ambiq_gpu_vg_color *, void *);
    void (*vg_paint_set_type)(void *, uint8_t, void *);
    void (*vg_paint_set_grad_radial)(void *, void *, float, float, float, uint32_t, void *);
    void (*vg_draw_circle)(float, float, float, const float *, void *, void *);
};
void open_cfw_ambiq_gpu_shadow_blur_corner_vg_candidate(
    float size, float shadow_width, uint32_t *shadow_buffer, void *paint,
    void *gradient, const struct open_cfw_ambiq_gpu_shadow_blur_vg_ports *ports
);
#endif
