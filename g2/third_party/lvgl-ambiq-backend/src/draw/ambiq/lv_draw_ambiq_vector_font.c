//*****************************************************************************
//
// Copyright (c) 2025, Ambiq Micro, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
// contributors may be used to endorse or promote products derived from this
// software without specific prior written permission.
//
// Third party software included in this distribution is subject to the
// additional license terms as defined in the /docs/licenses directory.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//*****************************************************************************

/**
 * @file lv_draw_ambiq_vector_font.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "../../core/lv_refr.h"

#if LV_USE_DRAW_AMBIQ && LV_USE_AMBIQ_VG

#include "lv_draw_ambiq_private.h"
#include "lv_draw_ambiq.h"
#include "../lv_draw_label_private.h"

#if LV_USE_FREETYPE
#include "../../libs/freetype/lv_freetype_private.h"
#endif

/*********************
 *      DEFINES
 *********************/
#if LV_USE_FREETYPE
#define FT_F26DOT6_SHIFT 6
#define FT_F26DOT6_TO_PATH_SCALE(x) (LV_FREETYPE_F26DOT6_TO_FLOAT(x) / (1 << FT_F26DOT6_SHIFT))
#endif
/**********************
 *      TYPEDEFS
 **********************/
static lv_array_t path_seg;
static lv_array_t path_data;
static NEMA_VG_PATH_HANDLE cur_path = NULL;

typedef struct {
    NEMA_VG_PATH_HANDLE glyph_path;
    NEMA_VG_PATH_HANDLE glyph_border;
} lv_ambiq_ft_glyph_t;

/**********************
 *  STATIC PROTOTYPES
 **********************/

static void lv_ambiq_ft_outline_push(const lv_freetype_outline_event_param_t * param);

static void lv_ambiq_ft_outline_alloc(lv_freetype_outline_event_param_t * param);

static void lv_ambiq_ft_outline_destroy(lv_ambiq_ft_glyph_t * outline);

static void lv_draw_ambiq_vector_font_ft(lv_draw_task_t * t, lv_draw_glyph_dsc_t * glyph_draw_dsc);

static void lv_draw_ambiq_vector_font_ft_cb(lv_event_t * e);

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void lv_draw_ambiq_vector_font_init(lv_draw_unit_t * draw_unit)
{
#if LV_USE_FREETYPE
    /*Set up the freetype outline event*/
    lv_freetype_outline_add_event(lv_draw_ambiq_vector_font_ft_cb, LV_EVENT_ALL, draw_unit);
#else
    LV_UNUSED(draw_unit);
#endif /* LV_USE_FREETYPE */
}

void lv_draw_ambiq_vector_font(lv_draw_task_t * t, lv_draw_glyph_dsc_t * glyph_draw_dsc)
{
#if LV_USE_FREETYPE
    if(lv_freetype_is_outline_font(glyph_draw_dsc->g->resolved_font)) {
        lv_draw_ambiq_vector_font_ft(t, glyph_draw_dsc);
    }
#endif
}

#if LV_USE_FREETYPE

static void lv_draw_ambiq_vector_font_ft(lv_draw_task_t * t, lv_draw_glyph_dsc_t * glyph_draw_dsc)
{

    lv_area_t blend_area;
    if(!lv_area_intersect(&blend_area, glyph_draw_dsc->letter_coords, &t->clip_area))
        return;

    lv_draw_ambiq_unit_t * unit = (lv_draw_ambiq_unit_t *)t->draw_unit;

    lv_ambiq_ft_glyph_t * outline = (lv_ambiq_ft_glyph_t *)glyph_draw_dsc->glyph_data;

    nema_vg_set_blend(NEMA_BL_SRC_OVER);

    /*Calculate Path Matrix*/
    nema_matrix3x3_t matrix;
    lv_point_t pos = {glyph_draw_dsc->letter_coords->x1, glyph_draw_dsc->letter_coords->y1};
    float scale = FT_F26DOT6_TO_PATH_SCALE(lv_freetype_outline_get_scale(glyph_draw_dsc->g->resolved_font));
    nema_mat3x3_load_identity(matrix);
    nema_mat3x3_scale(matrix, scale, -scale);
    nema_mat3x3_translate(matrix, pos.x - glyph_draw_dsc->g->ofs_x,
                          pos.y + glyph_draw_dsc->g->box_h + glyph_draw_dsc->g->ofs_y);

    // set fill rule
    nema_vg_set_fill_rule(NEMA_VG_FILL_EVEN_ODD);

    // set paint
    nema_vg_paint_set_type(unit->vg_paint, NEMA_VG_PAINT_COLOR);
    uint32_t glyph_color    = lv_ambiq_color_convert(glyph_draw_dsc->color, glyph_draw_dsc->opa);
    nema_vg_paint_set_paint_color(unit->vg_paint, glyph_color);

    // set matrix
    nema_vg_path_set_matrix(outline->glyph_path, matrix);

    //draw path
    nema_vg_draw_path(outline->glyph_path, unit->vg_paint);

    // draw boarder
    if(glyph_draw_dsc->outline_stroke_width > 0)
    {
        nema_vg_set_fill_rule(NEMA_VG_STROKE);

        float stroke_width_in_object_space = ((float)glyph_draw_dsc->outline_stroke_width)/scale;
        nema_vg_stroke_set_width(stroke_width_in_object_space);

        uint32_t border_color = lv_ambiq_color_convert(glyph_draw_dsc->outline_stroke_color, glyph_draw_dsc->outline_stroke_opa);
        nema_vg_paint_set_paint_color(unit->vg_paint, border_color);

        nema_vg_path_set_matrix(outline->glyph_border, matrix);
        nema_vg_draw_path(outline->glyph_border, unit->vg_paint);
    }

    return;
}

static void lv_draw_ambiq_vector_font_ft_cb(lv_event_t * e)
{
    LV_PROFILER_DRAW_BEGIN;
    lv_event_code_t code = lv_event_get_code(e);
    lv_freetype_outline_event_param_t * param = lv_event_get_param(e);

    switch(code) {
        case LV_EVENT_CREATE:
            // Create the lv_ambiq_ft_glyph_t object and set the value
            lv_ambiq_ft_outline_alloc(param);
            break;
        case LV_EVENT_DELETE:
            lv_ambiq_ft_outline_destroy(param->outline);
            break;
        case LV_EVENT_INSERT:
            lv_ambiq_ft_outline_push(param);
            break;
        default:
            LV_LOG_WARN("unknown event code: %d", code);
            break;
    }
    LV_PROFILER_DRAW_END;
}

static inline void lv_ambiq_ft_data_array_push(int32_t x, int32_t y)
{
    float x_f = (float)x;
    float y_f = (float)y;
    lv_result_t res;

    res = lv_array_push_back(&path_data, &x_f);
    LV_ASSERT(res == LV_RESULT_OK);

    res = lv_array_push_back(&path_data, &y_f);
    LV_ASSERT(res == LV_RESULT_OK);
}

static void lv_ambiq_ft_outline_push(const lv_freetype_outline_event_param_t * param)
{
    LV_PROFILER_DRAW_BEGIN;
    lv_ambiq_ft_glyph_t * outline = param->outline;
    LV_ASSERT_NULL(outline);

    lv_result_t res;
    uint8_t seg = NEMA_VG_PRIM_CLOSE;

    lv_freetype_outline_type_t type = param->type;
    switch(type) {
        case LV_FREETYPE_OUTLINE_END:
            seg = NEMA_VG_PRIM_CLOSE;
            break;
        case LV_FREETYPE_OUTLINE_MOVE_TO:
            seg = NEMA_VG_PRIM_MOVE;
            break;
        case LV_FREETYPE_OUTLINE_LINE_TO:
            seg = NEMA_VG_PRIM_LINE;
            break;
        case LV_FREETYPE_OUTLINE_CUBIC_TO:
            seg = NEMA_VG_PRIM_BEZIER_CUBIC;
            break;
        case LV_FREETYPE_OUTLINE_CONIC_TO:
            seg = NEMA_VG_PRIM_BEZIER_QUAD;
            break;
        case LV_FREETYPE_OUTLINE_BORDER_START:
            seg = NEMA_VG_PRIM_CLOSE;
            break;
        default:
            LV_LOG_ERROR("unknown point type: %d", type);
            break;
    }

    res = lv_array_push_back(&path_seg, &seg);
    LV_ASSERT(res == LV_RESULT_OK);

    if((seg == NEMA_VG_PRIM_BEZIER_CUBIC) || (seg == NEMA_VG_PRIM_BEZIER_QUAD))
    {
        lv_ambiq_ft_data_array_push(param->control1.x, param->control1.y);
    }

    if(seg == NEMA_VG_PRIM_BEZIER_CUBIC)
    {
        lv_ambiq_ft_data_array_push(param->control2.x, param->control2.y);
    }

    if(seg != NEMA_VG_PRIM_CLOSE)
    {
        lv_ambiq_ft_data_array_push(param->to.x, param->to.y);
    }

    if((type == LV_FREETYPE_OUTLINE_END) || (type == LV_FREETYPE_OUTLINE_BORDER_START))
    {
        nema_vg_path_set_shape(cur_path,
                                lv_array_size(&path_seg), lv_array_front(&path_seg),
                                lv_array_size(&path_data), lv_array_front(&path_data));
    }

    if(type == LV_FREETYPE_OUTLINE_BORDER_START)
    {
        outline->glyph_border = nema_vg_path_create();

        cur_path = outline->glyph_border;
    }

    LV_PROFILER_DRAW_END;
}

static void lv_ambiq_ft_outline_alloc(lv_freetype_outline_event_param_t * param)
{
    LV_PROFILER_DRAW_BEGIN;

    if(param->outline == NULL)
    {
        lv_ambiq_ft_glyph_t *outline = lv_malloc(sizeof(lv_ambiq_ft_glyph_t));
        LV_ASSERT_MALLOC(outline);

        outline->glyph_path = nema_vg_path_create();
        outline->glyph_border = NULL;

        param->outline = outline;

        cur_path = outline->glyph_path;
    }

    lv_array_deinit(&path_data);
    lv_array_deinit(&path_seg);

    uint32_t data_size = param->sizes.data_size;
    uint32_t seg_size = param->sizes.segments_size + 1;
    void* data = lv_malloc(data_size * sizeof(float));
    LV_ASSERT_MALLOC(data);
    void* seg = lv_malloc(seg_size * sizeof(uint8_t));
    LV_ASSERT_MALLOC(seg);

    lv_array_init_from_buf(&path_data, data, data_size, sizeof(float));
    lv_array_init_from_buf(&path_seg, seg, seg_size, sizeof(uint8_t));

    LV_PROFILER_DRAW_END;

    return;
}

static void lv_ambiq_ft_outline_destroy(lv_ambiq_ft_glyph_t * outline)
{
    LV_PROFILER_DRAW_BEGIN;
    LV_ASSERT_NULL(outline);

    uint32_t data_size;
    float* data;
    uint32_t seg_size;
    uint8_t* seg;

    if(outline->glyph_path != NULL)
    {
        lv_ambiq_get_path_vbuf(outline->glyph_path, &seg_size, &data_size, &seg, &data);
        lv_free(data);
        lv_free(seg);
    }

    if(outline->glyph_border != NULL)
    {
        lv_ambiq_get_path_vbuf(outline->glyph_border, &seg_size, &data_size, &seg, &data);
        lv_free(data);
        lv_free(seg);
    }

    if(outline->glyph_path != NULL)
    {
        nema_vg_path_destroy(outline->glyph_path);
        outline->glyph_path = NULL;
    }

    if(outline->glyph_border != NULL)
    {
        nema_vg_path_destroy(outline->glyph_border);
        outline->glyph_border = NULL;
    }

    lv_free(outline);
    LV_PROFILER_DRAW_END;
}
#endif /* LV_USE_FREETYPE */

#endif  /*LV_USE_DRAW_AMBIQ && LV_USE_AMBIQ_VG*/

