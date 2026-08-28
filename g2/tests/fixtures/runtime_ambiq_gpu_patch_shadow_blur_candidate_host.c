/* SPDX-License-Identifier: MIT */

#include "../../components/shared/lvgl/runtime_ambiq_gpu_patch_shadow_blur_candidate.h"

#include <string.h>

enum operation {
    OP_BLEND = 1,
    OP_CLIP,
    OP_BLIT,
    OP_COLOR,
    OP_RECT,
    OP_RGBA,
    OP_CONST_COLOR,
    OP_POP,
};

struct record {
    uint32_t operation;
    uint32_t arguments[8];
};

static struct record records[40];
static uint32_t record_count;

static void append(
    uint32_t operation,
    uint32_t a,
    uint32_t b,
    uint32_t c,
    uint32_t d,
    uint32_t e,
    uint32_t f,
    uint32_t g,
    uint32_t h
)
{
    struct record *record = &records[record_count++];
    record->operation = operation;
    record->arguments[0] = a;
    record->arguments[1] = b;
    record->arguments[2] = c;
    record->arguments[3] = d;
    record->arguments[4] = e;
    record->arguments[5] = f;
    record->arguments[6] = g;
    record->arguments[7] = h;
}

static void blend(uint32_t mode, open_cfw_ambiq_gpu_shadow_texture_id dst,
                  open_cfw_ambiq_gpu_shadow_texture_id fg, uint32_t bg,
                  void *context)
{
    (void)context;
    append(OP_BLEND, mode, dst, fg, bg, 0, 0, 0, 0);
}

static void clip(int32_t x, int32_t y, int32_t w, int32_t h, void *context)
{
    (void)context;
    append(OP_CLIP, (uint32_t)x, (uint32_t)y, (uint32_t)w, (uint32_t)h,
           0, 0, 0, 0);
}

static void blit(int32_t dx, int32_t dy, int32_t dw, int32_t dh,
                 int32_t sx, int32_t sy, int32_t sw, int32_t sh,
                 void *context)
{
    (void)context;
    append(OP_BLIT, (uint32_t)dx, (uint32_t)dy, (uint32_t)dw, (uint32_t)dh,
           (uint32_t)sx, (uint32_t)sy, (uint32_t)sw, (uint32_t)sh);
}

static void color(uint32_t value, void *context)
{
    (void)context;
    append(OP_COLOR, value, 0, 0, 0, 0, 0, 0, 0);
}

static void rect(int32_t x, int32_t y, int32_t w, int32_t h, void *context)
{
    (void)context;
    append(OP_RECT, (uint32_t)x, (uint32_t)y, (uint32_t)w, (uint32_t)h,
           0, 0, 0, 0);
}

static uint32_t rgba(uint8_t r, uint8_t g, uint8_t b, uint8_t a, void *context)
{
    uint32_t packed = (uint32_t)r | (uint32_t)g << 8 |
                      (uint32_t)b << 16 | (uint32_t)a << 24;
    (void)context;
    append(OP_RGBA, r, g, b, a, packed, 0, 0, 0);
    return packed;
}

static void const_color(uint32_t value, void *context)
{
    (void)context;
    append(OP_CONST_COLOR, value, 0, 0, 0, 0, 0, 0, 0);
}

static void pop(void *context)
{
    (void)context;
    append(OP_POP, 0, 0, 0, 0, 0, 0, 0, 0);
}

static const struct open_cfw_ambiq_gpu_shadow_blur_ports ports = {
    0, blend, clip, blit, color, rect, rgba, const_color, pop
};

void open_cfw_test_ambiq_shadow_blur_run(
    int32_t size, int32_t width, uint32_t texture_one, uint32_t texture_two
)
{
    memset(records, 0, sizeof(records));
    record_count = 0;
    open_cfw_ambiq_gpu_shadow_blur_corner_candidate(
        size,
        width,
        (open_cfw_ambiq_gpu_shadow_texture_id)texture_one,
        (open_cfw_ambiq_gpu_shadow_texture_id)texture_two,
        &ports
    );
}

uint32_t open_cfw_test_ambiq_shadow_blur_count(void) { return record_count; }
uint32_t open_cfw_test_ambiq_shadow_blur_operation(uint32_t index)
{
    return records[index].operation;
}
uint32_t open_cfw_test_ambiq_shadow_blur_argument(uint32_t index, uint32_t argument)
{
    return records[index].arguments[argument];
}
