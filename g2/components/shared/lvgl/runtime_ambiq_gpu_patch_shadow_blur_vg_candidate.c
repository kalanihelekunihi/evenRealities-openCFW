/* SPDX-License-Identifier: MIT */
#include "runtime_ambiq_gpu_patch_shadow_blur_vg_candidate.h"
#include <stdint.h>

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_shadow_blur_corner_vg_candidate(
    float size, float shadow_width, uint32_t *shadow_buffer, void *paint,
    void *gradient, const struct open_cfw_ambiq_gpu_shadow_blur_vg_ports *ports
)
{
    struct open_cfw_ambiq_gpu_vg_context_snapshot saved;
    struct open_cfw_ambiq_gpu_vg_color colors[2];
    float stops[2] = {1.0f - shadow_width / size, 1.0f};
    uint32_t integer_size = size > 0.0f ? (uint32_t)size : 0U;
    int32_t signed_size = (int32_t)size;

    colors[0].red = 255.0f;
    colors[0].green = 255.0f;
    colors[0].blue = 255.0f;
    colors[0].alpha = 0.0f;
    colors[1].red = 0.0f;
    colors[1].green = 0.0f;
    colors[1].blue = 0.0f;
    colors[1].alpha = 0.0f;

    ports->get_context_snapshot(&saved, ports->context);
    ports->bind_texture(0U, (uintptr_t)shadow_buffer, integer_size, integer_size,
                        9U, -1, 0U, ports->context);
    ports->set_blend(1U, 0U, UINT32_MAX, UINT32_MAX, ports->context);
    ports->set_clip(0, 0, integer_size, integer_size, ports->context);
    ports->set_raster_color(0U, ports->context);
    ports->raster_rect(0, 0, (uint32_t)signed_size, (uint32_t)signed_size,
                       ports->context);
    ports->vg_set_fill_rule(1U, ports->context);
    ports->vg_set_blend(1U, ports->context);
    ports->vg_grad_set(gradient, 2, stops, colors, ports->context);
    ports->vg_paint_set_type(paint, 3U, ports->context);
    ports->vg_paint_set_grad_radial(
        paint, gradient, 0.0f, size, size, 1U, ports->context
    );
    ports->vg_draw_circle(0.0f, size, size, 0, paint, ports->context);
    ports->bind_texture(
        0U, saved.texture_address, saved.texture_width, saved.texture_height,
        saved.texture_format, (int32_t)saved.texture_stride,
        (saved.texture_stride >> 16) & 0xFFU, ports->context
    );
    ports->set_clip(
        (int32_t)saved.clip_x, (int32_t)saved.clip_y,
        saved.clip_width, saved.clip_height, ports->context
    );
}
