/**
 * @file lv_draw_ambiq_img.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "../../misc/lv_area_private.h"
#include "../lv_image_decoder_private.h"
#include "../lv_draw_image_private.h"
#include "../lv_draw_private.h"

#if LV_USE_DRAW_AMBIQ
#include "lv_draw_ambiq.h"
#include "lv_draw_ambiq_private.h"
#include "../../misc/lv_log.h"
#include "../../core/lv_refr_private.h"
#include "../../stdlib/lv_mem.h"
#include "../../misc/lv_math.h"
#include "../../misc/lv_color.h"
#include "../../stdlib/lv_string.h"
#include "../../core/lv_global.h"

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/
static void lv_draw_ambiq_image_core(lv_draw_task_t * t,
                                    const lv_draw_image_dsc_t * draw_dsc,
                                    const lv_area_t * coords);

/**********************
 *  STATIC VARIABLES
 **********************/
#define _draw_info LV_GLOBAL_DEFAULT()->draw_info

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void lv_draw_ambiq_layer(lv_draw_task_t * t, const lv_draw_image_dsc_t * draw_dsc, const lv_area_t * coords)
{
    lv_layer_t * layer_to_draw = (lv_layer_t *)draw_dsc->src;

    /*It can happen that nothing was draw on a layer and therefore its buffer is not allocated.
     *In this case just return. */
    if(layer_to_draw->draw_buf == NULL) return;

    lv_draw_image_dsc_t new_draw_dsc = *draw_dsc;
    new_draw_dsc.src = layer_to_draw->draw_buf;
    lv_draw_ambiq_image(t, &new_draw_dsc, coords);
}


void lv_draw_ambiq_image(lv_draw_task_t * t, const lv_draw_image_dsc_t * draw_dsc,
                      const lv_area_t * coords)
{
    // check if the image is supported
    if((draw_dsc->blend_mode == LV_BLEND_MODE_SUBTRACTIVE) || 
       (draw_dsc->blend_mode == LV_BLEND_MODE_MULTIPLY))
    {
        LV_LOG_WARN("GPU failed, not supported blend mode!");
        return;  
    }

    bool transformed = draw_dsc->rotation != 0 || draw_dsc->scale_x != LV_SCALE_NONE ||
                       draw_dsc->scale_y != LV_SCALE_NONE || draw_dsc->skew_y != 0 || draw_dsc->skew_x != 0 ? true : false;

    if(draw_dsc->tile)
    {
        if(transformed) 
        {
             LV_LOG_WARN("Set rotation/scale/skew effect to tile image is not supported! We will ignore these parameters.");
        }

        int32_t img_w = draw_dsc->header.w;
        int32_t img_h = draw_dsc->header.h;

        bool width_is_power_of_2 = (img_w > 0) && ((img_w & (img_w - 1)) == 0);
        bool hight_is_power_of_2 = (img_h > 0) && ((img_h & (img_h - 1)) == 0);

        if( !width_is_power_of_2 || !hight_is_power_of_2 )
        {
            LV_LOG_WARN("The hight and width of tile texture is not power of 2, draw it one by one! ");
        }

        if(draw_dsc->clip_radius != 0)
        {
            LV_LOG_WARN("Set clip_radius parameter to a tiled image is not supported! ignore it! ");
        }

        if(draw_dsc->bitmap_mask_src)
        {
            LV_LOG_WARN("Set mask to a tiled image is not supported! ignore it! ");
        }
    }



    // TODO: compare the draw_area min and max value with coordinate range limitation.
    lv_draw_ambiq_image_core(t, draw_dsc, coords);
    
}



/**********************
 *   STATIC FUNCTIONS
 **********************/

static void lv_draw_ambiq_image_core(lv_draw_task_t * t,
                                    const lv_draw_image_dsc_t * draw_dsc,
                                    const lv_area_t * coords)
{

    // handle tile image
    bool tile_draw_one_by_one = false;
    if(draw_dsc->tile)
    {
        int32_t img_w = draw_dsc->header.w;
        int32_t img_h = draw_dsc->header.h;

        bool width_is_power_of_2 = (img_w > 0) && ((img_w & (img_w - 1)) == 0);
        bool hight_is_power_of_2 = (img_h > 0) && ((img_h & (img_h - 1)) == 0);

        if( !width_is_power_of_2 || !hight_is_power_of_2 )
        {
            tile_draw_one_by_one = true;
        }
    }

    uint32_t tex_wrap_mode = (draw_dsc->tile && !tile_draw_one_by_one) ? NEMA_TEX_REPEAT : NEMA_TEX_BORDER;

    bool transformed = draw_dsc->rotation != 0 || draw_dsc->scale_x != LV_SCALE_NONE ||
                       draw_dsc->scale_y != LV_SCALE_NONE || draw_dsc->skew_y != 0 || draw_dsc->skew_x != 0 ? true : false;

    uint32_t recolor_rgba =lv_ambiq_color_convert(draw_dsc->recolor, draw_dsc->recolor_opa);

    // decode and bind the image texture
    lv_image_decoder_dsc_t decoder_dsc;
    lv_result_t res = lv_draw_ambiq_decode_image(draw_dsc->src, transformed, &decoder_dsc, false);
    if(res != LV_RESULT_OK) {
        LV_LOG_ERROR("Failed to open image");
        return;
    }

    // bind the image texture
    uint32_t color_rgba = lv_ambiq_color_convert(draw_dsc->recolor, draw_dsc->opa);
    uint32_t blend_op_tex = lv_draw_ambiq_bind_image_texture(decoder_dsc.decoded, color_rgba, tex_wrap_mode);

    // decode the mask texture
    lv_image_decoder_dsc_t mask_decoder_dsc;
    bool need_release_mask_decoder = false;
    const lv_draw_buf_t * mask_img = NULL;
    if(draw_dsc->bitmap_mask_src)
    {

        lv_result_t res = lv_draw_ambiq_decode_image(draw_dsc->bitmap_mask_src, false, &mask_decoder_dsc, true);
        if(res != LV_RESULT_OK) {
            LV_LOG_WARN("MASK image decode failed. Drawing the image without mask.");
        }
        else
        {
            if((mask_decoder_dsc.decoded->header.w == draw_dsc->header.w) && 
            (mask_decoder_dsc.decoded->header.h == draw_dsc->header.h))
            {
                mask_img = mask_decoder_dsc.decoded;
            }
            else
            {
                LV_LOG_WARN("GPU limitation, mask size should be same as the texture size or the framebuffer size! draw it without mask.");
            }

            need_release_mask_decoder = true;
        }

    } 

    // bind the mask iamge
    uint32_t blend_op_mask = 0;
    if(mask_img)
    {
        bool do_multiply = (draw_dsc->header.cf == LV_COLOR_FORMAT_RGB565A8) ? true : false;
        blend_op_mask = lv_draw_ambiq_bind_mask_texture(mask_img, true);
    }
 



    lv_layer_t * layer = t->target_layer;

    // handle blend mode

    uint32_t blending_mode;

    switch(draw_dsc->blend_mode)
    {
        case LV_BLEND_MODE_ADDITIVE:
            blending_mode = NEMA_BL_ADD;
            break;
        default:
            if(layer->color_format == LV_COLOR_FORMAT_ARGB8888)
            {
                blending_mode = NEMA_BL_SRC_OVER|NEMA_BLOP_SRC_PREMULT;
            }
            else
            {
                blending_mode = NEMA_BL_SIMPLE;
            }           
            break;
    }

    blending_mode |= blend_op_tex;
    blending_mode |= blend_op_mask;



    // handle recolor
    bool is_alpha_only = false;
    if((draw_dsc->header.cf == LV_COLOR_FORMAT_A1) ||
       (draw_dsc->header.cf == LV_COLOR_FORMAT_A2) ||
       (draw_dsc->header.cf == LV_COLOR_FORMAT_A4) ||
       (draw_dsc->header.cf == LV_COLOR_FORMAT_A8))
    {
        is_alpha_only = true;
    }

    if((draw_dsc->recolor_opa > LV_OPA_MIN) && (!is_alpha_only))
    {
        blending_mode |= NEMA_BLOP_RECOLOR;
        nema_set_recolor_color(recolor_rgba);
    }


    // handle AA
    //Previous AA setting.
    uint32_t prev_aa = 0xFFFFFFFF;

    //Set antialias
    if(draw_dsc->antialias)
    {
        prev_aa = nema_enable_aa(true, true, true, true);
    }
    else
    {
        prev_aa = nema_enable_aa(false, false, false, false);
    }


    lv_ambiq_set_blend_blit((lv_draw_ambiq_unit_t*)t->draw_unit, blending_mode);

    if(!transformed)
    {
        //Blit
        if(!tile_draw_one_by_one){
            nema_blit(coords->x1 - layer->buf_area.x1, coords->y1 - layer->buf_area.y1);
        }
        else{
            lv_area_t tile_area;
            uint32_t img_w = draw_dsc->header.w;
            uint32_t img_h = draw_dsc->header.w;
            if(lv_area_get_width(&draw_dsc->image_area) >= 0) {
                tile_area = draw_dsc->image_area;
            }
            else {
                tile_area = *coords;
            }
            lv_area_set_width(&tile_area, img_w);
            lv_area_set_height(&tile_area, img_h);

            int32_t tile_x_start = tile_area.x1;

            while(tile_area.y1 <= coords->y2) {
                while(tile_area.x1 <= coords->x2) {

                    lv_area_t clipped_img_area;
                    if(lv_area_intersect(&clipped_img_area, &tile_area, coords)) {
                        nema_blit(tile_area.x1 - layer->buf_area.x1, tile_area.y1 - layer->buf_area.y1);
                    }

                    tile_area.x1 += img_w;
                    tile_area.x2 += img_w;
                }

                tile_area.y1 += img_h;
                tile_area.y2 += img_h;
                tile_area.x1 = tile_x_start;
                tile_area.x2 = tile_x_start + img_w - 1;
            }           
        }
    }
    else
    {

        // handle rotation

        //calculate rotation matrix
        nema_matrix3x3_t m;
        nema_mat3x3_load_identity(m);
        nema_mat3x3_translate(m, - draw_dsc->pivot.x, - draw_dsc->pivot.y);
        nema_mat3x3_scale(m, draw_dsc->scale_x/256.f, draw_dsc->scale_y/256.f);
        nema_mat3x3_rotate(m, draw_dsc->rotation/10.f);
        nema_mat3x3_shear(m, draw_dsc->skew_x/10.f, draw_dsc->skew_y/10.f);
        nema_mat3x3_translate(m, draw_dsc->pivot.x, draw_dsc->pivot.y);
        //handle the special case when the image coordinate is not the same as draw coordinate
        nema_mat3x3_translate(m, coords->x1  - layer->buf_area.x1, coords->y1  - layer->buf_area.y1); 

        //save the matrix before invert
        nema_matrix3x3_t m_draw;
        nema_mat3x3_copy(m_draw, m);

        // invert the matrix
        nema_mat3x3_invert(m);
        nema_set_matrix(m);



        // //rotate points
        // nema_mat3x3_translate(m_draw, coords->x1  - layer->buf_area.x1, coords->y1  - layer->buf_area.y1); 
        
        float x0 = 0;
        float y0 = 0;
        float x1 = x0 + lv_area_get_width(coords) - 1;
        float y1 = y0;
        float x2 = x0 + lv_area_get_width(coords) - 1;
        float y2 = y0 + lv_area_get_height(coords) - 1;
        float x3 = x0;
        float y3 = y0 + lv_area_get_height(coords) - 1;

        nema_mat3x3_mul_vec(m_draw, &x0, &y0);
        nema_mat3x3_mul_vec(m_draw, &x1, &y1);
        nema_mat3x3_mul_vec(m_draw, &x2, &y2);
        nema_mat3x3_mul_vec(m_draw, &x3, &y3);

        //draw
        nema_raster_quad_f(x0, y0,
                           x1, y1,
                           x2, y2,
                           x3, y3);
    }




    // handle clip radius(TODO)
    // enable tilling when rotation(TODO)
    // AL88 format is this same as NEMA_AL88?

    
    //Set antialias
    if(draw_dsc->antialias)
    {
        nema_enable_aa_flags(prev_aa);
    }

    nema_cmdlist_t * current_cl = nema_cl_get_bound();
    nema_cl_submit(current_cl);
    nema_cl_wait(current_cl);
    nema_cl_rewind(current_cl);

    lv_image_decoder_close(&decoder_dsc);
    if(need_release_mask_decoder)
    {
        lv_image_decoder_close(&mask_decoder_dsc);
    }
    
}


#endif /*LV_USE_DRAW_AMBIQ*/
