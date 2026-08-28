/* SPDX-License-Identifier: MIT */

#include "../../components/shared/lvgl/runtime_ambiq_gpu_patch_dashline_candidate.h"

#include <string.h>

enum operation {
    OP_WIDTH = 1,
    OP_CLIP,
    OP_BLEND,
    OP_COLOR,
    OP_RECT,
    OP_POP,
};

struct record {
    uint32_t operation;
    uint32_t arguments[4];
};

static struct record records[8];
static uint32_t record_count;
static uint32_t configured_width;

static void append(uint32_t operation, uint32_t a, uint32_t b, uint32_t c, uint32_t d)
{
    records[record_count].operation = operation;
    records[record_count].arguments[0] = a;
    records[record_count].arguments[1] = b;
    records[record_count].arguments[2] = c;
    records[record_count].arguments[3] = d;
    ++record_count;
}

static uint32_t width(open_cfw_ambiq_gpu_texture_id texture, void *context)
{
    (void)context;
    append(OP_WIDTH, texture, 0, 0, 0);
    return configured_width;
}

static void clip(int32_t x, int32_t y, uint32_t w, uint32_t h, void *context)
{
    (void)context;
    append(OP_CLIP, (uint32_t)x, (uint32_t)y, w, h);
}

static void blend(uint32_t source, open_cfw_ambiq_gpu_texture_id texture, uint32_t fg, uint32_t bg, void *context)
{
    (void)context;
    append(OP_BLEND, source, texture, fg, bg);
}

static void color(uint32_t value, void *context)
{
    (void)context;
    append(OP_COLOR, value, 0, 0, 0);
}

static void rect(int32_t x, int32_t y, uint32_t w, uint32_t h, void *context)
{
    (void)context;
    append(OP_RECT, (uint32_t)x, (uint32_t)y, w, h);
}

static void pop(void *context)
{
    (void)context;
    append(OP_POP, 0, 0, 0, 0);
}

static const struct open_cfw_ambiq_gpu_dashline_ports ports = {
    0, width, clip, blend, color, rect, pop
};

void open_cfw_test_ambiq_dashline_run(uint32_t dash, uint32_t gap, uint32_t rgba, uint32_t texture, uint32_t texture_width)
{
    memset(records, 0, sizeof(records));
    record_count = 0;
    configured_width = texture_width;
    open_cfw_ambiq_gpu_dashline_create_candidate(
        dash, gap, rgba, (open_cfw_ambiq_gpu_texture_id)texture, &ports
    );
}

uint32_t open_cfw_test_ambiq_dashline_count(void) { return record_count; }
uint32_t open_cfw_test_ambiq_dashline_operation(uint32_t index) { return records[index].operation; }
uint32_t open_cfw_test_ambiq_dashline_argument(uint32_t index, uint32_t argument)
{
    return records[index].arguments[argument];
}
