/* SPDX-License-Identifier: GPL-3.0-only */

#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SHADOW_BLUR_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SHADOW_BLUR_CANDIDATE_H

#include <stdint.h>

typedef uint8_t open_cfw_ambiq_gpu_shadow_texture_id;

struct open_cfw_ambiq_gpu_shadow_blur_ports {
    void *context;
    void (*set_blend)(
        uint32_t mode,
        open_cfw_ambiq_gpu_shadow_texture_id destination,
        open_cfw_ambiq_gpu_shadow_texture_id foreground,
        uint32_t background,
        void *context
    );
    void (*set_clip_temp)(
        int32_t x, int32_t y, int32_t width, int32_t height, void *context
    );
    void (*blit_subrect_fit)(
        int32_t destination_x,
        int32_t destination_y,
        int32_t destination_width,
        int32_t destination_height,
        int32_t source_x,
        int32_t source_y,
        int32_t source_width,
        int32_t source_height,
        void *context
    );
    void (*set_raster_color)(uint32_t color, void *context);
    void (*raster_rect)(
        int32_t x, int32_t y, int32_t width, int32_t height, void *context
    );
    uint32_t (*rgba)(
        uint8_t red, uint8_t green, uint8_t blue, uint8_t alpha, void *context
    );
    void (*set_const_color)(uint32_t color, void *context);
    void (*set_clip_pop)(void *context);
};

void open_cfw_ambiq_gpu_shadow_blur_corner_candidate(
    int32_t size,
    int32_t shadow_width,
    open_cfw_ambiq_gpu_shadow_texture_id texture_one,
    open_cfw_ambiq_gpu_shadow_texture_id texture_two,
    const struct open_cfw_ambiq_gpu_shadow_blur_ports *ports
);

#endif /* OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SHADOW_BLUR_CANDIDATE_H */
