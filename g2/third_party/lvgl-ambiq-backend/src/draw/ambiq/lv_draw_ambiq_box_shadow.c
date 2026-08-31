/**
 * @file lv_draw_ambiq_box_shadow.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "../../misc/lv_area_private.h"
#include "../lv_draw_private.h"
#include "lv_draw_ambiq.h"

#if LV_USE_DRAW_AMBIQ

#include "../../core/lv_global.h"
#include "../../misc/lv_math.h"
#include "../../core/lv_refr.h"
#include "../../misc/lv_assert.h"
#include "../../stdlib/lv_string.h"
#include "lv_draw_ambiq_private.h"

/*********************
 *      DEFINES
 *********************/
#define SHADOW_UPSCALE_SHIFT    6
#define SHADOW_ENHANCE          1


/*********************
 *      DEFINES
 *********************/


/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/
static void shadow_draw_corner_buf(const lv_area_t * coords, lv_opa_t * sh_buf, int32_t s,
                                                               int32_t r);

/**********************
 *  STATIC VARIABLES
 **********************/

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void lv_draw_ambiq_box_shadow(lv_draw_task_t * t, const lv_draw_box_shadow_dsc_t * dsc, const lv_area_t * coords)
{
    /*Calculate the rectangle which is blurred to get the shadow in `shadow_area`*/
    lv_area_t core_area;
    core_area.x1 = coords->x1  + dsc->ofs_x - dsc->spread;
    core_area.x2 = coords->x2  + dsc->ofs_x + dsc->spread;
    core_area.y1 = coords->y1  + dsc->ofs_y - dsc->spread;
    core_area.y2 = coords->y2  + dsc->ofs_y + dsc->spread;

    /*Calculate the bounding box of the shadow*/
    lv_area_t shadow_area;
    shadow_area.x1 = core_area.x1 - dsc->width / 2 - 1;
    shadow_area.x2 = core_area.x2 + dsc->width / 2 + 1;
    shadow_area.y1 = core_area.y1 - dsc->width / 2 - 1;
    shadow_area.y2 = core_area.y2 + dsc->width / 2 + 1;

    lv_opa_t opa = dsc->opa;
    if(opa > LV_OPA_MAX) opa = LV_OPA_COVER;

    /* Get layer buffer area */
    lv_layer_t * layer = t->target_layer;
    int32_t layer_buf_start_x = layer->buf_area.x1;
    int32_t layer_buf_start_y = layer->buf_area.y1;
    int32_t layer_buf_width = lv_area_get_width(&layer->buf_area);
    int32_t layer_buf_height = lv_area_get_height(&layer->buf_area);

    lv_draw_ambiq_unit_t* unit = (lv_draw_ambiq_unit_t*)t->draw_unit;

    /*Get clipped draw area which is the real draw area.
     *It is always the same or inside `shadow_area`*/
    lv_area_t draw_area;
    if(!lv_area_intersect(&draw_area, &shadow_area, &t->clip_area)) return;

    /*Consider 1 px smaller bg to be sure the edge will be covered by the shadow*/
    lv_area_t bg_area;
    lv_area_copy(&bg_area, coords);
    lv_area_increase(&bg_area, -1, -1);

    /*Get the clamped radius*/
    int32_t r_bg = dsc->radius;
    int32_t short_side = LV_MIN(lv_area_get_width(&bg_area), lv_area_get_height(&bg_area));
    if(r_bg > short_side >> 1) r_bg = short_side >> 1;

    /*Get the clamped radius*/
    int32_t r_sh = dsc->radius;
    short_side = LV_MIN(lv_area_get_width(&core_area), lv_area_get_height(&core_area));
    if(r_sh > short_side >> 1) r_sh = short_side >> 1;

    /*Get how many pixels are affected by the blur on the corners*/
    int32_t corner_size = dsc->width  + r_sh;

    lv_opa_t * sh_buf;


    sh_buf = lv_malloc(corner_size * corner_size);
    LV_ASSERT_MALLOC(sh_buf);
    shadow_draw_corner_buf(&core_area, (lv_opa_t *)sh_buf, dsc->width, r_sh);

    /*Skip a lot of masking if the background will cover the shadow that would be masked out*/
    bool simple = dsc->bg_cover;

    lv_area_t blend_area;
    lv_area_t raster_area;
    lv_area_t clip_raster_area;



    int32_t w_half = shadow_area.x1 + lv_area_get_width(&shadow_area) / 2;
    int32_t h_half = shadow_area.y1 + lv_area_get_height(&shadow_area) / 2;

    /*Draw the corners if they are on the current clip area and not fully covered by the bg*/


    /*transformation matrix for texture mapping*/
    nema_matrix3x3_t m;

    /* stencil buffer to hold the shadow */
    lv_result_t res = lv_draw_ambiq_stencil_buffer_adjust(unit, layer_buf_width, layer_buf_width);
    if(res != LV_RESULT_OK) {
        lv_free(sh_buf);
        return;
    }

    /* bind the stencil buffer to TEX1*/
    nema_bind_tex(NEMA_TEX1, (uintptr_t)unit->stencil_buffer->data, unit->stencil_buffer->header.w, unit->stencil_buffer->header.h, NEMA_A8, -1, NEMA_FILTER_PS);

    /* bind the blurred corner buffer to TEX2*/
    nema_bind_tex(NEMA_TEX2, (uintptr_t)sh_buf, corner_size, corner_size, NEMA_A8, -1, NEMA_FILTER_PS);

    /* set the blend mode to SRC*/
    lv_ambiq_blend_mode_change(unit, NEMA_BL_SRC, NEMA_TEX1, NEMA_TEX2, NEMA_NOTEX, false);

    nema_set_clip_temp(0 , 0 , layer_buf_width, layer_buf_height);


    /*Top right corner*/
    blend_area.x2 = shadow_area.x2;
    blend_area.x1 = shadow_area.x2 - corner_size + 1;
    blend_area.y1 = shadow_area.y1;
    blend_area.y2 = shadow_area.y1 + corner_size - 1;

    /*Do not overdraw the other top corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.x1 = LV_MAX(blend_area.x1, w_half);
    raster_area.y2 = LV_MIN(blend_area.y2, h_half);
    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {

        /* Blit the blurred corner to the stencil buffer*/

        /* set the translate matrix*/
        nema_mat3x3_load_identity(m);
        nema_mat3x3_translate(m, -(blend_area.x1 - layer_buf_start_x), -(blend_area.y1 - layer_buf_start_y));
        nema_set_matrix(m);

        /* draw the blurred corner to the stencil buffer*/
        nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                         clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);
    }



    /*Bottom right corner.*/
    blend_area.x2 = shadow_area.x2;
    blend_area.x1 = shadow_area.x2 - corner_size + 1;
    blend_area.y1 = shadow_area.y2 - corner_size + 1;
    blend_area.y2 = shadow_area.y2;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.x1 = LV_MAX(blend_area.x1, w_half);
    raster_area.y1 = LV_MAX(blend_area.y1, h_half + 1);

    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {
    
        /* Blit the blurred corner to the stencil buffer*/
    
        /* set the translate matrix*/
        nema_mat3x3_load_identity(m);
        m[1][1] = -1;
        m[0][2] = blend_area.x1 - layer_buf_start_x;
        m[1][2] = corner_size - 1 + blend_area.y1 - layer_buf_start_y;
        nema_mat3x3_invert(m);
        nema_set_matrix(m);
    
        /* draw the blurred corner to the stencil buffer*/
        nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                        clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);
    }

    /*Bottom left corner.
     *Almost the same as bottom right just read the lines of `sh_buf` from then end*/
    blend_area.x1 = shadow_area.x1 ;
    blend_area.x2 = shadow_area.x1 + corner_size - 1;
    blend_area.y1 = shadow_area.y2 - corner_size + 1;
    blend_area.y2 = shadow_area.y2;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);  
    raster_area.y1 = LV_MAX(blend_area.y1, h_half + 1);
    raster_area.x2 = LV_MIN(blend_area.x2, w_half - 1);

    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {
        /* Blit the blurred corner to the stencil buffer*/
    
        /* set the translate matrix*/
        nema_mat3x3_load_identity(m);
        m[0][0] = -1;
        m[1][1] = -1;
        m[0][2] = corner_size - 1 + blend_area.x1 - layer_buf_start_x;
        m[1][2] = corner_size - 1 + blend_area.y1 - layer_buf_start_y;
        nema_mat3x3_invert(m);
        nema_set_matrix(m);
    
        /* draw the blurred corner to the stencil buffer*/
        nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                        clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);
    }

    /*Top left corner*/
    blend_area.x1 = shadow_area.x1;
    blend_area.x2 = shadow_area.x1 + corner_size - 1;
    blend_area.y1 = shadow_area.y1;
    blend_area.y2 = shadow_area.y1 + corner_size - 1;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.x2 = LV_MIN(blend_area.x2, w_half - 1);
    raster_area.y2 = LV_MIN(blend_area.y2, h_half);

    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {
        /* set the translate matrix*/
        nema_mat3x3_load_identity(m);
        m[0][0] = -1;
        m[0][2] = corner_size - 1 + blend_area.x1 - layer_buf_start_x;
        m[1][2] = blend_area.y1 - layer_buf_start_y;
        nema_mat3x3_invert(m);
        nema_set_matrix(m);
    
        /* draw the blurred corner to the stencil buffer*/
        nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                        clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);
    }



    /*Top side*/
    blend_area.x1 = shadow_area.x1 + corner_size;
    blend_area.x2 = shadow_area.x2 - corner_size;
    blend_area.y1 = shadow_area.y1;
    blend_area.y2 = shadow_area.y1 + corner_size - 1;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.y2 = LV_MIN(blend_area.y2, h_half);

    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {

        /* Blit the blurred corner to the stencil buffer*/
    
        /* set the translate matrix*/
        nema_mat3x3_load_identity(m);
        nema_mat3x3_translate(m, -(blend_area.x2 - layer_buf_start_x), -(blend_area.y1 - layer_buf_start_y));
        nema_set_matrix(m);
    
        /* draw the blurred corner to the stencil buffer*/
        nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                        clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);        

    }


    /*Bottom side*/
    blend_area.x1 = shadow_area.x1 + corner_size;
    blend_area.x2 = shadow_area.x2 - corner_size;
    blend_area.y1 = shadow_area.y2 - corner_size + 1;
    blend_area.y2 = shadow_area.y2;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.y1 = LV_MAX(blend_area.y1, h_half + 1);

    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {

        /* Blit the blurred corner to the stencil buffer*/
    
        /* set the translate matrix*/
        nema_mat3x3_load_identity(m);

        m[1][1] = -1;
        m[0][2] = blend_area.x2 - layer_buf_start_x;
        m[1][2] = corner_size - 1 + blend_area.y1 - layer_buf_start_y;
        nema_mat3x3_invert(m);
        nema_set_matrix(m);
    
        /* draw the blurred corner to the stencil buffer*/
        nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                        clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);        

    }

    /*Right side*/
    blend_area.x1 = shadow_area.x2 - corner_size + 1;
    blend_area.x2 = shadow_area.x2;
    blend_area.y1 = shadow_area.y1 + corner_size;
    blend_area.y2 = shadow_area.y2 - corner_size;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.y1 = LV_MIN(blend_area.y1, h_half + 1);
    raster_area.y2 = LV_MAX(blend_area.y2, h_half);
    raster_area.x1 = LV_MAX(blend_area.x1, w_half);

    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {

        /* Blit the blurred corner to the stencil buffer*/
    
        /* set the translate matrix*/
        nema_mat3x3_load_identity(m);
        nema_mat3x3_translate(m, -(blend_area.x1 - layer_buf_start_x), -(blend_area.y1 - corner_size + 1 - layer_buf_start_y));
        nema_set_matrix(m);
    
        /* draw the blurred corner to the stencil buffer*/
        nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                        clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);

    }

    /*Left side*/
    blend_area.x1 = shadow_area.x1;
    blend_area.x2 = shadow_area.x1 + corner_size - 1;
    blend_area.y1 = shadow_area.y1 + corner_size;
    blend_area.y2 = shadow_area.y2 - corner_size;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.y1 = LV_MIN(blend_area.y1, h_half + 1);
    raster_area.y2 = LV_MAX(blend_area.y2, h_half);
    raster_area.x2 = LV_MIN(blend_area.x2, w_half - 1);

    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {

            /* Blit the blurred corner to the stencil buffer*/
        
            /* set the translate matrix*/
            nema_mat3x3_load_identity(m);
            m[0][0] = -1;
            m[0][2] = corner_size - 1 + blend_area.x1 - layer_buf_start_x;
            m[1][2] = blend_area.y1 - corner_size + 1 - layer_buf_start_y;
            nema_mat3x3_invert(m);
            nema_set_matrix(m);
        
            /* draw the blurred corner to the stencil buffer*/
            nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                            clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);

    }

    /* set the blend mode to SRC*/
    lv_ambiq_blend_mode_change(unit, NEMA_BL_SRC, NEMA_TEX1, NEMA_NOTEX, NEMA_NOTEX, false);
    nema_set_raster_color(0xff000000);

    /*Draw the center rectangle.*/
    blend_area.x1 = shadow_area.x1 + corner_size ;
    blend_area.x2 = shadow_area.x2 - corner_size;
    blend_area.y1 = shadow_area.y1 + corner_size;
    blend_area.y2 = shadow_area.y2 - corner_size;
    /*Do not overdraw the other corners*/
    lv_area_copy(&raster_area, &blend_area);
    raster_area.y1 = LV_MIN(blend_area.y1, h_half + 1);
    raster_area.y2 = LV_MAX(blend_area.y2, h_half);


    if(lv_area_intersect(&clip_raster_area, &raster_area, &t->clip_area) &&
       !lv_area_is_in(&clip_raster_area, &bg_area, r_bg)) {
            nema_raster_rect(clip_raster_area.x1 - layer_buf_start_x, clip_raster_area.y1 - layer_buf_start_y, 
                            clip_raster_area.x2 - clip_raster_area.x1 + 1, clip_raster_area.y2 - clip_raster_area.y1 + 1);
    }

    
    if(!simple)
    {
        nema_set_raster_color(0x00000000);
        nema_raster_rounded_rect(bg_area.x1 - layer_buf_start_x, bg_area.y1 - layer_buf_start_y, 
                                lv_area_get_width(&bg_area), lv_area_get_height(&bg_area), r_bg);
    }

    uint32_t blending_mode;

    if(layer->color_format == LV_COLOR_FORMAT_ARGB8888)
    {
        blending_mode = NEMA_BL_SRC_OVER;
    }
    else
    {
        blending_mode = NEMA_BL_SIMPLE;
    }

    nema_mat3x3_load_identity(m);
    nema_set_matrix(m);

    /* draw shadow with stencil*/

    uint32_t shadow_color = lv_ambiq_color_convert(dsc->color, dsc->opa);
    if ( dsc->opa == 0xFF) {
        lv_ambiq_set_blend_blit(unit, blending_mode);
    } else {
        lv_ambiq_set_blend_blit(unit, blending_mode|NEMA_BLOP_MODULATE_A);
        nema_set_const_color(shadow_color);
    }
    nema_set_tex_color(shadow_color);

    nema_set_clip_pop();

    nema_raster_rect(shadow_area.x1 - layer_buf_start_x, shadow_area.y1 - layer_buf_start_y, 
                    lv_area_get_width(&shadow_area), lv_area_get_height(&shadow_area));

    nema_cmdlist_t * cl = nema_cl_get_bound();
    nema_cl_submit(cl);
    nema_cl_wait(cl);
    nema_cl_rewind(cl);

    lv_free(sh_buf);
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

/**
 * Calculate a blurred corner
 * @param coords Coordinates of the shadow
 * @param sh_buf a buffer to store the result. Its size should be `(sw + r)^2 * 2`
 * @param sw shadow width
 * @param r radius
 */
static void LV_ATTRIBUTE_FAST_MEM shadow_draw_corner_buf(const lv_area_t * coords, lv_opa_t * sh_buf, int32_t sw,
                                                         int32_t r)
{
    int32_t sw_ori = sw;
    int32_t size = sw_ori  + r;

    lv_area_t sh_area;
    lv_area_copy(&sh_area, coords);
    sh_area.x2 = sw / 2 + r - 1  - ((sw & 1) ? 0 : 1);
    sh_area.y1 = sw / 2 + 1;

    sh_area.x1 = sh_area.x2 - lv_area_get_width(coords);
    sh_area.y2 = sh_area.y1 + lv_area_get_height(coords);

    lv_draw_sw_mask_radius_param_t mask_param;
    lv_draw_sw_mask_radius_init(&mask_param, &sh_area, r, false);

#if SHADOW_ENHANCE
    /*Set half shadow width because blur will be repeated*/
    if(sw_ori == 1) sw = 1;
    else sw = sw_ori >> 1;
#endif /*SHADOW_ENHANCE*/

    int32_t y;
    lv_opa_t * mask_line = lv_malloc(size);
    LV_ASSERT_MALLOC(mask_line);
    lv_opa_t * sh_ups_tmp_buf = (lv_opa_t *)sh_buf;
    for(y = 0; y < size; y++) {
        lv_memset(mask_line, 0xff, size);
        lv_draw_sw_mask_res_t mask_res = mask_param.dsc.cb(mask_line, 0, y, size, &mask_param);
        if(mask_res == LV_DRAW_SW_MASK_RES_TRANSP) {
            lv_memzero(sh_ups_tmp_buf, size * sizeof(sh_ups_tmp_buf[0]));
        }
        else {
            lv_memcpy(sh_ups_tmp_buf, mask_line, size);
        }

        sh_ups_tmp_buf += size;
    }
    lv_free(mask_line);

    lv_draw_sw_mask_free_param(&mask_param);

    if(sw == 1) {
        return;
    }

    /*Create a temporary buff for calculating shadows*/ 
    lv_draw_buf_t * sh_ups_blur_buf = lv_draw_buf_create(size + sw, size + sw, LV_COLOR_FORMAT_A8, 0);

    /*Bind src tex*/
    nema_bind_tex(NEMA_TEX1, (uintptr_t)sh_buf, size, size, NEMA_A8, -1, NEMA_FILTER_PS);

    /*Bind tmp tex*/
    nema_bind_tex(NEMA_TEX2, (uintptr_t)sh_ups_blur_buf->data, size + sw, size + sw, NEMA_A8, -1, NEMA_FILTER_PS);

    lv_ambiq_shadow_blur_corner(size, sw, NEMA_TEX1, NEMA_TEX2);

#if SHADOW_ENHANCE
    sw += sw_ori & 1;
    if(sw > 1) {
        lv_ambiq_shadow_blur_corner(size, sw, NEMA_TEX1, NEMA_TEX2);
    }
#endif

    /*Run this GPU rendering before destroying the temporary buffer.*/
    nema_cmdlist_t * cl = nema_cl_get_bound();
    nema_cl_submit(cl);
    nema_cl_wait(cl);
    nema_cl_rewind(cl);

    /*This call has no immediate effect here; it's used to update the global blend mode after calling `lv_ambiq_shadow_blur_corner`.
     *At this point, the blend mode must be updated to any valid state (or restore the previous one)
     *to maintain correct global rendering behavior.*/
    lv_ambiq_blend_mode_change(NULL, NEMA_BL_SRC, NEMA_TEX1, NEMA_TEX2, NEMA_NOTEX, false);

    /*Destroy temp buffer*/
    lv_draw_buf_destroy(sh_ups_blur_buf);
}

#endif /*LV_USE_DRAW_AMBIQ*/