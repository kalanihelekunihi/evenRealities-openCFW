/* SPDX-License-Identifier: MIT */
#include "runtime_nemavg_stroke_caps_candidate.h"

#define OPEN_CFW_NEMAVG_CAP_MAX_SEGMENTS 94U
#define OPEN_CFW_NEMAVG_PI 3.14159265358979323846f

static float squared_length(struct open_cfw_nemavg_point value)
{
    return value.x * value.x + value.y * value.y;
}

static float dot(struct open_cfw_nemavg_point left,
                 struct open_cfw_nemavg_point right)
{
    return left.x * right.x + left.y * right.y;
}

static struct open_cfw_nemavg_point subtract(
    struct open_cfw_nemavg_point left,
    struct open_cfw_nemavg_point right)
{
    struct open_cfw_nemavg_point result;
    result.x = left.x - right.x;
    result.y = left.y - right.y;
    return result;
}

static struct open_cfw_nemavg_point add(
    struct open_cfw_nemavg_point left,
    struct open_cfw_nemavg_point right)
{
    struct open_cfw_nemavg_point result;
    result.x = left.x + right.x;
    result.y = left.y + right.y;
    return result;
}

static struct open_cfw_nemavg_point scale(
    struct open_cfw_nemavg_point value, float factor)
{
    struct open_cfw_nemavg_point result;
    result.x = value.x * factor;
    result.y = value.y * factor;
    return result;
}

static struct open_cfw_nemavg_point rotate(
    struct open_cfw_nemavg_point value, float sine, float cosine)
{
    struct open_cfw_nemavg_point result;
    result.x = cosine * value.x - sine * value.y;
    result.y = sine * value.x + cosine * value.y;
    return result;
}

static uint32_t finish(const struct open_cfw_nemavg_stroke_caps *caps,
                       uint32_t token, int provider_result)
{
    if (caps->ports->end_command_state != NULL)
        caps->ports->end_command_state(caps->port_context, token);
    return provider_result == 0 ? OPEN_CFW_NEMAVG_CAP_OK
                                : OPEN_CFW_NEMAVG_CAP_PROVIDER_FAILED;
}

static uint32_t draw_square(
    const struct open_cfw_nemavg_stroke_caps *caps,
    const struct open_cfw_nemavg_cap_endpoint *endpoint,
    uint8_t is_end_cap)
{
    struct open_cfw_nemavg_point outward;
    struct open_cfw_nemavg_point shift;
    struct open_cfw_nemavg_point quad[4];
    float length_squared;
    float length;
    uint32_t token = 0U;

    if (caps->ports->emit_quad == NULL ||
        caps->ports->square_root == NULL)
        return OPEN_CFW_NEMAVG_CAP_INVALID_ARGUMENT;
    outward = subtract(endpoint->center, endpoint->adjacent_center);
    length_squared = squared_length(outward);
    if (!(length_squared > 0.0f) || !(caps->stroke_width > 0.0f))
        return OPEN_CFW_NEMAVG_CAP_INVALID_ARGUMENT;

    length = caps->ports->square_root(caps->port_context, length_squared);
    if (!(length > 0.0f))
        return OPEN_CFW_NEMAVG_CAP_PROVIDER_FAILED;
    shift = scale(outward, 0.5f * caps->stroke_width / length);
    quad[0] = endpoint->left;
    quad[1] = endpoint->right;
    quad[2] = add(endpoint->right, shift);
    quad[3] = add(endpoint->left, shift);
    if (caps->ports->begin_command_state != NULL)
        token = caps->ports->begin_command_state(
            caps->port_context, is_end_cap, caps->antialias);
    return finish(caps, token,
                  caps->ports->emit_quad(caps->port_context, quad));
}

static uint32_t draw_round(
    const struct open_cfw_nemavg_stroke_caps *caps,
    const struct open_cfw_nemavg_cap_endpoint *endpoint,
    uint8_t is_end_cap)
{
    struct open_cfw_nemavg_point vertices[OPEN_CFW_NEMAVG_CAP_MAX_SEGMENTS + 2U];
    struct open_cfw_nemavg_point radial;
    struct open_cfw_nemavg_point outward;
    struct open_cfw_nemavg_point probe;
    float sine;
    float cosine;
    unsigned int segments;
    unsigned int index;
    uint32_t token = 0U;

    if (caps->ports->arc_segment_count == NULL ||
        caps->ports->sincos_radians == NULL ||
        caps->ports->emit_triangle_fan == NULL ||
        !(caps->stroke_width > 0.0f))
        return OPEN_CFW_NEMAVG_CAP_INVALID_ARGUMENT;
    segments = caps->ports->arc_segment_count(
        caps->port_context, caps->stroke_width * 0.5f);
    if (segments < 2U)
        segments = 2U;
    if (segments > OPEN_CFW_NEMAVG_CAP_MAX_SEGMENTS)
        segments = OPEN_CFW_NEMAVG_CAP_MAX_SEGMENTS;
    if (caps->ports->sincos_radians(
            caps->port_context, OPEN_CFW_NEMAVG_PI / (float)segments,
            &sine, &cosine) != 0)
        return OPEN_CFW_NEMAVG_CAP_PROVIDER_FAILED;

    radial = subtract(endpoint->left, endpoint->center);
    outward = subtract(endpoint->center, endpoint->adjacent_center);
    probe = radial;
    for (index = 0U; index < segments / 2U; ++index)
        probe = rotate(probe, sine, cosine);
    if (dot(probe, outward) < 0.0f)
        sine = -sine;

    vertices[0] = endpoint->center;
    vertices[1] = endpoint->left;
    for (index = 1U; index < segments; ++index) {
        radial = rotate(radial, sine, cosine);
        vertices[index + 1U] = add(endpoint->center, radial);
    }
    vertices[segments + 1U] = endpoint->right;
    if (caps->ports->begin_command_state != NULL)
        token = caps->ports->begin_command_state(
            caps->port_context, is_end_cap, caps->antialias);
    return finish(caps, token, caps->ports->emit_triangle_fan(
        caps->port_context, vertices, (size_t)segments + 2U));
}

static uint32_t draw_one(const struct open_cfw_nemavg_stroke_caps *caps,
                         uint8_t is_end_cap)
{
    const struct open_cfw_nemavg_cap_endpoint *endpoint;
    uint8_t style;
    if (caps == NULL || caps->ports == NULL)
        return OPEN_CFW_NEMAVG_CAP_INVALID_ARGUMENT;
    endpoint = is_end_cap != 0U ? &caps->end : &caps->start;
    style = is_end_cap != 0U ? caps->end_style : caps->start_style;
    if (style == OPEN_CFW_NEMAVG_CAP_BUTT)
        return OPEN_CFW_NEMAVG_CAP_OK;
    if (style == OPEN_CFW_NEMAVG_CAP_ROUND)
        return draw_round(caps, endpoint, is_end_cap);
    if (style == OPEN_CFW_NEMAVG_CAP_SQUARE)
        return draw_square(caps, endpoint, is_end_cap);
    return OPEN_CFW_NEMAVG_CAP_INVALID_STYLE;
}

uint32_t open_cfw_nemavg_draw_start_cap(
    const struct open_cfw_nemavg_stroke_caps *caps)
{
    return draw_one(caps, 0U);
}

uint32_t open_cfw_nemavg_draw_end_cap(
    const struct open_cfw_nemavg_stroke_caps *caps)
{
    return draw_one(caps, 1U);
}

uint32_t open_cfw_nemavg_draw_caps(
    const struct open_cfw_nemavg_stroke_caps *caps)
{
    uint32_t result = open_cfw_nemavg_draw_start_cap(caps);
    if (result != OPEN_CFW_NEMAVG_CAP_OK)
        return result;
    return open_cfw_nemavg_draw_end_cap(caps);
}
