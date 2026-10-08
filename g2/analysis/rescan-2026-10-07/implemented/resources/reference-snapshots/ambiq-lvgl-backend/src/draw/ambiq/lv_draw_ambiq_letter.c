/**
 * @file lv_draw_ambiq_letter.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "../lv_draw_label_private.h"
#include "lv_draw_ambiq.h"
#if LV_USE_DRAW_AMBIQ

#include "lv_draw_ambiq_private.h"
#include "../../display/lv_display.h"
#include "../../misc/lv_math.h"
#include "../../misc/lv_assert.h"
#include "../../misc/lv_area.h"
#include "../../misc/lv_style.h"
#include "../../font/lv_font.h"
#include "../../core/lv_refr_private.h"
#include "../../stdlib/lv_string.h"
#include "../../font/lv_font_fmt_txt.h"

/*********************
 *      DEFINES
 *********************/
#define NEMA_COORD_LIMIT 2046

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/

static void /* LV_ATTRIBUTE_FAST_MEM */ draw_letter_cb(lv_draw_task_t * t, lv_draw_glyph_dsc_t * glyph_draw_dsc,
                                                       lv_draw_fill_dsc_t * fill_draw_dsc, const lv_area_t * fill_area);

/**********************
 *  STATIC VARIABLES
 **********************/

/**********************
 *  GLOBAL VARIABLES
 **********************/

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/
void lv_draw_ambiq_label(lv_draw_task_t * t, const lv_draw_label_dsc_t * dsc, const lv_area_t * coords)
{
    if(dsc->opa <= LV_OPA_MIN) return;

    LV_PROFILER_DRAW_BEGIN;
    lv_draw_label_iterate_characters(t, dsc, coords, draw_letter_cb);
    LV_PROFILER_DRAW_END;
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

static bool is_width_aligned(uint32_t width, uint32_t format)
{
    switch(format) {
        case LV_FONT_GLYPH_FORMAT_A1:
            return (width % 8) == 0;
        case LV_FONT_GLYPH_FORMAT_A2:
            return (width % 4) == 0;
        case LV_FONT_GLYPH_FORMAT_A4:
            return (width % 2) == 0;
        case LV_FONT_GLYPH_FORMAT_A8:
            return true;
        default:
            LV_LOG_ERROR("Unsupported format!");
            return false;
    }

    return false;
}

static void draw_raw_bitmap_internal(lv_draw_ambiq_unit_t* unit, const void* bitmap, int32_t bitmap_w, int32_t bitmap_h, 
                                        lv_area_t* raster_area, 
                                        lv_font_glyph_format_t format, 
                                        uint32_t color, bool aligned, bool extend_width)
{
    nema_tex_format_t nema_format;

    switch(format) {
        case LV_FONT_GLYPH_FORMAT_A1:
        case LV_FONT_GLYPH_FORMAT_A1_ALIGNED:
            nema_format = NEMA_A1;
            break;
        case LV_FONT_GLYPH_FORMAT_A2:
        case LV_FONT_GLYPH_FORMAT_A2_ALIGNED:
            nema_format = NEMA_A2;
            break;
        case LV_FONT_GLYPH_FORMAT_A4:
        case LV_FONT_GLYPH_FORMAT_A4_ALIGNED:
            nema_format = NEMA_A4;
            break;
        case LV_FONT_GLYPH_FORMAT_A8:
        case LV_FONT_GLYPH_FORMAT_A8_ALIGNED:
            nema_format = NEMA_A8;
            break;
        default:
            LV_LOG_ERROR("Unsupported format!");
            return;
    }

    if ( (color & 0xFF000000U) == 0xFF000000U) {
        lv_ambiq_set_blend_blit(unit, NEMA_BL_SIMPLE);
    } else {
        lv_ambiq_set_blend_blit(unit, NEMA_BL_SIMPLE|NEMA_BLOP_MODULATE_A);
        nema_set_const_color(color); 
    }
    nema_set_tex_color(color);

    nema_matrix3x3_t m;
    nema_mat3x3_load_identity(m);

    if (aligned) {
        if(extend_width && ((bitmap_w % 2) == 0))
            bitmap_w += 2;

        nema_bind_src_tex((uintptr_t)bitmap, bitmap_w, bitmap_h, nema_format, -1, NEMA_FILTER_PS);
        nema_mat3x3_translate(m, -raster_area->x1, -raster_area->y1);
    } else {
        nema_bind_src_tex((uintptr_t)(bitmap), bitmap_w * bitmap_h, 1, nema_format, 0, NEMA_FILTER_PS);
        m[0][1] = bitmap_w;
        m[0][2] = -raster_area->x1 - (raster_area->y1 * bitmap_w) - (0.5 * bitmap_w);
    }


    nema_set_matrix(m);

    nema_raster_rect(raster_area->x1, raster_area->y1, 
                    raster_area->x2 - raster_area->x1 + 1, 
                    raster_area->y2 - raster_area->y1 + 1);

}

static void LV_ATTRIBUTE_FAST_MEM draw_letter_cb(lv_draw_task_t * t, lv_draw_glyph_dsc_t * glyph_draw_dsc,
                                                 lv_draw_fill_dsc_t * fill_draw_dsc, const lv_area_t * fill_area)
{

    lv_draw_ambiq_unit_t * draw_ambiq_unit = (lv_draw_ambiq_unit_t *)t->draw_unit;
    lv_layer_t * layer = t->target_layer;

    bool cpu_gpu_sync = false;

    if (fill_draw_dsc == NULL && glyph_draw_dsc == NULL) {
        return;
    }
    if  (fill_draw_dsc && glyph_draw_dsc) {
        LV_LOG_WARN("Both fill and glyph draw descriptors are not NULL, use the glyph draw descriptor");
    }
    

    uint32_t color;
    if (glyph_draw_dsc) {
        color = lv_ambiq_color_convert(glyph_draw_dsc->color, glyph_draw_dsc->opa);
    }
    else {
        color = lv_ambiq_color_convert(fill_draw_dsc->color, fill_draw_dsc->opa);
    }


    lv_area_t raster_coords;

    if(glyph_draw_dsc) {
        switch(glyph_draw_dsc->format) {
            case LV_FONT_GLYPH_FORMAT_NONE: {
#if LV_USE_FONT_PLACEHOLDER
                    if(glyph_draw_dsc->bg_coords == NULL) break;
                    lv_ambiq_set_blend_fill(draw_ambiq_unit, NEMA_BL_SIMPLE);

                    lv_area_copy(&raster_coords, glyph_draw_dsc->bg_coords);
                    lv_area_move(&raster_coords, -layer->buf_area.x1, -layer->buf_area.y1);

                    nema_draw_rect(raster_coords.x1, raster_coords.y1, 
                                   lv_area_get_width(&raster_coords), lv_area_get_height(&raster_coords),
                                   color);
#endif
                }
                break;

            case LV_FONT_GLYPH_FORMAT_A1:
            case LV_FONT_GLYPH_FORMAT_A2:
            case LV_FONT_GLYPH_FORMAT_A3:
            case LV_FONT_GLYPH_FORMAT_A4:
            case LV_FONT_GLYPH_FORMAT_A8: 
            case LV_FONT_GLYPH_FORMAT_A1_ALIGNED:
            case LV_FONT_GLYPH_FORMAT_A2_ALIGNED:
            case LV_FONT_GLYPH_FORMAT_A4_ALIGNED:
            case LV_FONT_GLYPH_FORMAT_A8_ALIGNED:

                    const lv_font_t * font = glyph_draw_dsc->g->resolved_font;
                    lv_font_fmt_txt_dsc_t * fdsc = (lv_font_fmt_txt_dsc_t *)font->dsc;
                    lv_font_glyph_dsc_t* g = glyph_draw_dsc->g;

                    lv_area_copy(&raster_coords, glyph_draw_dsc->letter_coords);
                    lv_area_move(&raster_coords, -layer->buf_area.x1, -layer->buf_area.y1);

                    bool is_within_nema_coord_limit = ((g->box_h * g->box_w) <= NEMA_COORD_LIMIT) ? true : false;
                    bool is_aligned;
                    bool extend_width;
                    if (fdsc->bitmap_format == LV_FONT_FMT_PLAIN_ALIGNED) {
                        is_aligned = true;
                        extend_width = true;
                    } else if (is_width_aligned(g->box_w, g->format)) {
                        is_aligned = true;
                        extend_width = false;
                    } else {
                        is_aligned = false;
                        extend_width = false;
                    }

                    bool is_plain = false;
                    if(font->get_glyph_bitmap == lv_font_get_bitmap_fmt_txt) {
                        if(fdsc->bitmap_format == LV_FONT_FMT_TXT_PLAIN || fdsc->bitmap_format == LV_FONT_FMT_PLAIN_ALIGNED) {
                            is_plain = true;
                        }
                    }
                    if(glyph_draw_dsc->format == LV_FONT_GLYPH_FORMAT_A3) {
                        is_plain = false;
                    }

                    if(is_plain && is_aligned)
                    {
                        g->req_raw_bitmap = 1;
                        glyph_draw_dsc->glyph_data = lv_font_get_glyph_bitmap(g, NULL); 
                        draw_raw_bitmap_internal(draw_ambiq_unit, glyph_draw_dsc->glyph_data, g->box_w, g->box_h,
                                &raster_coords, g->format, color, true, extend_width);   
                    }
                    else if(is_plain && is_within_nema_coord_limit)
                    {
                        g->req_raw_bitmap = 1;
                        glyph_draw_dsc->glyph_data = lv_font_get_glyph_bitmap(g, NULL); 
                        draw_raw_bitmap_internal(draw_ambiq_unit, glyph_draw_dsc->glyph_data, g->box_w, g->box_h,
                                &raster_coords, g->format, color, false, false);   
                    }
                    else
                    {
                        LV_LOG_WARN("CPU GPU sync required for unaligned bitmap, Slow down the performance!");
                        g->req_raw_bitmap = 0;
                        glyph_draw_dsc->glyph_data = lv_font_get_glyph_bitmap(glyph_draw_dsc->g, glyph_draw_dsc->_draw_buf);
                        if (glyph_draw_dsc->glyph_data == NULL) {
                            LV_LOG_WARN("Glyph data is NULL");
                            break;
                        }

                        void* aligned_a8_bitmap = (void*)glyph_draw_dsc->_draw_buf->data;
                        draw_raw_bitmap_internal(draw_ambiq_unit, aligned_a8_bitmap, g->box_w, g->box_h,
                            &raster_coords, LV_FONT_GLYPH_FORMAT_A8, color, true, false); 
                        cpu_gpu_sync = true;  
                    }
                    break;
 

            case LV_FONT_GLYPH_FORMAT_IMAGE: {
                    lv_draw_image_dsc_t img_dsc;
                    lv_draw_image_dsc_init(&img_dsc);
                    img_dsc.rotation = 0;
                    img_dsc.scale_x = LV_SCALE_NONE;
                    img_dsc.scale_y = LV_SCALE_NONE;
                    img_dsc.opa = glyph_draw_dsc->opa;
                    img_dsc.src = glyph_draw_dsc->glyph_data;
                    lv_draw_ambiq_image(t, &img_dsc, glyph_draw_dsc->letter_coords);
                }
                break;

            case LV_FONT_GLYPH_FORMAT_VECTOR: {
                    lv_draw_ambiq_vector_font(t, glyph_draw_dsc);
                }
                break;


            default:
                break;
        }

    }

    if(fill_draw_dsc && fill_area) {
        lv_ambiq_set_blend_fill(draw_ambiq_unit, NEMA_BL_SIMPLE);

        lv_area_copy(&raster_coords, fill_area);
        lv_area_move(&raster_coords, -layer->buf_area.x1, -layer->buf_area.y1);

        nema_fill_rect(raster_coords.x1, raster_coords.y1, 
                        lv_area_get_width(&raster_coords), lv_area_get_height(&raster_coords),
                        color);
    }

    if(cpu_gpu_sync) {
        nema_cmdlist_t * current_cl = nema_cl_get_bound();
        nema_cl_submit(current_cl);
        nema_cl_wait(current_cl);
        nema_cl_rewind(current_cl);
    }
}

#endif /*LV_USE_DRAW_AMBIQ*/
