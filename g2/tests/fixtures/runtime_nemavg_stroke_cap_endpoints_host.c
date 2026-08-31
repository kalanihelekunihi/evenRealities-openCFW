/* SPDX-License-Identifier: MIT */
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint8_t *host_context;
static unsigned int host_steps = 8U;
static unsigned int host_enable_calls;
static unsigned int host_restore_calls;
static unsigned int host_fan_calls;
static unsigned int host_triangle_calls;
static unsigned int host_quad_calls;
static int host_fan_count;
static float host_quad[8];
static uint32_t host_error;

static int host_calculate_steps(float radius);
static float host_cos(float degrees);
static float host_sin(float degrees);
static float host_sqrt(float value);
static uint32_t host_enable_aa(
    uint8_t edge0, uint8_t edge1, uint8_t edge2, uint8_t edge3);
static uint32_t host_restore_aa(uint32_t flags);
static void host_raster_fan(float *vertices, int count, int stride);
static void host_raster_triangle(
    float x0, float y0, float x1, float y1, float x2, float y2);
static void host_raster_quad(
    float x0, float y0, float x1, float y1,
    float x2, float y2, float x3, float y3);
static void host_set_error(uint32_t error);

#define OPEN_CFW_NEMAVG_CONTEXT_POINTER() host_context
#define OPEN_CFW_NEMAVG_CALCULATE_STEPS host_calculate_steps
#define OPEN_CFW_NEMAVG_COS host_cos
#define OPEN_CFW_NEMAVG_SIN host_sin
#define OPEN_CFW_NEMAVG_SQRT host_sqrt
#define OPEN_CFW_NEMAVG_ENABLE_AA host_enable_aa
#define OPEN_CFW_NEMAVG_RESTORE_AA host_restore_aa
#define OPEN_CFW_NEMAVG_RASTER_TRIANGLE_FAN host_raster_fan
#define OPEN_CFW_NEMAVG_RASTER_TRIANGLE host_raster_triangle
#define OPEN_CFW_NEMAVG_RASTER_QUAD host_raster_quad
#define OPEN_CFW_NEMAVG_SET_ERROR host_set_error
#include "runtime_nemavg_stroke_cap_endpoints.c"

static int host_calculate_steps(float radius)
{
    return radius > 0.0f ? (int)host_steps : 0;
}

static float host_cos(float degrees)
{
    return cosf(degrees * 0.01745329251994329577f);
}

static float host_sin(float degrees)
{
    return sinf(degrees * 0.01745329251994329577f);
}

static float host_sqrt(float value)
{
    return sqrtf(value);
}

static uint32_t host_enable_aa(
    uint8_t edge0, uint8_t edge1, uint8_t edge2, uint8_t edge3)
{
    host_enable_calls++;
    return UINT32_C(0x100) | (uint32_t)edge0 | ((uint32_t)edge1 << 1) |
           ((uint32_t)edge2 << 2) | ((uint32_t)edge3 << 3);
}

static uint32_t host_restore_aa(uint32_t flags)
{
    host_restore_calls++;
    return flags;
}

static void host_raster_fan(float *vertices, int count, int stride)
{
    (void)vertices;
    host_fan_calls++;
    host_fan_count = count;
    if (stride != 2)
        host_fan_count = -1;
}

static void host_raster_triangle(
    float x0, float y0, float x1, float y1, float x2, float y2)
{
    (void)x0;
    (void)y0;
    (void)x1;
    (void)y1;
    (void)x2;
    (void)y2;
    host_triangle_calls++;
}

static void host_raster_quad(
    float x0, float y0, float x1, float y1,
    float x2, float y2, float x3, float y3)
{
    const float values[8] = {x0, y0, x1, y1, x2, y2, x3, y3};
    memcpy(host_quad, values, sizeof(values));
    host_quad_calls++;
}

static void host_set_error(uint32_t error)
{
    host_error = error;
}

static void store_u32(uint8_t *context, size_t offset, uint32_t value)
{
    memcpy(context + offset, &value, sizeof(value));
}

static void store_float(uint8_t *context, size_t offset, float value)
{
    memcpy(context + offset, &value, sizeof(value));
}

static int close_enough(float left, float right)
{
    return fabsf(left - right) < 0.001f;
}

static void initialize_context(uint8_t *context)
{
    memset(context, 0, 0x400U);
    store_u32(context, 0x110U, 1U);
    store_float(context, 0x12cU, 2.0f);
    store_float(context, 0x2d8U, 2.0f);

    /* First line: start edge at x=0, adjacent edge at x=1. */
    store_float(context, 0x138U, 0.0f);
    store_float(context, 0x13cU, -1.0f);
    store_float(context, 0x140U, 1.0f);
    store_float(context, 0x144U, -1.0f);
    store_float(context, 0x148U, 1.0f);
    store_float(context, 0x14cU, 1.0f);
    store_float(context, 0x150U, 0.0f);
    store_float(context, 0x154U, 1.0f);

    /* End line: adjacent edge at x=9, end edge at x=10. */
    store_float(context, 0x190U, 9.0f);
    store_float(context, 0x194U, -1.0f);
    store_float(context, 0x198U, 10.0f);
    store_float(context, 0x19cU, -1.0f);
    store_float(context, 0x1a0U, 10.0f);
    store_float(context, 0x1a4U, 1.0f);
    store_float(context, 0x1a8U, 9.0f);
    store_float(context, 0x1acU, 1.0f);
}

int main(void)
{
    union {
        uint32_t alignment;
        uint8_t bytes[0x400];
    } storage;
    unsigned int checks = 0U;

#define CHECK(expression) do { if (!(expression)) return __LINE__; checks++; } while (0)
    initialize_context(storage.bytes);
    host_context = storage.bytes;

    CHECK(open_cfw_nemavg_draw_start_cap_endpoint() == 0U);
    CHECK(host_quad_calls == 0U && host_fan_calls == 0U);

    storage.bytes[0x2e0U] = 7U;
    CHECK(open_cfw_nemavg_draw_start_cap_endpoint() == UINT32_C(0x00800000));
    store_u32(storage.bytes, 0x114U, 9U);
    store_u32(storage.bytes, 0x118U, 10U);
    CHECK(open_cfw_nemavg_draw_caps_dispatch() == UINT32_C(0x00800000));
    CHECK(host_error == UINT32_C(0x00800000));
    CHECK(open_cfw_nemavg_load_u32(storage.bytes, 0x114U) == 0U &&
          open_cfw_nemavg_load_u32(storage.bytes, 0x118U) == 0U);

    storage.bytes[0x2e0U] = OPEN_CFW_NEMAVG_STYLE_SQUARE;
    CHECK(open_cfw_nemavg_draw_start_cap_endpoint() == 0U);
    CHECK(host_quad_calls == 1U && host_restore_calls == 1U);
    CHECK(close_enough(host_quad[0], 0.0f) &&
          close_enough(host_quad[1], -1.0f));
    CHECK(close_enough(host_quad[4], -1.0f) &&
          close_enough(host_quad[6], -1.0f));

    storage.bytes[0x2e1U] = OPEN_CFW_NEMAVG_STYLE_SQUARE;
    CHECK(open_cfw_nemavg_draw_end_cap_endpoint() == 0U);
    CHECK(host_quad_calls == 2U && close_enough(host_quad[4], 11.0f) &&
          close_enough(host_quad[6], 11.0f));

    storage.bytes[0x2e1U] = OPEN_CFW_NEMAVG_STYLE_ROUND;
    CHECK(open_cfw_nemavg_draw_end_cap_endpoint() == 0U);
    CHECK(host_fan_calls == 1U && host_fan_count == 3);
    CHECK(host_triangle_calls == 1U && host_restore_calls == 3U);

    store_u32(storage.bytes, 0x110U, 0U);
    storage.bytes[0x2e0U] = 9U;
    CHECK(open_cfw_nemavg_draw_start_cap_endpoint() == 0U);
    host_context = NULL;
    CHECK(open_cfw_nemavg_draw_end_cap_endpoint() == 0U);
    return checks == 17U && host_enable_calls == 4U ? 0 : 250;
}
