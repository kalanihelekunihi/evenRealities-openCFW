/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room expression of lv_ambiq_dashline_create().
 * The exact public GCC body, exact stock IAR body, and all six Nema effects
 * agree.  Indirect ports keep the binary Nema implementation outside this
 * independently authored candidate.
 */

#include "runtime_ambiq_gpu_patch_dashline_candidate.h"

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_dashline_create_candidate(
    uint32_t dash_width,
    uint32_t dash_gap,
    uint32_t rgba_color,
    open_cfw_ambiq_gpu_texture_id texture,
    const struct open_cfw_ambiq_gpu_dashline_ports *ports
)
{
    uint32_t texture_width = ports->texture_width(texture, ports->context);
    float ratio;
    uint32_t dash_pixels;

    ports->set_clip_temp(0, 0, texture_width, 1U, ports->context);
    ports->set_blend(
        1U, texture, UINT32_MAX, UINT32_MAX, ports->context
    );

    ratio = (float)dash_width / (float)(dash_width + dash_gap);
    dash_pixels = (uint32_t)(ratio * (float)texture_width);

    ports->set_raster_color(rgba_color, ports->context);
    ports->raster_rect(0, 0, dash_pixels, 1U, ports->context);
    ports->set_raster_color(0U, ports->context);
    ports->raster_rect(
        (int32_t)dash_pixels,
        0,
        texture_width - dash_pixels,
        1U,
        ports->context
    );
    ports->set_clip_pop(ports->context);
}
