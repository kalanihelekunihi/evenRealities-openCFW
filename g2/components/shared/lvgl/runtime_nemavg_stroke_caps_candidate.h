/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_NEMAVG_STROKE_CAPS_CANDIDATE_H
#define OPEN_CFW_RUNTIME_NEMAVG_STROKE_CAPS_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

enum open_cfw_nemavg_cap_style {
    OPEN_CFW_NEMAVG_CAP_BUTT = 0,
    OPEN_CFW_NEMAVG_CAP_ROUND = 1,
    OPEN_CFW_NEMAVG_CAP_SQUARE = 2,
};

enum open_cfw_nemavg_cap_status {
    OPEN_CFW_NEMAVG_CAP_OK = 0,
    OPEN_CFW_NEMAVG_CAP_PROVIDER_FAILED = 0x00400000U,
    OPEN_CFW_NEMAVG_CAP_INVALID_STYLE = 0x00800000U,
    OPEN_CFW_NEMAVG_CAP_INVALID_ARGUMENT = 0x01000000U,
};

struct open_cfw_nemavg_point {
    float x;
    float y;
};

/*
 * `adjacent_center` is the next point into the stroked path. Therefore the
 * cap's outward tangent is `center - adjacent_center` for both endpoints.
 * `left` and `right` are the already-expanded stroke-edge vertices.
 */
struct open_cfw_nemavg_cap_endpoint {
    struct open_cfw_nemavg_point center;
    struct open_cfw_nemavg_point adjacent_center;
    struct open_cfw_nemavg_point left;
    struct open_cfw_nemavg_point right;
};

struct open_cfw_nemavg_cap_ports {
    unsigned int (*arc_segment_count)(void *context, float radius);
    float (*square_root)(void *context, float value);
    int (*sincos_radians)(void *context, float angle,
                          float *sine, float *cosine);
    int (*emit_triangle_fan)(void *context,
                             const struct open_cfw_nemavg_point *vertices,
                             size_t count);
    int (*emit_quad)(void *context,
                     const struct open_cfw_nemavg_point vertices[4]);
    uint32_t (*begin_command_state)(void *context, uint8_t is_end_cap,
                                    uint8_t antialias);
    void (*end_command_state)(void *context, uint32_t token);
};

struct open_cfw_nemavg_stroke_caps {
    struct open_cfw_nemavg_cap_endpoint start;
    struct open_cfw_nemavg_cap_endpoint end;
    const struct open_cfw_nemavg_cap_ports *ports;
    void *port_context;
    float stroke_width;
    uint8_t start_style;
    uint8_t end_style;
    uint8_t antialias;
};

uint32_t open_cfw_nemavg_draw_start_cap(
    const struct open_cfw_nemavg_stroke_caps *caps);
uint32_t open_cfw_nemavg_draw_end_cap(
    const struct open_cfw_nemavg_stroke_caps *caps);
uint32_t open_cfw_nemavg_draw_caps(
    const struct open_cfw_nemavg_stroke_caps *caps);

#endif
