/**
 * @file lv_draw_ambiq_line.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include <stdbool.h>
#include "lv_draw_ambiq.h"
#if LV_USE_DRAW_AMBIQ

#include "../../misc/lv_math.h"
#include "../../core/lv_refr.h"
#include "../../stdlib/lv_string.h"
#include "lv_draw_ambiq_private.h"

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/


/**********************
 *  STATIC VARIABLES
 **********************/

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void
nema_raster_line_aa(float x0, float y0, float x1, float y1, float w)
{
    float dX = x1-x0;
    float dY = y1-y0;
    float w_ = w;

    if (w_ < 1.f) {
        w_ = 1.f;
    }


    float dx, dy;

    // if line is vertical
    if ( nema_absf(dX) < 0.5f ) {
        dy = 0.f;
        dx = w_*0.5f;
    }
    else {
        float l_tan = dY/dX;

        // nema_atan is more suitable than nema_sqrt
        float angle = nema_atan(l_tan);
        dx =  nema_sin(angle)*w_*0.5f;
        dy = -nema_cos(angle)*w_*0.5f;
    }

    float qx0 = x0+dx;
    float qx1 = x1+dx;
    float qx2 = x1-dx;
    float qx3 = x0-dx;
    float qy0 = y0+dy;
    float qy1 = y1+dy;
    float qy2 = y1-dy;
    float qy3 = y0-dy;

    uint32_t prev_aa = nema_enable_aa(1,1,1,1);

    nema_raster_quad_fx(nema_f2fx(qx0), nema_f2fx(qy0),
                        nema_f2fx(qx1), nema_f2fx(qy1),
                        nema_f2fx(qx2), nema_f2fx(qy2),
                        nema_f2fx(qx3), nema_f2fx(qy3) );

    (void)nema_enable_aa_flags(prev_aa);
}


void lv_draw_ambiq_line(lv_draw_task_t * t, const lv_draw_line_dsc_t * dsc)
{
    if(dsc->width == 0) return;
    if(dsc->opa <= LV_OPA_MIN) return;

    if(dsc->p1.x == dsc->p2.x && dsc->p1.y == dsc->p2.y) return;

    lv_area_t clip_line;
    clip_line.x1 = (int32_t)LV_MIN(dsc->p1.x, dsc->p2.x) - dsc->width / 2;
    clip_line.x2 = (int32_t)LV_MAX(dsc->p1.x, dsc->p2.x) + dsc->width / 2;
    clip_line.y1 = (int32_t)LV_MIN(dsc->p1.y, dsc->p2.y) - dsc->width / 2;
    clip_line.y2 = (int32_t)LV_MAX(dsc->p1.y, dsc->p2.y) + dsc->width / 2;

    bool is_common;
    is_common = lv_area_intersect(&clip_line, &clip_line, &t->clip_area);
    if(!is_common) return;

    lv_draw_ambiq_unit_t * draw_ambiq_unit = (lv_draw_ambiq_unit_t *)t->draw_unit;
    lv_layer_t * layer = t->target_layer;
    uint32_t bg_color    = lv_ambiq_color_convert(dsc->color, dsc->opa);
    uint32_t blending_mode;

    if(layer->color_format == LV_COLOR_FORMAT_ARGB8888)
    {
        blending_mode = NEMA_BL_SRC_OVER|NEMA_BLOP_SRC_PREMULT;
    }
    else
    {
        blending_mode = NEMA_BL_SIMPLE;
    }

    float angle;
    float x0 = dsc->p1.x - layer->buf_area.x1;
    float y0 = dsc->p1.y - layer->buf_area.y1;
    float x1 = dsc->p2.x - layer->buf_area.x1;
    float y1 = dsc->p2.y - layer->buf_area.y1;
    float w = dsc->width;

    // if line is vertical
    if ( dsc->p2.x == dsc->p1.x ) {
        if(dsc->p2.y > dsc->p1.y)
        {
            angle = 90;
        }
        else
        {
            angle = -90;
        }
    }
    else {
        float dX = x1-x0;
        float dY = y1-y0;

        angle = nema_atan(dY/dX);
    }

    bool dashed = dsc->dash_gap && dsc->dash_width;
    if(dashed)
    {
        //Create dash in RGBA format
        nema_bind_tex(NEMA_TEX1, (uintptr_t)draw_ambiq_unit->small_texture_buffer->data,
                      draw_ambiq_unit->small_texture_buffer->header.w,
                      1,
                      NEMA_RGBA8888,
                      0, NEMA_FILTER_BL|NEMA_TEX_REPEAT);
        lv_ambiq_dashline_create(dsc->dash_width, dsc->dash_gap, bg_color, NEMA_TEX1);
        

        // set blend
        lv_ambiq_blend_mode_change(draw_ambiq_unit, blending_mode, NEMA_TEX0, NEMA_TEX1, NEMA_NOTEX, true);


        // transform
        nema_matrix3x3_t m;
        float rotate_angle = (dsc->p2.x >= dsc->p1.x) ? angle : 180 + angle ;
        float scale_x = (float)(dsc->dash_gap + dsc->dash_width) / (draw_ambiq_unit->small_texture_buffer->header.w);
        float scale_y = w;

        nema_mat3x3_load_identity(m);
        nema_mat3x3_scale(m, scale_x, scale_y);
        nema_mat3x3_translate(m, 0, -w*0.5f);
        nema_mat3x3_rotate(m, rotate_angle);
        nema_mat3x3_translate(m, x0, y0);


        nema_mat3x3_invert(m);

        nema_set_matrix_all(m);
    }
    else
    {
        lv_ambiq_set_blend_fill(draw_ambiq_unit, blending_mode);
        nema_set_raster_color(bg_color);
    }

    // Draw Line
    nema_raster_line_aa(x0, y0, x1, y1, w); 

    //Draw line end
    if(dsc->round_start && (dsc->width > 1)) {


        nema_raster_stroked_arc_aa(x0, y0, w*0.25f, w*0.5f, 90.f+angle, 270.f + angle);
    }
    
    if(dsc->round_end && (dsc->width > 1)) {


        nema_raster_stroked_arc_aa(x1, y1, w*0.25f, w*0.5f, -90.f+angle, 90.f + angle);
    }

}



#endif /*LV_USE_DRAW_AMBIQ*/
