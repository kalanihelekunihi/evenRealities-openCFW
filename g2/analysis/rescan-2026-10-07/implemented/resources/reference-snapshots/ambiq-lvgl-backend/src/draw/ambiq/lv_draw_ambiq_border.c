/**
 * @file lv_draw_sw_fill.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "lv_draw_ambiq.h"
#if LV_USE_DRAW_AMBIQ
#include "../../core/lv_refr.h"
#include "../../misc/lv_assert.h"
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

void lv_draw_ambiq_border(lv_draw_task_t * t, const lv_draw_border_dsc_t * dsc, const lv_area_t * coords)
{
    if(dsc->opa <= LV_OPA_MIN) return;
    if(dsc->width == 0) return;
    if(dsc->side == LV_BORDER_SIDE_NONE) return;

    lv_area_t draw_area;
    if(!lv_area_intersect(&draw_area, coords, &t->clip_area)) return;

    int32_t coords_w = lv_area_get_width(coords);
    int32_t coords_h = lv_area_get_height(coords);
    int32_t rout = dsc->radius;
    int32_t short_side = LV_MIN(coords_w, coords_h);
    if(rout > short_side >> 1) rout = short_side >> 1;

    
    int32_t border_width = LV_MIN(dsc->width, short_side >> 1);

    bool top_side = dsc->side & LV_BORDER_SIDE_TOP;
    bool bottom_side = dsc->side & LV_BORDER_SIDE_BOTTOM;
    bool left_side = dsc->side & LV_BORDER_SIDE_LEFT;
    bool right_side = dsc->side & LV_BORDER_SIDE_RIGHT;

    uint32_t blending_mode;

    if(t->target_layer->color_format == LV_COLOR_FORMAT_ARGB8888)
    {
        blending_mode = NEMA_BL_SRC_OVER|NEMA_BLOP_SRC_PREMULT;
    }
    else
    {
        blending_mode = NEMA_BL_SIMPLE;
    }

    uint32_t bg_color    = lv_ambiq_color_convert(dsc->color, dsc->opa);


    lv_ambiq_set_blend_fill((lv_draw_ambiq_unit_t*)t->draw_unit, blending_mode);
    nema_set_raster_color(bg_color);

    int draw_buf_offset_x = t->target_layer->buf_area.x1;
    int draw_buf_offset_y = t->target_layer->buf_area.y1;    

    int x1;
    int y1;
    int w;
    int h;


    if(left_side)
    {
        if(rout)
        {
            x1 = coords->x1;
            y1 = coords->y1 + rout;
            w = LV_MIN(border_width, rout);
            h = coords_h - 2 * rout;
        }
        else
        {
            x1 = coords->x1;
            y1 = coords->y1 + ((top_side) ? border_width : 0);
            w = border_width;
            h = coords_h - ((top_side) ? border_width : 0) - ((bottom_side) ? border_width : 0);   
        }

        nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);

        if(rout && (border_width > rout))
        {

            x1 = coords->x1 + rout;
            y1 = coords->y1 + ((top_side) ? border_width : 0);
            w = border_width - rout;
            h = coords_h - ((top_side) ? border_width : 0) - ((bottom_side) ? border_width : 0); 
 
            nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);
        }
    }

    if(right_side)
    {
        if(rout)
        {
            x1 = coords->x2 + 1 - LV_MIN(border_width, rout);
            y1 = coords->y1 + rout;
            w = LV_MIN(border_width, rout);
            h = coords_h - 2 * rout;
        }
        else
        {
            x1 = coords->x2 + 1 - border_width;
            y1 = coords->y1 + ((top_side) ? border_width : 0);
            w = border_width;
            h = coords_h - ((top_side) ? border_width : 0) - ((bottom_side) ? border_width : 0);   
        }

        nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);

        if(rout && (border_width > rout))
        {

            x1 = coords->x2 + 1 - border_width;
            y1 = coords->y1 + ((top_side) ? border_width : 0);
            w = border_width - rout;
            h = coords_h - ((top_side) ? border_width : 0) - ((bottom_side) ? border_width : 0);  
  
            nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);
        }
    }

    if(top_side)
    {
        if(rout)
        {
            x1 = coords->x1 + rout;
            y1 = coords->y1;
            w = coords_w - 2 * rout;
            h = LV_MIN(border_width, rout);
        }
        else
        {
            x1 = coords->x1;
            y1 = coords->y1;
            w = coords_w;
            h = border_width;   
        }
        nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);

        if(rout && (border_width > rout))
        {

            x1 = coords->x1 + ((left_side) ? rout : 0);
            y1 = coords->y1 + rout;
            w = coords_w - ((left_side) ? rout : 0) - ((right_side) ? rout : 0);
            h = border_width - rout; 
   
            nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);
        }
    }

    if(bottom_side)
    {
        if(rout)
        {
            x1 = coords->x1 + rout;
            y1 = coords->y2 + 1 - LV_MIN(border_width, rout);
            w = coords_w - 2 * rout;
            h = LV_MIN(border_width, rout);
        }
        else
        {
            x1 = coords->x1;
            y1 = coords->y2 + 1 - border_width;
            w = coords_w;
            h = border_width;   
        }

        nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);

        if(rout && (border_width > rout))
        {
            x1 = coords->x1 + ((left_side) ? rout : 0);
            y1 = coords->y2 + 1 - border_width;
            w = coords_w - ((left_side) ? rout : 0) - ((right_side) ? rout : 0);
            h = border_width - rout;   

            nema_raster_rect(x1 - draw_buf_offset_x, y1 - draw_buf_offset_y, w, h);
        }
    }

    lv_area_t clip;
    lv_area_t clip_intersect;
    float x_arc;
    float y_arc;
    float r_arc;
    float w_arc;

    if(rout != 0)
    {
        if(left_side || top_side)
        {
            clip.x1 = coords->x1;
            clip.y1 = coords->y1;
            clip.x2 = clip.x1 + rout - 1;
            clip.y2 = clip.y1 + rout - 1;

            // Left up corner
            if(left_side && !top_side)
            {
                clip.x2 = clip.x1 + LV_MIN(border_width, rout) - 1;
            }
            else if(!left_side && top_side)
            {
                clip.y2 = clip.y1 + LV_MIN(border_width, rout) - 1;
            }

            lv_area_intersect(&clip_intersect, &clip, &t->clip_area);

            lv_area_move(&clip_intersect, -draw_buf_offset_x, -draw_buf_offset_y);

            nema_set_clip_temp(clip_intersect.x1 , clip_intersect.y1 , 
                               clip_intersect.x2 - clip_intersect.x1 + 1, 
                               clip_intersect.y2 - clip_intersect.y1 + 1);

            x_arc = (float)(coords->x1 + rout - draw_buf_offset_x);
            y_arc = (float)(coords->y1 + rout - draw_buf_offset_y); 
            r_arc = (float)rout - LV_MIN(border_width, rout) * 0.5f;
            w_arc = (float)LV_MIN(border_width, rout);
            nema_raster_stroked_arc_aa(x_arc, y_arc, r_arc, w_arc, 180.f, 270.f);
            nema_set_clip_pop();
        }

        if(left_side || bottom_side)
        {
            clip.x1 = coords->x1;
            clip.y2 = coords->y2;

            clip.x2 = clip.x1 + rout - 1;
            clip.y1 = clip.y2 - rout + 1;

            // Left up corner
            if(left_side && !bottom_side)
            {
                clip.x2 = clip.x1 + LV_MIN(border_width, rout) - 1;
            }
            else if(!left_side && bottom_side)
            {
                clip.y1 = clip.y2 - LV_MIN(border_width, rout) + 1;
            }

            lv_area_intersect(&clip_intersect, &clip, &t->clip_area);

            lv_area_move(&clip_intersect, -draw_buf_offset_x, -draw_buf_offset_y);

            nema_set_clip_temp(clip_intersect.x1 , clip_intersect.y1 , 
                               clip_intersect.x2 - clip_intersect.x1 + 1, 
                               clip_intersect.y2 - clip_intersect.y1 + 1);

            x_arc = (float)(coords->x1 + rout - draw_buf_offset_x);
            y_arc = (float)(coords->y2 - rout + 1 - draw_buf_offset_y); 
            r_arc = (float)rout - LV_MIN(border_width, rout) * 0.5f;
            w_arc = (float)LV_MIN(border_width, rout);
            nema_raster_stroked_arc_aa(x_arc, y_arc, r_arc, w_arc, 90.f, 180.f);
            nema_set_clip_pop();
        }

        if(right_side || bottom_side)
        {
            clip.x2 = coords->x2;
            clip.y2 = coords->y2;

            clip.x1 = clip.x2 - rout + 1;
            clip.y1 = clip.y2 - rout + 1;

            // Left up corner
            if(right_side && !bottom_side)
            {
                clip.x1 = clip.x2 - LV_MIN(border_width, rout) + 1;
            }
            else if(!right_side && bottom_side)
            {
                clip.y1 = clip.y2 - LV_MIN(border_width, rout) + 1;
            }

            lv_area_intersect(&clip_intersect, &clip, &t->clip_area);

            lv_area_move(&clip_intersect, -draw_buf_offset_x, -draw_buf_offset_y);

            nema_set_clip_temp(clip_intersect.x1 , clip_intersect.y1 , 
                               clip_intersect.x2 - clip_intersect.x1 + 1, 
                               clip_intersect.y2 - clip_intersect.y1 + 1);

            x_arc = (float)(coords->x2 - rout + 1 - draw_buf_offset_x);
            y_arc = (float)(coords->y2 - rout + 1 - draw_buf_offset_y); 
            r_arc = (float)rout - LV_MIN(border_width, rout) * 0.5f;
            w_arc = (float)LV_MIN(border_width, rout);
            nema_raster_stroked_arc_aa(x_arc, y_arc, r_arc, w_arc, 0.f, 90.f);
            nema_set_clip_pop();
        }

        if(right_side || top_side)
        {
            clip.x2 = coords->x2;
            clip.y1 = coords->y1;

            clip.x1 = clip.x2 - rout + 1;
            clip.y2 = clip.y1 + rout - 1;

            // Left up corner
            if(right_side && !top_side)
            {
                clip.x1 = clip.x2 - LV_MIN(border_width, rout) + 1;
            }
            else if(!right_side && top_side)
            {
                clip.y2 = clip.y1 - LV_MIN(border_width, rout) + 1;
            }

            lv_area_intersect(&clip_intersect, &clip, &t->clip_area);

            lv_area_move(&clip_intersect, -draw_buf_offset_x, -draw_buf_offset_y);

            nema_set_clip_temp(clip_intersect.x1 , clip_intersect.y1 , 
                               clip_intersect.x2 - clip_intersect.x1 + 1, 
                               clip_intersect.y2 - clip_intersect.y1 + 1);

            x_arc = (float)(coords->x2 - rout + 1 - draw_buf_offset_x);
            y_arc = (float)(coords->y1 + rout - draw_buf_offset_y); 
            r_arc = (float)rout - LV_MIN(border_width, rout) * 0.5f;
            w_arc = (float)LV_MIN(border_width, rout);
            nema_raster_stroked_arc_aa(x_arc, y_arc, r_arc, w_arc, 270.f, 360.f);
            nema_set_clip_pop();
        }


    }
}

#endif /*LV_USE_DRAW_AMBIQ*/
