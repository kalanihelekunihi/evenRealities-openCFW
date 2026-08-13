/* SPDX-License-Identifier: GPL-3.0-only */

#define OPEN_CFW_AMBIQ_GPU_PATCH_HOST_MODEL 1
#include "../../components/shared/lvgl/runtime_ambiq_gpu_patch_accessors_candidate.h"

#include <string.h>

static struct open_cfw_ambiq_gpu_paint_view paint;
static struct open_cfw_ambiq_gpu_path_view path;
static open_cfw_ambiq_gpu_address image_result;
static open_cfw_ambiq_gpu_address palette_result;
static open_cfw_ambiq_gpu_address segments_result;
static open_cfw_ambiq_gpu_address data_result;
static uint32_t segment_size_result;
static uint32_t data_size_result;
static float bounds_result[4];

void open_cfw_test_ambiq_gpu_reset(void)
{
    memset(&paint, 0, sizeof(paint));
    memset(&path, 0, sizeof(path));
    image_result = 0xAAAAAAAAU;
    palette_result = 0xBBBBBBBBU;
    segments_result = 0xCCCCCCCCU;
    data_result = 0xDDDDDDDDU;
    segment_size_result = 0U;
    data_size_result = 0U;
    memset(bounds_result, 0, sizeof(bounds_result));
}

void open_cfw_test_ambiq_gpu_set_paint(uint32_t image, uint32_t palette, uint32_t is_lut)
{
    paint.texture.image = image;
    paint.texture.palette = palette;
    paint.texture.is_lut_texture = (uint8_t)is_lut;
}

void open_cfw_test_ambiq_gpu_run_paint(void)
{
    open_cfw_ambiq_gpu_get_paint_texture_candidate(&paint, &image_result, &palette_result);
}

void open_cfw_test_ambiq_gpu_set_vbuf(uint32_t segment_size, uint32_t data_size, uint32_t segments, uint32_t data)
{
    path.shape.segment_size = segment_size;
    path.shape.data_size = data_size;
    path.shape.segments = segments;
    path.shape.data = data;
}

void open_cfw_test_ambiq_gpu_run_vbuf(void)
{
    open_cfw_ambiq_gpu_get_path_vbuf_candidate(
        &path, &segment_size_result, &data_size_result, &segments_result, &data_result
    );
}

void open_cfw_test_ambiq_gpu_set_bounds(float x_min, float y_min, float x_max, float y_max)
{
    path.shape.bbox.min.x = x_min;
    path.shape.bbox.min.y = y_min;
    path.shape.bbox.max.x = x_max;
    path.shape.bbox.max.y = y_max;
}

void open_cfw_test_ambiq_gpu_run_bounds(void)
{
    open_cfw_ambiq_gpu_get_path_aabb_candidate(
        &path, &bounds_result[0], &bounds_result[1], &bounds_result[2], &bounds_result[3]
    );
}

uint32_t open_cfw_test_ambiq_gpu_get_image(void) { return image_result; }
uint32_t open_cfw_test_ambiq_gpu_get_palette(void) { return palette_result; }
uint32_t open_cfw_test_ambiq_gpu_get_segments(void) { return segments_result; }
uint32_t open_cfw_test_ambiq_gpu_get_data(void) { return data_result; }
uint32_t open_cfw_test_ambiq_gpu_get_segment_size(void) { return segment_size_result; }
uint32_t open_cfw_test_ambiq_gpu_get_data_size(void) { return data_size_result; }
float open_cfw_test_ambiq_gpu_get_bound(uint32_t index) { return bounds_result[index]; }
