/* SPDX-License-Identifier: GPL-3.0-only */

#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_DASHLINE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_DASHLINE_CANDIDATE_H

#include <stdint.h>

typedef uint8_t open_cfw_ambiq_gpu_texture_id;

struct open_cfw_ambiq_gpu_dashline_ports {
    void *context;
    uint32_t (*texture_width)(open_cfw_ambiq_gpu_texture_id texture, void *context);
    void (*set_clip_temp)(
        int32_t x, int32_t y, uint32_t width, uint32_t height, void *context
    );
    void (*set_blend)(
        uint32_t source, open_cfw_ambiq_gpu_texture_id texture,
        uint32_t foreground, uint32_t background, void *context
    );
    void (*set_raster_color)(uint32_t color, void *context);
    void (*raster_rect)(
        int32_t x, int32_t y, uint32_t width, uint32_t height, void *context
    );
    void (*set_clip_pop)(void *context);
};

void open_cfw_ambiq_gpu_dashline_create_candidate(
    uint32_t dash_width,
    uint32_t dash_gap,
    uint32_t rgba_color,
    open_cfw_ambiq_gpu_texture_id texture,
    const struct open_cfw_ambiq_gpu_dashline_ports *ports
);

#endif /* OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_DASHLINE_CANDIDATE_H */
