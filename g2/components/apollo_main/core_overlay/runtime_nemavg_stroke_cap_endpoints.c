/* SPDX-License-Identifier: MIT */
/*
 * Source-owned NemaVG stroke-cap endpoint providers for the G2 Apollo image.
 *
 * The no-argument ABI, context pointer cell, context member offsets, cap-style
 * values, and retained NemaGFX provider ABIs are authenticated against the G2
 * image and the public Apollo5 NemaVG 1.1.8 archive.  Geometry is emitted via
 * the retained public NemaGFX raster API; no vendor instruction bytes are
 * embedded here.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_NEMAVG_OK UINT32_C(0)
#define OPEN_CFW_NEMAVG_INVALID_STYLE UINT32_C(0x00800000)
#define OPEN_CFW_NEMAVG_STYLE_BUTT UINT8_C(0)
#define OPEN_CFW_NEMAVG_STYLE_ROUND UINT8_C(1)
#define OPEN_CFW_NEMAVG_STYLE_SQUARE UINT8_C(2)

#define OPEN_CFW_NEMAVG_CONTEXT_ACTIVE_OFFSET UINT32_C(0x110)
#define OPEN_CFW_NEMAVG_QUALITY_OFFSET UINT32_C(0x07d)
#define OPEN_CFW_NEMAVG_SCREEN_STROKE_WIDTH_OFFSET UINT32_C(0x12c)
#define OPEN_CFW_NEMAVG_FIRST_LINE_OFFSET UINT32_C(0x138)
#define OPEN_CFW_NEMAVG_END_LINE_OFFSET UINT32_C(0x190)
#define OPEN_CFW_NEMAVG_STROKE_WIDTH_OFFSET UINT32_C(0x2d8)
#define OPEN_CFW_NEMAVG_START_STYLE_OFFSET UINT32_C(0x2e0)
#define OPEN_CFW_NEMAVG_END_STYLE_OFFSET UINT32_C(0x2e1)
#define OPEN_CFW_NEMAVG_QUALITY_DISABLE_AA UINT8_C(0x10)
#define OPEN_CFW_NEMAVG_MAX_HALF_STEPS 48

#if !defined(OPEN_CFW_NEMAVG_STROKE_CAPS_START_ONLY) &&                    \
    !defined(OPEN_CFW_NEMAVG_STROKE_CAPS_END_ONLY) &&                      \
    !defined(OPEN_CFW_NEMAVG_STROKE_CAPS_DISPATCH_ONLY)
#define OPEN_CFW_NEMAVG_STROKE_CAPS_BUILD_ALL 1
#endif

struct open_cfw_nemavg_point {
    float x;
    float y;
};

struct open_cfw_nemavg_line {
    struct open_cfw_nemavg_point q0;
    struct open_cfw_nemavg_point q1;
    struct open_cfw_nemavg_point q2;
    struct open_cfw_nemavg_point q3;
    float length;
    float dx;
    float dy;
};

#ifndef OPEN_CFW_NEMAVG_CONTEXT_POINTER
#define OPEN_CFW_NEMAVG_CONTEXT_POINTER()                                    \
    (*(volatile uint8_t *volatile *)(uintptr_t)UINT32_C(0x20074F04))
#endif

#ifndef OPEN_CFW_NEMAVG_CALCULATE_STEPS
int open_cfw_retained_nemavg_calculate_steps(float radius);
#define OPEN_CFW_NEMAVG_CALCULATE_STEPS                                      \
    open_cfw_retained_nemavg_calculate_steps
#endif

#ifndef OPEN_CFW_NEMAVG_COS
float open_cfw_retained_nemavg_cos(float angle_degrees);
#define OPEN_CFW_NEMAVG_COS open_cfw_retained_nemavg_cos
#endif

#ifndef OPEN_CFW_NEMAVG_SIN
float open_cfw_retained_nemavg_sin(float angle_degrees);
#define OPEN_CFW_NEMAVG_SIN open_cfw_retained_nemavg_sin
#endif

#ifndef OPEN_CFW_NEMAVG_SQRT
float open_cfw_retained_nemavg_sqrt(float value);
#define OPEN_CFW_NEMAVG_SQRT open_cfw_retained_nemavg_sqrt
#endif

#ifndef OPEN_CFW_NEMAVG_ENABLE_AA
uint32_t open_cfw_retained_nemavg_enable_aa(
    uint8_t edge0, uint8_t edge1, uint8_t edge2, uint8_t edge3);
#define OPEN_CFW_NEMAVG_ENABLE_AA open_cfw_retained_nemavg_enable_aa
#endif

#ifndef OPEN_CFW_NEMAVG_RESTORE_AA
uint32_t open_cfw_retained_nemavg_restore_aa(uint32_t flags);
#define OPEN_CFW_NEMAVG_RESTORE_AA open_cfw_retained_nemavg_restore_aa
#endif

#ifndef OPEN_CFW_NEMAVG_RASTER_TRIANGLE_FAN
void open_cfw_retained_nemavg_raster_triangle_fan(
    float *vertices, int vertex_count, int stride);
#define OPEN_CFW_NEMAVG_RASTER_TRIANGLE_FAN                                  \
    open_cfw_retained_nemavg_raster_triangle_fan
#endif

#ifndef OPEN_CFW_NEMAVG_RASTER_TRIANGLE
void open_cfw_retained_nemavg_raster_triangle(
    float x0, float y0, float x1, float y1, float x2, float y2);
#define OPEN_CFW_NEMAVG_RASTER_TRIANGLE                                      \
    open_cfw_retained_nemavg_raster_triangle
#endif

#ifndef OPEN_CFW_NEMAVG_RASTER_QUAD
void open_cfw_retained_nemavg_raster_quad(
    float x0, float y0, float x1, float y1,
    float x2, float y2, float x3, float y3);
#define OPEN_CFW_NEMAVG_RASTER_QUAD open_cfw_retained_nemavg_raster_quad
#endif

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_NEMAVG_ALWAYS_INLINE                                        \
    static __attribute__((always_inline, unused)) inline
#else
#define OPEN_CFW_NEMAVG_ALWAYS_INLINE static inline
#endif

OPEN_CFW_NEMAVG_ALWAYS_INLINE uint32_t
open_cfw_nemavg_load_u32(const volatile uint8_t *context, uint32_t offset)
{
    return *(const volatile uint32_t *)(const volatile void *)(context + offset);
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE float
open_cfw_nemavg_load_float(const volatile uint8_t *context, uint32_t offset)
{
    return *(const volatile float *)(const volatile void *)(context + offset);
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE struct open_cfw_nemavg_point
open_cfw_nemavg_load_point(const volatile uint8_t *context, uint32_t offset)
{
    struct open_cfw_nemavg_point point;
    point.x = open_cfw_nemavg_load_float(context, offset);
    point.y = open_cfw_nemavg_load_float(context, offset + UINT32_C(4));
    return point;
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE struct open_cfw_nemavg_point
open_cfw_nemavg_add(struct open_cfw_nemavg_point left,
                    struct open_cfw_nemavg_point right)
{
    struct open_cfw_nemavg_point result = {
        left.x + right.x, left.y + right.y
    };
    return result;
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE struct open_cfw_nemavg_point
open_cfw_nemavg_subtract(struct open_cfw_nemavg_point left,
                         struct open_cfw_nemavg_point right)
{
    struct open_cfw_nemavg_point result = {
        left.x - right.x, left.y - right.y
    };
    return result;
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE struct open_cfw_nemavg_point
open_cfw_nemavg_scale(struct open_cfw_nemavg_point value, float scale)
{
    struct open_cfw_nemavg_point result = {
        value.x * scale, value.y * scale
    };
    return result;
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE struct open_cfw_nemavg_point
open_cfw_nemavg_midpoint(struct open_cfw_nemavg_point left,
                         struct open_cfw_nemavg_point right)
{
    return open_cfw_nemavg_scale(open_cfw_nemavg_add(left, right), 0.5f);
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE struct open_cfw_nemavg_point
open_cfw_nemavg_rotate(struct open_cfw_nemavg_point value,
                       float sine, float cosine)
{
    struct open_cfw_nemavg_point result = {
        cosine * value.x - sine * value.y,
        sine * value.x + cosine * value.y
    };
    return result;
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE void
open_cfw_nemavg_load_line(const volatile uint8_t *context, uint32_t offset,
                          struct open_cfw_nemavg_line *line)
{
    line->q0 = open_cfw_nemavg_load_point(context, offset);
    line->q1 = open_cfw_nemavg_load_point(context, offset + UINT32_C(8));
    line->q2 = open_cfw_nemavg_load_point(context, offset + UINT32_C(16));
    line->q3 = open_cfw_nemavg_load_point(context, offset + UINT32_C(24));
    line->length = open_cfw_nemavg_load_float(context, offset + UINT32_C(32));
    line->dx = open_cfw_nemavg_load_float(context, offset + UINT32_C(36));
    line->dy = open_cfw_nemavg_load_float(context, offset + UINT32_C(40));
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE uint8_t
open_cfw_nemavg_aa_disabled(const volatile uint8_t *context)
{
    return (uint8_t)((context[OPEN_CFW_NEMAVG_QUALITY_OFFSET] &
                      OPEN_CFW_NEMAVG_QUALITY_DISABLE_AA) != 0U);
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE void
open_cfw_nemavg_fill_round(const volatile uint8_t *context,
                           struct open_cfw_nemavg_point center,
                           struct open_cfw_nemavg_point direction,
                           float radius, uint8_t is_end_cap)
{
    struct open_cfw_nemavg_point vertices[OPEN_CFW_NEMAVG_MAX_HALF_STEPS];
    float angle;
    float cosine;
    float sine;
    int steps;
    int half_steps;
    int index;
    uint32_t previous_aa;

    if (!(radius > 0.0f))
        return;
    steps = OPEN_CFW_NEMAVG_CALCULATE_STEPS(radius);
    half_steps = steps / 2;
    if (half_steps < 2)
        half_steps = 2;
    if (half_steps > OPEN_CFW_NEMAVG_MAX_HALF_STEPS)
        half_steps = OPEN_CFW_NEMAVG_MAX_HALF_STEPS;
    angle = 180.0f / (float)half_steps;
    cosine = OPEN_CFW_NEMAVG_COS(angle);
    sine = OPEN_CFW_NEMAVG_SIN(angle);
    if (is_end_cap == 0U)
        sine = -sine;

    vertices[0] = open_cfw_nemavg_add(
        center, open_cfw_nemavg_scale(direction, -radius));
    for (index = 1; index < half_steps; ++index) {
        direction = open_cfw_nemavg_rotate(direction, sine, cosine);
        vertices[index] = open_cfw_nemavg_add(
            center, open_cfw_nemavg_scale(direction, radius));
    }

    previous_aa = open_cfw_nemavg_aa_disabled(context) != 0U
        ? OPEN_CFW_NEMAVG_ENABLE_AA(0U, 0U, 0U, 0U)
        : OPEN_CFW_NEMAVG_ENABLE_AA(0U, 1U, 0U, 0U);
    OPEN_CFW_NEMAVG_RASTER_TRIANGLE_FAN(
        &vertices[0].x, half_steps - 1, 2);
    if (open_cfw_nemavg_aa_disabled(context) != 0U)
        (void)OPEN_CFW_NEMAVG_ENABLE_AA(0U, 0U, 0U, 0U);
    else
        (void)OPEN_CFW_NEMAVG_ENABLE_AA(0U, 1U, 1U, 0U);
    OPEN_CFW_NEMAVG_RASTER_TRIANGLE(
        vertices[0].x, vertices[0].y,
        vertices[half_steps - 2].x, vertices[half_steps - 2].y,
        vertices[half_steps - 1].x, vertices[half_steps - 1].y);
    (void)OPEN_CFW_NEMAVG_RESTORE_AA(previous_aa);
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE void
open_cfw_nemavg_draw_round(const volatile uint8_t *context,
                           uint8_t is_end_cap)
{
    struct open_cfw_nemavg_line first;
    struct open_cfw_nemavg_line end;
    struct open_cfw_nemavg_point center;
    struct open_cfw_nemavg_point direction;
    float width = open_cfw_nemavg_load_float(
        context, OPEN_CFW_NEMAVG_STROKE_WIDTH_OFFSET);

    if (!(width > 0.0f))
        return;
    open_cfw_nemavg_load_line(context, OPEN_CFW_NEMAVG_FIRST_LINE_OFFSET, &first);
    open_cfw_nemavg_load_line(context, OPEN_CFW_NEMAVG_END_LINE_OFFSET, &end);
    if (end.q0.x == end.q1.x && end.q0.y == end.q1.y &&
        end.q2.x == end.q3.x && end.q2.y == end.q3.y) {
        center = open_cfw_nemavg_midpoint(end.q0, end.q2);
        direction = open_cfw_nemavg_scale(
            open_cfw_nemavg_subtract(end.q0, end.q2), 1.0f / width);
    } else if (is_end_cap != 0U) {
        center = open_cfw_nemavg_midpoint(end.q1, end.q2);
        direction = open_cfw_nemavg_scale(
            open_cfw_nemavg_subtract(end.q2, end.q1), 1.0f / width);
    } else {
        center = open_cfw_nemavg_midpoint(first.q0, first.q3);
        direction = open_cfw_nemavg_scale(
            open_cfw_nemavg_subtract(first.q3, first.q0), 1.0f / width);
    }
    open_cfw_nemavg_fill_round(context, center, direction,
                               width * 0.5f, is_end_cap);
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE void
open_cfw_nemavg_draw_square(const volatile uint8_t *context,
                            uint8_t is_end_cap)
{
    struct open_cfw_nemavg_line first;
    struct open_cfw_nemavg_line end;
    struct open_cfw_nemavg_point edge0;
    struct open_cfw_nemavg_point edge1;
    struct open_cfw_nemavg_point center;
    struct open_cfw_nemavg_point adjacent;
    struct open_cfw_nemavg_point outward;
    struct open_cfw_nemavg_point shifted0;
    struct open_cfw_nemavg_point shifted1;
    float length;
    float half_width = open_cfw_nemavg_load_float(
        context, OPEN_CFW_NEMAVG_SCREEN_STROKE_WIDTH_OFFSET) * 0.5f;
    uint32_t previous_aa;

    if (!(half_width > 0.0f))
        return;
    open_cfw_nemavg_load_line(context, OPEN_CFW_NEMAVG_FIRST_LINE_OFFSET, &first);
    open_cfw_nemavg_load_line(context, OPEN_CFW_NEMAVG_END_LINE_OFFSET, &end);
    if (is_end_cap != 0U) {
        edge0 = end.q1;
        edge1 = end.q2;
        center = open_cfw_nemavg_midpoint(edge0, edge1);
        adjacent = open_cfw_nemavg_midpoint(end.q0, end.q3);
    } else {
        edge0 = first.q0;
        edge1 = first.q3;
        center = open_cfw_nemavg_midpoint(edge0, edge1);
        adjacent = open_cfw_nemavg_midpoint(first.q1, first.q2);
    }
    outward = open_cfw_nemavg_subtract(center, adjacent);
    length = OPEN_CFW_NEMAVG_SQRT(
        outward.x * outward.x + outward.y * outward.y);
    if (!(length > 0.0f))
        return;
    outward = open_cfw_nemavg_scale(outward, half_width / length);
    shifted0 = open_cfw_nemavg_add(edge0, outward);
    shifted1 = open_cfw_nemavg_add(edge1, outward);

    if (open_cfw_nemavg_aa_disabled(context) != 0U) {
        previous_aa = OPEN_CFW_NEMAVG_ENABLE_AA(0U, 0U, 0U, 0U);
    } else if (is_end_cap != 0U) {
        previous_aa = OPEN_CFW_NEMAVG_ENABLE_AA(1U, 1U, 1U, 0U);
    } else {
        previous_aa = OPEN_CFW_NEMAVG_ENABLE_AA(0U, 1U, 1U, 1U);
    }
    OPEN_CFW_NEMAVG_RASTER_QUAD(
        edge0.x, edge0.y, edge1.x, edge1.y,
        shifted1.x, shifted1.y, shifted0.x, shifted0.y);
    (void)OPEN_CFW_NEMAVG_RESTORE_AA(previous_aa);
}

OPEN_CFW_NEMAVG_ALWAYS_INLINE uint32_t
open_cfw_nemavg_draw_endpoint(uint8_t is_end_cap)
{
    volatile uint8_t *context = OPEN_CFW_NEMAVG_CONTEXT_POINTER();
    uint8_t style;

    if (context == NULL ||
        open_cfw_nemavg_load_u32(
            context, OPEN_CFW_NEMAVG_CONTEXT_ACTIVE_OFFSET) == 0U)
        return OPEN_CFW_NEMAVG_OK;
    style = context[is_end_cap != 0U
        ? OPEN_CFW_NEMAVG_END_STYLE_OFFSET
        : OPEN_CFW_NEMAVG_START_STYLE_OFFSET];
    if (style == OPEN_CFW_NEMAVG_STYLE_BUTT)
        return OPEN_CFW_NEMAVG_OK;
    if (style == OPEN_CFW_NEMAVG_STYLE_ROUND) {
        open_cfw_nemavg_draw_round(context, is_end_cap);
        return OPEN_CFW_NEMAVG_OK;
    }
    if (style == OPEN_CFW_NEMAVG_STYLE_SQUARE) {
        open_cfw_nemavg_draw_square(context, is_end_cap);
        return OPEN_CFW_NEMAVG_OK;
    }
    return OPEN_CFW_NEMAVG_INVALID_STYLE;
}

#if defined(OPEN_CFW_NEMAVG_STROKE_CAPS_START_ONLY) ||                      \
    defined(OPEN_CFW_NEMAVG_STROKE_CAPS_BUILD_ALL)
uint32_t open_cfw_nemavg_draw_start_cap_endpoint(void)
{
    return open_cfw_nemavg_draw_endpoint(0U);
}
#endif

#if defined(OPEN_CFW_NEMAVG_STROKE_CAPS_END_ONLY) ||                        \
    defined(OPEN_CFW_NEMAVG_STROKE_CAPS_BUILD_ALL)
uint32_t open_cfw_nemavg_draw_end_cap_endpoint(void)
{
    return open_cfw_nemavg_draw_endpoint(1U);
}
#endif

#ifndef OPEN_CFW_NEMAVG_SET_ERROR
void open_cfw_retained_nemavg_set_error(uint32_t error);
#define OPEN_CFW_NEMAVG_SET_ERROR open_cfw_retained_nemavg_set_error
#endif

#if defined(OPEN_CFW_NEMAVG_STROKE_CAPS_DISPATCH_ONLY) ||                   \
    defined(OPEN_CFW_NEMAVG_STROKE_CAPS_BUILD_ALL)
uint32_t open_cfw_nemavg_draw_start_cap_endpoint(void);
uint32_t open_cfw_nemavg_draw_end_cap_endpoint(void);

uint32_t open_cfw_nemavg_draw_caps_dispatch(void)
{
    volatile uint8_t *context;
    uint32_t result = open_cfw_nemavg_draw_start_cap_endpoint();

    if (result == OPEN_CFW_NEMAVG_OK)
        result = open_cfw_nemavg_draw_end_cap_endpoint();
    if (result == OPEN_CFW_NEMAVG_OK)
        return result;
    context = OPEN_CFW_NEMAVG_CONTEXT_POINTER();
    if (context != NULL) {
        *(volatile uint32_t *)(volatile void *)(context + UINT32_C(0x114)) = 0U;
        *(volatile uint32_t *)(volatile void *)(context + UINT32_C(0x118)) = 0U;
    }
    OPEN_CFW_NEMAVG_SET_ERROR(result);
    return result;
}
#endif
