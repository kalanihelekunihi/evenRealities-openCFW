/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded clean-room expression of lv_ambiq_gradient_create()
 * for G2's recovered LV_GRADIENT_MAX_STOPS == 2 caller contract. Exact public
 * object emulation fixes all observable Nema effects for this boundary.
 */

#include "runtime_ambiq_gpu_patch_gradient_candidate.h"

#include <stdint.h>

#define OPEN_CFW_NEMA_NOTEX UINT32_MAX
#define OPEN_CFW_NEMA_BL_SIMPLE 1U
#define OPEN_CFW_GRADIENT_ENDPOINT_PIXEL 63

static uint8_t channel_to_u8(float channel)
{
    if (!(channel > 0.0f)) {
        return 0U;
    }
    return (uint8_t)(int32_t)channel;
}

static void emit_segment(
    float first_stop,
    float second_stop,
    const struct open_cfw_ambiq_gpu_gradient_color *first,
    const struct open_cfw_ambiq_gpu_gradient_color *second,
    uint32_t width,
    const struct open_cfw_ambiq_gpu_gradient_ports *ports
)
{
    float width_float = (float)width;
    float sample_span = (float)(width - 1U);
    float first_sample = first_stop * sample_span + 0.5f;
    float second_sample = second_stop * sample_span + 0.5f;
    int32_t first_pixel = (int32_t)(first_stop * width_float);
    int32_t second_pixel = (int32_t)(second_stop * width_float);
    float distance = second_sample - first_sample;
    float red_dx = (second->red - first->red) / distance;
    float green_dx = (second->green - first->green) / distance;
    float blue_dx = (second->blue - first->blue) / distance;
    float alpha_dx = (second->alpha - first->alpha) / distance;
    float fraction = first_sample - (float)(int32_t)first_sample;
    float distance_to_center;

    if (fraction <= 0.5f) {
        distance_to_center = 0.5f - fraction;
    }
    else {
        distance_to_center = 1.5f - fraction;
    }

    ports->set_gradient(
        first->red + red_dx * distance_to_center,
        first->green + green_dx * distance_to_center,
        first->blue + blue_dx * distance_to_center,
        first->alpha + alpha_dx * distance_to_center,
        red_dx, 0.0f,
        green_dx, 0.0f,
        blue_dx, 0.0f,
        alpha_dx, 0.0f,
        ports->context
    );
    ports->fill_rect(
        first_pixel,
        0,
        (uint32_t)(second_pixel - first_pixel),
        1U,
        UINT32_MAX,
        ports->context
    );
}

static void emit_invalid_fallback(
    uint32_t width,
    const struct open_cfw_ambiq_gpu_gradient_ports *ports
)
{
    const struct open_cfw_ambiq_gpu_gradient_color transparent_black = {
        0.0f, 0.0f, 0.0f, 0.0f
    };
    const struct open_cfw_ambiq_gpu_gradient_color opaque_white = {
        255.0f, 255.0f, 255.0f, 255.0f
    };

    ports->interpolate_rect_colors(
        0, 0, width, 1U,
        &transparent_black, &opaque_white, &opaque_white,
        ports->context
    );
    ports->fill_rect(0, 0, width, 1U, UINT32_MAX, ports->context);
}

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_gradient_create_candidate(
    int stops_count,
    const float *stops,
    const struct open_cfw_ambiq_gpu_gradient_color *colors,
    open_cfw_ambiq_gpu_gradient_texture_id texture,
    const struct open_cfw_ambiq_gpu_gradient_ports *ports
)
{
    uint32_t width = ports->texture_width(texture, ports->context);
    uint32_t packed;

    ports->set_clip_temp(0, 0, width, 1U, ports->context);
    ports->set_blend(
        OPEN_CFW_NEMA_BL_SIMPLE,
        texture,
        OPEN_CFW_NEMA_NOTEX,
        OPEN_CFW_NEMA_NOTEX,
        ports->context
    );
    ports->enable_gradient(1, ports->context);

    if (
        stops_count != 2
        || stops == 0
        || colors == 0
        || !(stops[0] >= 0.0f && stops[0] <= 1.0f)
        || !(stops[1] >= 0.0f && stops[1] <= 1.0f)
        || stops[1] < stops[0]
    ) {
        emit_invalid_fallback(width, ports);
        ports->enable_gradient(0, ports->context);
        ports->set_clip_pop(ports->context);
        return;
    }

    if (stops[0] > 0.0f) {
        emit_segment(0.0f, stops[0], &colors[0], &colors[0], width, ports);
    }
    emit_segment(stops[0], stops[1], &colors[0], &colors[1], width, ports);
    if (stops[1] < 1.0f) {
        emit_segment(stops[1], 1.0f, &colors[1], &colors[1], width, ports);
    }

    ports->enable_gradient(0, ports->context);
    packed = ports->rgba(
        channel_to_u8(colors[0].red),
        channel_to_u8(colors[0].green),
        channel_to_u8(colors[0].blue),
        channel_to_u8(colors[0].alpha),
        ports->context
    );
    ports->fill_rect(0, 0, 1U, 1U, packed, ports->context);
    packed = ports->rgba(
        channel_to_u8(colors[1].red),
        channel_to_u8(colors[1].green),
        channel_to_u8(colors[1].blue),
        channel_to_u8(colors[1].alpha),
        ports->context
    );
    ports->fill_rect(
        OPEN_CFW_GRADIENT_ENDPOINT_PIXEL,
        0,
        1U,
        1U,
        packed,
        ports->context
    );
    ports->enable_gradient(0, ports->context);
    ports->set_clip_pop(ports->context);

}
