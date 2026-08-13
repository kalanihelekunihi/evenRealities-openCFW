/* SPDX-License-Identifier: GPL-3.0-only */

#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SMALL_RASTER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SMALL_RASTER_CANDIDATE_H

#include <stdint.h>

struct open_cfw_ambiq_gpu_corner_mask_ports {
    void *context;
    void (*bind_texture)(uint8_t texture, uintptr_t address, uint32_t width,
                         uint32_t height, uint32_t format, int32_t stride,
                         uint32_t mode, void *context);
    void (*set_blend)(uint32_t mode, uint32_t destination, uint32_t foreground,
                      uint32_t background, void *context);
    void (*set_clip_temp)(int32_t x, int32_t y, uint32_t width, uint32_t height,
                          void *context);
    void (*set_raster_color)(uint32_t color, void *context);
    void (*raster_rect)(int32_t x, int32_t y, uint32_t width, uint32_t height,
                        void *context);
    uint32_t (*rgba)(uint8_t red, uint8_t green, uint8_t blue, uint8_t alpha,
                     void *context);
    void (*raster_stroked_arc_aa)(float x, float y, float radius, float width,
                                  float start_degrees, float end_degrees,
                                  void *context);
    void (*set_clip_pop)(void *context);
};

struct open_cfw_ambiq_gpu_l8_l4_ports {
    void *context;
    void (*bind_texture)(uint8_t texture, uintptr_t address, uint32_t width,
                         uint32_t height, uint32_t format, int32_t stride,
                         uint32_t mode, void *context);
    void (*set_clip_temp)(int32_t x, int32_t y, uint32_t width, uint32_t height,
                          void *context);
    void (*matrix_load_identity)(float matrix[9], void *context);
    void (*set_matrix)(const float matrix[9], void *context);
    void (*set_blend)(uint32_t mode, uint32_t destination, uint32_t foreground,
                      uint32_t background, void *context);
    void (*set_texture_color)(uint32_t color, void *context);
    void (*set_const_color)(uint32_t color, void *context);
    void (*raster_rect)(int32_t x, int32_t y, uint32_t width, uint32_t height,
                        void *context);
    void (*set_clip_pop)(void *context);
};

void open_cfw_ambiq_gpu_create_corner_mask_candidate(
    uint32_t size, uint32_t shadow_width, uint32_t *shadow_buffer,
    const struct open_cfw_ambiq_gpu_corner_mask_ports *ports
);

uint32_t open_cfw_ambiq_gpu_l8_l4_convert_candidate(
    const void *l8_buffer, void *l4_buffer, uint32_t width, uint32_t height,
    const struct open_cfw_ambiq_gpu_l8_l4_ports *ports
);

#endif /* OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_SMALL_RASTER_CANDIDATE_H */
