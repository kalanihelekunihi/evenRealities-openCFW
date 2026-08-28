/* SPDX-License-Identifier: MIT */
#include "runtime_nemavg_stroke_caps_candidate.h"

#include <math.h>
#include <stddef.h>
#include <stdint.h>

struct trace {
    unsigned int begin_count;
    unsigned int end_count;
    unsigned int fan_count;
    unsigned int quad_count;
    unsigned int fail_emit;
    uint8_t last_is_end;
    size_t last_vertex_count;
    struct open_cfw_nemavg_point vertices[96];
};

static int close_enough(float left, float right)
{
    return fabsf(left - right) < 0.001f;
}

static unsigned int segments(void *context, float radius)
{
    (void)context;
    return radius > 0.0f ? 4U : 0U;
}

static float port_sqrt(void *context, float value)
{
    (void)context;
    return sqrtf(value);
}

static int port_sincos(void *context, float angle, float *sine, float *cosine)
{
    (void)context;
    *sine = sinf(angle);
    *cosine = cosf(angle);
    return 0;
}

static int emit_fan(void *context,
                    const struct open_cfw_nemavg_point *vertices,
                    size_t count)
{
    struct trace *trace = context;
    size_t index;
    trace->fan_count++;
    trace->last_vertex_count = count;
    for (index = 0U; index < count && index < 96U; ++index)
        trace->vertices[index] = vertices[index];
    return trace->fail_emit != 0U ? -1 : 0;
}

static int emit_quad(void *context,
                     const struct open_cfw_nemavg_point vertices[4])
{
    struct trace *trace = context;
    size_t index;
    trace->quad_count++;
    trace->last_vertex_count = 4U;
    for (index = 0U; index < 4U; ++index)
        trace->vertices[index] = vertices[index];
    return trace->fail_emit != 0U ? -1 : 0;
}

static uint32_t begin(void *context, uint8_t is_end_cap, uint8_t antialias)
{
    struct trace *trace = context;
    trace->begin_count++;
    trace->last_is_end = is_end_cap;
    return (uint32_t)antialias + 41U;
}

static void end(void *context, uint32_t token)
{
    struct trace *trace = context;
    if (token == 42U)
        trace->end_count++;
}

int main(void)
{
    static const struct open_cfw_nemavg_cap_ports ports = {
        segments, port_sqrt, port_sincos, emit_fan, emit_quad, begin, end,
    };
    struct trace trace = {0};
    struct open_cfw_nemavg_stroke_caps caps = {
        .start = {{0.0f, 0.0f}, {1.0f, 0.0f},
                  {0.0f, -1.0f}, {0.0f, 1.0f}},
        .end = {{10.0f, 0.0f}, {9.0f, 0.0f},
                {10.0f, 1.0f}, {10.0f, -1.0f}},
        .ports = &ports,
        .port_context = &trace,
        .stroke_width = 2.0f,
        .start_style = OPEN_CFW_NEMAVG_CAP_BUTT,
        .end_style = OPEN_CFW_NEMAVG_CAP_BUTT,
        .antialias = 1U,
    };
    unsigned int checks = 0U;

#define CHECK(expression) do { if (!(expression)) return __LINE__; checks++; } while (0)
    CHECK(open_cfw_nemavg_draw_caps(&caps) == OPEN_CFW_NEMAVG_CAP_OK);
    CHECK(trace.begin_count == 0U && trace.fan_count == 0U && trace.quad_count == 0U);

    caps.end_style = OPEN_CFW_NEMAVG_CAP_SQUARE;
    CHECK(open_cfw_nemavg_draw_end_cap(&caps) == OPEN_CFW_NEMAVG_CAP_OK);
    CHECK(trace.quad_count == 1U && trace.begin_count == 1U && trace.end_count == 1U);
    CHECK(trace.last_is_end == 1U && trace.last_vertex_count == 4U);
    CHECK(close_enough(trace.vertices[2].x, 11.0f));
    CHECK(close_enough(trace.vertices[3].x, 11.0f));

    caps.start_style = OPEN_CFW_NEMAVG_CAP_ROUND;
    caps.end_style = OPEN_CFW_NEMAVG_CAP_BUTT;
    CHECK(open_cfw_nemavg_draw_start_cap(&caps) == OPEN_CFW_NEMAVG_CAP_OK);
    CHECK(trace.fan_count == 1U && trace.last_vertex_count == 6U);
    CHECK(trace.last_is_end == 0U);
    CHECK(close_enough(trace.vertices[0].x, 0.0f) &&
          close_enough(trace.vertices[0].y, 0.0f));
    CHECK(trace.vertices[3].x < -0.99f);
    CHECK(close_enough(trace.vertices[5].x, 0.0f) &&
          close_enough(trace.vertices[5].y, 1.0f));

    caps.start_style = 7U;
    CHECK(open_cfw_nemavg_draw_start_cap(&caps) ==
          OPEN_CFW_NEMAVG_CAP_INVALID_STYLE);
    CHECK(open_cfw_nemavg_draw_start_cap(NULL) ==
          OPEN_CFW_NEMAVG_CAP_INVALID_ARGUMENT);

    caps.start_style = OPEN_CFW_NEMAVG_CAP_ROUND;
    trace.fail_emit = 1U;
    CHECK(open_cfw_nemavg_draw_start_cap(&caps) ==
          OPEN_CFW_NEMAVG_CAP_PROVIDER_FAILED);
    CHECK(trace.begin_count == trace.end_count);
    return checks == 17U ? 0 : 250;
}
