/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room expression of lv_ambiq_shadow_blur_corner().
 * The exact AmbiqSuite 5.1.0 object fixes the complete two-pass box-blur
 * command stream. Indirect ports keep the binary Nema implementation outside
 * this independently authored candidate.
 */

#include "runtime_ambiq_gpu_patch_shadow_blur_candidate.h"

#include <stdint.h>

#define OPEN_CFW_NEMA_NOTEX UINT32_MAX
#define OPEN_CFW_NEMA_BL_SRC_ALPHA 0x08000101U

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_shadow_blur_corner_candidate(
    int32_t size,
    int32_t shadow_width,
    open_cfw_ambiq_gpu_shadow_texture_id texture_one,
    open_cfw_ambiq_gpu_shadow_texture_id texture_two,
    const struct open_cfw_ambiq_gpu_shadow_blur_ports *ports
)
{
    int32_t half_width = shadow_width >> 1;
    int32_t leading_width = half_width - 1;
    int32_t extended_size = size + shadow_width;
    int32_t sample_count;
    uint8_t average_alpha;
    int32_t sample;

    if ((shadow_width & 1) != 0) {
        leading_width = half_width;
    }
    sample_count = leading_width + half_width;
    average_alpha = (uint8_t)(255.0f / (float)shadow_width);

    ports->set_blend(
        1U, texture_two, texture_one, OPEN_CFW_NEMA_NOTEX, ports->context
    );
    ports->set_clip_temp(
        0, 0, extended_size, extended_size, ports->context
    );
    ports->blit_subrect_fit(
        leading_width, leading_width, size, size,
        0, 0, size, size, ports->context
    );
    ports->blit_subrect_fit(
        0, leading_width, leading_width, size,
        0, 0, leading_width, size, ports->context
    );
    ports->blit_subrect_fit(
        leading_width + size, leading_width, half_width, size,
        size - half_width, 0, half_width, size, ports->context
    );

    ports->set_blend(
        1U, texture_one, (open_cfw_ambiq_gpu_shadow_texture_id)UINT8_MAX,
        OPEN_CFW_NEMA_NOTEX, ports->context
    );
    ports->set_clip_temp(0, 0, size, size, ports->context);
    ports->set_raster_color(0U, ports->context);
    ports->raster_rect(0, 0, size, size, ports->context);
    ports->set_blend(
        OPEN_CFW_NEMA_BL_SRC_ALPHA,
        texture_one,
        texture_two,
        OPEN_CFW_NEMA_NOTEX,
        ports->context
    );
    ports->set_const_color(
        ports->rgba(0U, 0U, 0U, average_alpha, ports->context),
        ports->context
    );
    for (sample = 0; sample < sample_count; ++sample) {
        ports->blit_subrect_fit(
            0, 0, size, size,
            sample, leading_width, size, size, ports->context
        );
    }

    ports->set_blend(
        1U, texture_two, texture_one, OPEN_CFW_NEMA_NOTEX, ports->context
    );
    ports->set_clip_temp(
        0, 0, extended_size, extended_size, ports->context
    );
    ports->blit_subrect_fit(
        leading_width, leading_width, size, size,
        0, 0, size, size, ports->context
    );
    ports->blit_subrect_fit(
        leading_width, 0, size, leading_width,
        0, 0, size, leading_width, ports->context
    );
    ports->blit_subrect_fit(
        leading_width, leading_width + size, size, half_width,
        0, size - half_width, size, half_width, ports->context
    );

    ports->set_blend(
        1U, texture_one, (open_cfw_ambiq_gpu_shadow_texture_id)UINT8_MAX,
        OPEN_CFW_NEMA_NOTEX, ports->context
    );
    ports->set_clip_temp(0, 0, size, size, ports->context);
    ports->set_raster_color(0U, ports->context);
    ports->raster_rect(0, 0, size, size, ports->context);
    ports->set_blend(
        OPEN_CFW_NEMA_BL_SRC_ALPHA,
        texture_one,
        texture_two,
        OPEN_CFW_NEMA_NOTEX,
        ports->context
    );
    ports->set_const_color(
        ports->rgba(0U, 0U, 0U, average_alpha, ports->context),
        ports->context
    );
    for (sample = 0; sample <= sample_count; ++sample) {
        ports->blit_subrect_fit(
            0, 0, size, size,
            leading_width, sample, size, size, ports->context
        );
    }

    ports->set_clip_pop(ports->context);
}
