/**
 * @file lv_draw_ambiq_arc.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "lv_draw_ambiq.h"
#include "../lv_image_decoder_private.h"
#if LV_USE_DRAW_AMBIQ
#include "../../core/lv_refr.h"
#include "../../misc/lv_assert.h"
#include "lv_draw_ambiq_private.h"
#include <math.h>

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
void lv_draw_ambiq_arc(lv_draw_task_t * t, const lv_draw_arc_dsc_t * dsc, const lv_area_t * coords)
{
    if(dsc->opa <= LV_OPA_MIN) return;
    if(dsc->width == 0) return;
    if(dsc->start_angle == dsc->end_angle) return;

    int32_t width = dsc->width;
    if(width > dsc->radius) width = dsc->radius;

    lv_area_t area_out = *coords;
    lv_area_t clipped_area;
    if(!lv_area_intersect(&clipped_area, &area_out, &t->clip_area)) return;

    float start_angle = dsc->start_angle;
    float end_angle = dsc->end_angle;

    // make start_angle in [0, 360]
    start_angle = fmod(start_angle, 360.f);
    if(start_angle < 0)
    {
        start_angle += 360.f;
    }

    // make end_angle in [start_angle, 720]
    end_angle = fmod(end_angle, 360.f);
    if(end_angle < 0)
    {
        end_angle += 360.f;
    }
    if(end_angle <= start_angle)
    {
        end_angle += 360.f;
    }

    lv_layer_t * layer = t->target_layer;
    uint32_t bg_color    = lv_ambiq_color_convert(dsc->color, dsc->opa);

    bool is_full_circle = false;
    if(end_angle - start_angle > 359.9f && end_angle - start_angle < 360.1f)
    {
        is_full_circle = true;
        nema_set_clip_temp(coords->x1 - layer->buf_area.x1 , coords->y1 - layer->buf_area.y1, lv_area_get_width(coords), lv_area_get_height(coords));
    }

    uint32_t blending_mode;

    if(layer->color_format == LV_COLOR_FORMAT_ARGB8888)
    {
        blending_mode = NEMA_BL_SRC_OVER|NEMA_BLOP_SRC_PREMULT;
    }
    else
    {
        blending_mode = NEMA_BL_SIMPLE;
    }
    
    //Make the coords area relative to the display area
    int32_t center_x = dsc->center.x - layer->buf_area.x1;
    int32_t center_y = dsc->center.y - layer->buf_area.y1;

    lv_image_decoder_dsc_t decoder_dsc;
    lv_draw_buf_t *bg_img = NULL;
    if(dsc->img_src)
    {
        lv_result_t res = lv_draw_ambiq_decode_image(dsc->img_src, false, &decoder_dsc, false);
        if(res == LV_RESULT_OK) 
        {
            bg_img = decoder_dsc.decoded;
        }
        else
        {
            LV_LOG_ERROR("Failed to decode image");
        }
    }

    if(bg_img)
    {
        //blending_mode = bind_background_image(dsc, &decoder_dsc, blending_mode);
        uint32_t blend_op = lv_draw_ambiq_bind_image_texture(bg_img, bg_color, NEMA_TEX_BORDER);

        blending_mode |= blend_op;

        //Set Blending Mode
        lv_ambiq_set_blend_blit((lv_draw_ambiq_unit_t*)t->draw_unit, blending_mode);

        /*Center align*/
        lv_area_t area;
        area.x1 = center_x - bg_img->header.w / 2;
        area.y1 = center_y - bg_img->header.h / 2;
        area.x2 = area.x1 + bg_img->header.w - 1;
        area.y2 = area.y1 + bg_img->header.h - 1;

        nema_set_matrix_translate((float)area.x1, (float)area.y1);

    }
    else
    {
        //Set Blending Mode
        lv_ambiq_set_blend_fill((lv_draw_ambiq_unit_t*)t->draw_unit, blending_mode);;

        //Set color
        nema_set_raster_color(bg_color);
    }

    float width_f = width;
    float radius_f = dsc->radius;

    // In NemaSDK, the radius_out= radius+width*0.5, radius_in=radius-width*0.5;
    radius_f -= width_f * 0.5f;

    //Draw rounded ending
    if(dsc->rounded)
    {
        //Draw the arc
        nema_raster_stroked_arc_aa(center_x, center_y, radius_f, width_f, start_angle, end_angle);
        float width_cir = width_f * 0.5f;
        float start_cir_x = center_x + radius_f * nema_cos(start_angle);
        float start_cir_y = center_y + radius_f * nema_sin(start_angle);
        float end_cir_x = center_x + radius_f * nema_cos(end_angle);
        float end_cir_y = center_y + radius_f * nema_sin(end_angle);

        nema_raster_stroked_arc_aa(start_cir_x, start_cir_y, width_cir * 0.5f, width_cir, start_angle + 180.f, start_angle + 360.f);
        nema_raster_stroked_arc_aa(end_cir_x, end_cir_y, width_cir * 0.5f, width_cir, end_angle, end_angle + 180.f);
    }
    else
    {
        //Draw the arc
        nema_raster_stroked_arc_aa_mask(center_x, center_y, radius_f, width_f, start_angle, end_angle, 0x04000000U|0x01000000U);
    }

    if (bg_img)
    {
        nema_cmdlist_t * cl = nema_cl_get_bound();
        nema_cl_submit(cl);
        nema_cl_wait(cl);
        nema_cl_rewind(cl);

        lv_image_decoder_close(&decoder_dsc);
    }

    if(is_full_circle)
    {
        nema_set_clip_pop();
    }

    return;
    
}

#endif /*LV_USE_DRAW_AMBIQ*/
