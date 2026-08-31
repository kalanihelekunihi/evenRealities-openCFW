/**
 * @file lv_draw_ambiq_triangle.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "lv_draw_ambiq.h"
#if LV_USE_DRAW_AMBIQ
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

void lv_draw_ambiq_triangle(lv_draw_task_t * t, const lv_draw_triangle_dsc_t * dsc)
{

    lv_area_t tri_area;
    tri_area.x1 = (int32_t)LV_MIN3(dsc->p[0].x, dsc->p[1].x, dsc->p[2].x);
    tri_area.y1 = (int32_t)LV_MIN3(dsc->p[0].y, dsc->p[1].y, dsc->p[2].y);
    tri_area.x2 = (int32_t)LV_MAX3(dsc->p[0].x, dsc->p[1].x, dsc->p[2].x);
    tri_area.y2 = (int32_t)LV_MAX3(dsc->p[0].y, dsc->p[1].y, dsc->p[2].y);

    bool is_common;
    lv_area_t draw_area;
    is_common = lv_area_intersect(&draw_area, &tri_area, &t->clip_area);
    if(!is_common) return;

    if(dsc->opa <= LV_OPA_MIN) return;

    lv_draw_ambiq_unit_t * draw_ambiq_unit = (lv_draw_ambiq_unit_t *)t->draw_unit;
    lv_layer_t * layer = t->target_layer;
    lv_grad_dir_t grad_dir = dsc->grad.dir;
    uint32_t bg_color    = lv_ambiq_color_convert(dsc->color, dsc->opa);

    float p0_x = (float)(dsc->p[0].x - layer->buf_area.x1);
    float p0_y = (float)(dsc->p[0].y - layer->buf_area.y1);
    float p1_x = (float)(dsc->p[1].x - layer->buf_area.x1);
    float p1_y = (float)(dsc->p[1].y - layer->buf_area.y1);
    float p2_x = (float)(dsc->p[2].x - layer->buf_area.x1);
    float p2_y = (float)(dsc->p[2].y - layer->buf_area.y1);

    // handle AA
    //Previous AA setting.
    uint32_t prev_aa = 0xFFFFFFFF;

    //Set antialias
    prev_aa = nema_enable_aa(true, true, true, false);

    uint32_t blending_mode;

    if(layer->color_format == LV_COLOR_FORMAT_ARGB8888)
    {
        blending_mode = NEMA_BL_SRC_OVER|NEMA_BLOP_SRC_PREMULT;
    }
    else
    {
        blending_mode = NEMA_BL_SIMPLE;
    }

    if((grad_dir == LV_GRAD_DIR_NONE)) {
        lv_ambiq_set_blend_fill(draw_ambiq_unit, blending_mode);
        nema_set_raster_color(bg_color);
        nema_raster_triangle_f(p0_x, p0_y, p1_x, p1_y, p2_x, p2_y);
        return;
    }

    int stops_count = dsc->grad.stops_count;

    if(stops_count > LV_GRADIENT_MAX_STOPS)
    {
        LV_LOG_WARN("stops_count is bigger than LV_GRADIENT_MAX_STOPS, use LV_GRADIENT_MAX_STOPS.\n");
        stops_count = LV_GRADIENT_MAX_STOPS;
    }



    float stops[LV_GRADIENT_MAX_STOPS];
    color_var_t colors[LV_GRADIENT_MAX_STOPS];

    for(uint32_t i=0; i<stops_count; i++)
    {
        stops[i] = (float)dsc->grad.stops[i].frac / 255.f;
        colors[i].r = (float)dsc->grad.stops[i].color.red;
        colors[i].g = (float)dsc->grad.stops[i].color.green;
        colors[i].b = (float)dsc->grad.stops[i].color.blue;   
        colors[i].a = (float)dsc->grad.stops[i].opa * (float)dsc->opa / 255.f;               
    }

    nema_bind_tex(NEMA_TEX1, (uintptr_t)draw_ambiq_unit->small_texture_buffer->data,
                  draw_ambiq_unit->small_texture_buffer->header.w,
                  1,
                  NEMA_RGBA8888,
                  0, NEMA_FILTER_BL);
    lv_ambiq_gradient_create(stops_count, stops, colors, NEMA_TEX1);

    lv_ambiq_blend_mode_change(draw_ambiq_unit, blending_mode, NEMA_TEX0, NEMA_TEX1, NEMA_NOTEX, true);

    int32_t start_x = tri_area.x1 - layer->buf_area.x1;
    int32_t start_y = tri_area.y1 - layer->buf_area.y1;
    uint32_t width = lv_area_get_width(&tri_area);
    uint32_t hight = lv_area_get_height(&tri_area);
    uint32_t gradient_texture_width = draw_ambiq_unit->small_texture_buffer->header.w;

    nema_matrix3x3_t m;
    float rotate_angle = (grad_dir == LV_GRAD_DIR_HOR) ? 0.f : 90.f;
    float scale_x = (grad_dir == LV_GRAD_DIR_HOR) ? (float)width/gradient_texture_width : (float)width;
    float scale_y = (grad_dir == LV_GRAD_DIR_HOR) ? (float)hight : (float)hight/gradient_texture_width;


    nema_mat3x3_load_identity(m);
    nema_mat3x3_rotate(m, rotate_angle);
    nema_mat3x3_scale(m, scale_x, scale_y);
    nema_mat3x3_translate(m, start_x, start_y);


    nema_mat3x3_invert(m);

    nema_set_matrix_all(m);

    nema_raster_triangle_f(p0_x, p0_y, p1_x, p1_y, p2_x, p2_y);

    nema_enable_aa_flags(prev_aa);

    return;
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

#endif /*LV_USE_DRAW_AMBIQ*/
