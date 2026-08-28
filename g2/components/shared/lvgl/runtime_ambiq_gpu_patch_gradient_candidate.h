/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_GRADIENT_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_GRADIENT_CANDIDATE_H

#include <stdint.h>

typedef uint8_t open_cfw_ambiq_gpu_gradient_texture_id;

struct open_cfw_ambiq_gpu_gradient_color {
    float red;
    float green;
    float blue;
    float alpha;
};

struct open_cfw_ambiq_gpu_gradient_ports {
    void *context;
    uint32_t (*texture_width)(
        open_cfw_ambiq_gpu_gradient_texture_id texture, void *context
    );
    void (*set_clip_temp)(
        int32_t x, int32_t y, uint32_t width, uint32_t height, void *context
    );
    void (*set_blend)(
        uint32_t mode,
        open_cfw_ambiq_gpu_gradient_texture_id destination,
        uint32_t foreground,
        uint32_t background,
        void *context
    );
    void (*enable_gradient)(int enabled, void *context);
    void (*set_gradient)(
        float red_initial,
        float green_initial,
        float blue_initial,
        float alpha_initial,
        float red_dx,
        float red_dy,
        float green_dx,
        float green_dy,
        float blue_dx,
        float blue_dy,
        float alpha_dx,
        float alpha_dy,
        void *context
    );
    void (*fill_rect)(
        int32_t x,
        int32_t y,
        uint32_t width,
        uint32_t height,
        uint32_t color,
        void *context
    );
    void (*interpolate_rect_colors)(
        int32_t x,
        int32_t y,
        uint32_t width,
        uint32_t height,
        const struct open_cfw_ambiq_gpu_gradient_color *first,
        const struct open_cfw_ambiq_gpu_gradient_color *second,
        const struct open_cfw_ambiq_gpu_gradient_color *third,
        void *context
    );
    uint32_t (*rgba)(
        uint8_t red, uint8_t green, uint8_t blue, uint8_t alpha, void *context
    );
    void (*set_clip_pop)(void *context);
};

void open_cfw_ambiq_gpu_gradient_create_candidate(
    int stops_count,
    const float *stops,
    const struct open_cfw_ambiq_gpu_gradient_color *colors,
    open_cfw_ambiq_gpu_gradient_texture_id texture,
    const struct open_cfw_ambiq_gpu_gradient_ports *ports
);

#endif /* OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_GRADIENT_CANDIDATE_H */
