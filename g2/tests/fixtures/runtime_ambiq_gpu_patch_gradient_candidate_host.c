/* SPDX-License-Identifier: GPL-3.0-only */

#include "../../components/shared/lvgl/runtime_ambiq_gpu_patch_gradient_candidate.h"

#include <string.h>

enum operation {
    OP_WIDTH = 1,
    OP_CLIP,
    OP_BLEND,
    OP_ENABLE,
    OP_GRADIENT,
    OP_FILL,
    OP_INTERPOLATE,
    OP_RGBA,
    OP_POP,
};

struct record {
    uint32_t operation;
    uint32_t arguments[5];
    float values[12];
};

static struct record records[24];
static uint32_t record_count;
static uint32_t configured_width;

static struct record *append(uint32_t operation)
{
    struct record *record = &records[record_count++];
    record->operation = operation;
    return record;
}

static uint32_t texture_width(open_cfw_ambiq_gpu_gradient_texture_id texture, void *context)
{
    struct record *record;
    (void)context;
    record = append(OP_WIDTH);
    record->arguments[0] = texture;
    return configured_width;
}

static void clip(int32_t x, int32_t y, uint32_t width, uint32_t height, void *context)
{
    struct record *record;
    (void)context;
    record = append(OP_CLIP);
    record->arguments[0] = (uint32_t)x;
    record->arguments[1] = (uint32_t)y;
    record->arguments[2] = width;
    record->arguments[3] = height;
}

static void blend(uint32_t mode, open_cfw_ambiq_gpu_gradient_texture_id destination,
                  uint32_t foreground, uint32_t background, void *context)
{
    struct record *record;
    (void)context;
    record = append(OP_BLEND);
    record->arguments[0] = mode;
    record->arguments[1] = destination;
    record->arguments[2] = foreground;
    record->arguments[3] = background;
}

static void enable(int enabled, void *context)
{
    struct record *record;
    (void)context;
    record = append(OP_ENABLE);
    record->arguments[0] = (uint32_t)enabled;
}

static void gradient(float ri, float gi, float bi, float ai,
                     float rdx, float rdy, float gdx, float gdy,
                     float bdx, float bdy, float adx, float ady,
                     void *context)
{
    struct record *record;
    (void)context;
    record = append(OP_GRADIENT);
    record->values[0] = ri;
    record->values[1] = gi;
    record->values[2] = bi;
    record->values[3] = ai;
    record->values[4] = rdx;
    record->values[5] = rdy;
    record->values[6] = gdx;
    record->values[7] = gdy;
    record->values[8] = bdx;
    record->values[9] = bdy;
    record->values[10] = adx;
    record->values[11] = ady;
}

static void fill(int32_t x, int32_t y, uint32_t width, uint32_t height,
                 uint32_t color, void *context)
{
    struct record *record;
    (void)context;
    record = append(OP_FILL);
    record->arguments[0] = (uint32_t)x;
    record->arguments[1] = (uint32_t)y;
    record->arguments[2] = width;
    record->arguments[3] = height;
    record->arguments[4] = color;
}

static void interpolate(
    int32_t x, int32_t y, uint32_t width, uint32_t height,
    const struct open_cfw_ambiq_gpu_gradient_color *first,
    const struct open_cfw_ambiq_gpu_gradient_color *second,
    const struct open_cfw_ambiq_gpu_gradient_color *third,
    void *context
)
{
    const struct open_cfw_ambiq_gpu_gradient_color *colors[3] = {first, second, third};
    struct record *record;
    uint32_t index;
    (void)context;
    record = append(OP_INTERPOLATE);
    record->arguments[0] = (uint32_t)x;
    record->arguments[1] = (uint32_t)y;
    record->arguments[2] = width;
    record->arguments[3] = height;
    for (index = 0; index < 3; ++index) {
        record->values[index * 4] = colors[index]->red;
        record->values[index * 4 + 1] = colors[index]->green;
        record->values[index * 4 + 2] = colors[index]->blue;
        record->values[index * 4 + 3] = colors[index]->alpha;
    }
}

static uint32_t rgba(uint8_t red, uint8_t green, uint8_t blue, uint8_t alpha, void *context)
{
    struct record *record;
    uint32_t result = (uint32_t)red << 24 | (uint32_t)green << 16 |
                      (uint32_t)blue << 8 | alpha;
    (void)context;
    record = append(OP_RGBA);
    record->arguments[0] = red;
    record->arguments[1] = green;
    record->arguments[2] = blue;
    record->arguments[3] = alpha;
    record->arguments[4] = result;
    return result;
}

static void pop(void *context)
{
    (void)context;
    (void)append(OP_POP);
}

static const struct open_cfw_ambiq_gpu_gradient_ports ports = {
    0, texture_width, clip, blend, enable, gradient, fill, interpolate, rgba, pop
};

void open_cfw_test_ambiq_gradient_run(
    int stops_count,
    const float *stops,
    const struct open_cfw_ambiq_gpu_gradient_color *colors,
    uint32_t texture,
    uint32_t width
)
{
    memset(records, 0, sizeof(records));
    record_count = 0;
    configured_width = width;
    open_cfw_ambiq_gpu_gradient_create_candidate(
        stops_count,
        stops,
        colors,
        (open_cfw_ambiq_gpu_gradient_texture_id)texture,
        &ports
    );
}

uint32_t open_cfw_test_ambiq_gradient_count(void) { return record_count; }
uint32_t open_cfw_test_ambiq_gradient_operation(uint32_t index)
{
    return records[index].operation;
}
uint32_t open_cfw_test_ambiq_gradient_argument(uint32_t index, uint32_t argument)
{
    return records[index].arguments[argument];
}
float open_cfw_test_ambiq_gradient_value(uint32_t index, uint32_t value)
{
    return records[index].values[value];
}
