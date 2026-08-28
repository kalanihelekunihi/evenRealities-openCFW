/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room expressions of two small Ambiq GPU-patch
 * raster pipelines recovered from the exact AmbiqSuite 5.1.0 object.
 */

#include "runtime_ambiq_gpu_patch_small_raster_candidate.h"

#include <stdint.h>

#define OPEN_CFW_NEMA_NOTEX UINT32_MAX

__attribute__((used, noinline))
void open_cfw_ambiq_gpu_create_corner_mask_candidate(
    uint32_t size, uint32_t shadow_width, uint32_t *shadow_buffer,
    const struct open_cfw_ambiq_gpu_corner_mask_ports *ports
)
{
    uint32_t inner = size - shadow_width;
    uint32_t white;

    ports->bind_texture(1U, (uintptr_t)shadow_buffer, size, size, 8U, -1, 0U,
                        ports->context);
    ports->set_blend(1U, 1U, OPEN_CFW_NEMA_NOTEX, OPEN_CFW_NEMA_NOTEX,
                     ports->context);
    ports->set_clip_temp(0, 0, size, size, ports->context);
    ports->set_raster_color(0U, ports->context);
    ports->raster_rect(0, 0, size, size, ports->context);
    ports->set_clip_temp(0, (int32_t)shadow_width, inner, size, ports->context);
    white = ports->rgba(255U, 255U, 255U, 255U, ports->context);
    ports->set_raster_color(white, ports->context);
    ports->raster_stroked_arc_aa(
        0.0f, (float)size, 0.0f, (float)inner, 270.0f, 360.0f,
        ports->context
    );
    ports->set_clip_pop(ports->context);
}

__attribute__((used, noinline))
uint32_t open_cfw_ambiq_gpu_l8_l4_convert_candidate(
    const void *l8_buffer, void *l4_buffer, uint32_t width, uint32_t height,
    const struct open_cfw_ambiq_gpu_l8_l4_ports *ports
)
{
    uint32_t output_width;
    float matrix[9];

    if ((width & 1U) != 0U) {
        return 0U;
    }

    output_width = width >> 1;
    ports->bind_texture(2U, (uintptr_t)l4_buffer, output_width, height, 0x45U,
                        (int32_t)output_width, 0U, ports->context);
    ports->set_clip_temp(0, 0, output_width, height, ports->context);
    ports->bind_texture(1U, (uintptr_t)l8_buffer, width << 1, height, 0x34U,
                        (int32_t)width, 0U, ports->context);
    ports->matrix_load_identity(matrix, ports->context);
    matrix[0] = 4.0f;
    matrix[2] = -2.0f;
    ports->set_matrix(matrix, ports->context);
    ports->set_blend(1U, 2U, 1U, OPEN_CFW_NEMA_NOTEX, ports->context);
    ports->set_texture_color(0xFF000000U, ports->context);
    ports->raster_rect(0, 0, output_width, height, ports->context);

    ports->bind_texture(1U, (uintptr_t)l8_buffer, width << 1, height, 0x35U,
                        (int32_t)width, 0U, ports->context);
    ports->matrix_load_identity(matrix, ports->context);
    matrix[0] = 4.0f;
    matrix[2] = 0.0f;
    ports->set_matrix(matrix, ports->context);
    ports->set_blend(0x10000101U, 2U, 1U, OPEN_CFW_NEMA_NOTEX,
                     ports->context);
    ports->set_const_color(0U, ports->context);
    ports->raster_rect(0, 0, output_width, height, ports->context);
    ports->set_clip_pop(ports->context);
    return 0U;
}
