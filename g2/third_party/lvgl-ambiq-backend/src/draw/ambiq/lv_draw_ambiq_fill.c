/**
 * @file lv_draw_ambiq_fill.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "lv_draw_ambiq.h"
#if LV_USE_DRAW_AMBIQ
#include "lv_draw_ambiq_private.h"
#include "../../core/lv_refr.h"
#include "../../misc/lv_assert.h"

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

void lv_draw_ambiq_fill(lv_draw_task_t * t, const lv_draw_fill_dsc_t * dsc, const lv_area_t * coords)
{
    if(dsc->opa <= LV_OPA_MIN) return;

    lv_draw_ambiq_unit_t * draw_ambiq_unit = (lv_draw_ambiq_unit_t *)t->draw_unit;
    lv_layer_t * layer = t->target_layer;
    lv_grad_dir_t grad_dir = dsc->grad.dir;
    uint32_t bg_color    = lv_ambiq_color_convert(dsc->color, dsc->opa);

    lv_area_t bg_coords;
    lv_area_copy(&bg_coords, coords);
    lv_area_move(&bg_coords, -layer->buf_area.x1, -layer->buf_area.y1);

    /*Get the real radius. Can't be larger than the half of the shortest side */
    int32_t coords_w = lv_area_get_width(&bg_coords);
    int32_t coords_h = lv_area_get_height(&bg_coords);
    int32_t short_side = LV_MIN(coords_w, coords_h);
    int32_t rout = LV_MIN(dsc->radius, short_side >> 1);

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
        if(rout == 0)
        {
            nema_raster_rect(bg_coords.x1, bg_coords.y1, coords_w, coords_h);
        }
        else
        {
            nema_raster_rounded_rect(bg_coords.x1, bg_coords.y1, coords_w, coords_h, rout);
        }
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

    uint32_t small_texture_size_pixel = draw_ambiq_unit->small_texture_buffer->header.w;
    nema_bind_tex(NEMA_TEX1, (uintptr_t)draw_ambiq_unit->small_texture_buffer->data,
                  draw_ambiq_unit->small_texture_buffer->header.w,
                  1,
                  NEMA_RGBA8888,
                  0, NEMA_FILTER_BL);
    lv_ambiq_gradient_create(stops_count, stops, colors, NEMA_TEX1);

    lv_ambiq_blend_mode_change(draw_ambiq_unit, blending_mode, NEMA_TEX0, NEMA_TEX1, NEMA_NOTEX, true);

    nema_matrix3x3_t m;
    float rotate_angle = (grad_dir == LV_GRAD_DIR_HOR) ? 0.f : 90.f;
    float scale_x = (grad_dir == LV_GRAD_DIR_HOR) ? (float)coords_w/small_texture_size_pixel : (float)coords_w;
    float scale_y = (grad_dir == LV_GRAD_DIR_HOR) ? (float)coords_h : (float)coords_h/small_texture_size_pixel;


    nema_mat3x3_load_identity(m);
    nema_mat3x3_rotate(m, rotate_angle);
    nema_mat3x3_scale(m, scale_x, scale_y);
    nema_mat3x3_translate(m, bg_coords.x1, bg_coords.y1);


    nema_mat3x3_invert(m);

    nema_set_matrix_all(m);

    if(rout == 0)
    {
        nema_raster_rect(bg_coords.x1, bg_coords.y1, coords_w, coords_h);
    }
    else
    {
        nema_raster_rounded_rect(bg_coords.x1, bg_coords.y1, coords_w, coords_h, rout);
    }

    return;
}

#endif /*LV_USE_DRAW_AMBIQ*/
