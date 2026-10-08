/**
 * @file lv_draw_ambiq_color.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "lv_draw_ambiq.h"

#if LV_USE_DRAW_AMBIQ

#include "lv_draw_ambiq_private.h"
#include "../lv_image_decoder_private.h"
#include "../lv_draw_image_private.h"

#include "nema_graphics.h"

typedef struct {
    uint32_t code;
    const char *message;
} error_map_t;

static const error_map_t vg_error_map[] = {
    { NEMA_VG_ERR_NO_ERROR, "NO_ERROR" },
    { NEMA_VG_ERR_BAD_HANDLE, "BAD_HANDLE" },
    { NEMA_VG_ERR_BAD_BUFFER, "BAD_BUFFER" },
    { NEMA_VG_ERR_INVALID_FILL_RULE, "INVALID_FILL_RULE" },
    { NEMA_VG_ERR_INVALID_PAINT_TYPE, "INVALID_PAINT_TYPE" },
    { NEMA_VG_ERR_INVALID_VERTEX_DATA, "INVALID_VERTEX_DATA" },
    { NEMA_VG_ERR_NO_RADIAL_ENABLED, "NO_RADIAL_ENABLED" },
    { NEMA_VG_ERR_NO_BOUND_CL, "NO_BOUND_CL" },
    { NEMA_VG_ERR_INVALID_ARGUMENTS, "INVALID_ARGUMENTS" },
    { NEMA_VG_ERR_INVALID_ARC_DATA, "INVALID_ARC_DATA" },
    { NEMA_VG_ERR_CL_FULL, "CL_FULL" },
    { NEMA_VG_ERR_DRAW_OUT_OF_BOUNDS, "DRAW_OUT_OF_BOUNDS" },
    { NEMA_VG_ERR_INVALID_MASKING_OBJ, "INVALID_MASKING_OBJ" },
    { NEMA_VG_ERR_INVALID_MASKING_FORMAT, "INVALID_MASKING_FORMAT" },
    { NEMA_VG_ERR_INVALID_LUT_IDX_FORMAT, "INVALID_LUT_IDX_FORMAT" },
    { NEMA_VG_ERR_COORDS_OUT_OF_RANGE, "COORDS_OUT_OF_RANGE" },
    { NEMA_VG_ERR_EMPTY_TSVG, "EMPTY_TSVG" },
    { NEMA_VG_ERR_NO_BOUND_FONT, "NO_BOUND_FONT" },
    { NEMA_VG_ERR_UNSUPPORTED_FONT, "UNSUPPORTED_FONT" },
    { NEMA_VG_ERR_NON_INVERTIBLE_MATRIX, "NON_INVERTIBLE_MATRIX" },
    { NEMA_VG_ERR_INVALID_GRAD_STOPS, "INVALID_GRAD_STOPS" },
    { NEMA_VG_ERR_NO_INIT, "NO_INIT" },
    { NEMA_VG_ERR_INVALID_STROKE_WIDTH, "INVALID_STROKE_WIDTH" },
    { NEMA_VG_ERR_INVALID_OPACITY, "INVALID_OPACITY" },
    { NEMA_VG_ERR_INVALID_CAP_STYLE, "INVALID_CAP_STYLE" },
    { NEMA_VG_ERR_INVALID_JOIN_STYLE, "INVALID_JOIN_STYLE" },
    { NEMA_VG_ERR_INVALID_STENCIL_SIZE, "INVALID_STENCIL_SIZE" },
    { NEMA_VG_ERR_DEPRECATED_FONT, "DEPRECATED_FONT" },
};

static const error_map_t gpu_error_map[] = {
    { NEMA_ERR_NO_ERROR, "NO_ERROR" },
    { NEMA_ERR_SYS_INIT_FAILURE, "SYS_INIT_FAILURE" },
    { NEMA_ERR_GPU_ABSENT, "GPU_ABSENT" },
    { NEMA_ERR_RB_INIT_FAILURE, "RB_INIT_FAILURE" },
    { NEMA_ERR_NON_EXPANDABLE_CL_FULL, "NON_EXPANDABLE_CL_FULL" },
    { NEMA_ERR_CL_EXPANSION, "CL_EXPANSION" },
    { NEMA_ERR_OUT_OF_GFX_MEMORY, "OUT_OF_GFX_MEMORY" },
    { NEMA_ERR_OUT_OF_HOST_MEMORY, "OUT_OF_HOST_MEMORY" },
    { NEMA_ERR_NO_BOUND_CL, "NO_BOUND_CL" },
    { NEMA_ERR_NO_BOUND_FONT, "NO_BOUND_FONT" },
    { NEMA_ERR_GFX_MEMORY_INIT, "GFX_MEMORY_INIT" },
    { NEMA_ERR_DRIVER_FAILURE, "DRIVER_FAILURE" },
    { NEMA_ERR_MUTEX_INIT, "MUTEX_INIT" },
    { NEMA_ERR_INVALID_BO, "INVALID_BO" },
    { NEMA_ERR_INVALID_CL, "INVALID_CL" },
    { NEMA_ERR_INVALID_CL_ALIGMENT, "INVALID_CL_ALIGMENT" },
    { NEMA_ERR_NO_INIT, "NO_INIT" },
    { NEMA_ERR_INVALID_SECTORED_CL_SIZE, "INVALID_SECTORED_CL_SIZE" },
};

static const char* interpret_error(const error_map_t* map, size_t size, uint32_t code)
{
    for (size_t i = 0; i < size; i++) {
        if (map[i].code == code) {
            return map[i].message;
        }
    }
    return "UNKNOWN";
}

const char *nema_vg_error_interpret(uint32_t error_code)
{
    return interpret_error(vg_error_map, sizeof(vg_error_map)/sizeof(vg_error_map[0]), error_code);
}

const char *nema_raster_error_interpret(uint32_t error_code)
{
    return interpret_error(gpu_error_map, sizeof(gpu_error_map)/sizeof(gpu_error_map[0]), error_code);
}

nema_tex_format_t lv_ambiq_color_format_map_src(lv_color_format_t lvgl_cf)
{
    switch(lvgl_cf)
    {
        case LV_COLOR_FORMAT_L8:
            return NEMA_L8;

        case LV_COLOR_FORMAT_AL88:
            return NEMA_AL88;

        case LV_COLOR_FORMAT_I1:
            return NEMA_L1;
        case LV_COLOR_FORMAT_I2:
            return NEMA_L2;
        case LV_COLOR_FORMAT_I4:
            return NEMA_L4;
        case LV_COLOR_FORMAT_I8:
            return NEMA_L8;

        case LV_COLOR_FORMAT_A1:
            return NEMA_A1;
        case LV_COLOR_FORMAT_A2:
            return NEMA_A2;
        case LV_COLOR_FORMAT_A4:
            return NEMA_A4;
        case LV_COLOR_FORMAT_A8:
            return NEMA_A8;


        case LV_COLOR_FORMAT_RGB565:
            return NEMA_RGB565; 

        case LV_COLOR_FORMAT_RGB565A8:
            return NEMA_RGB565; 

        case LV_COLOR_FORMAT_RGB888:
            return NEMA_BGR24; 

        case LV_COLOR_FORMAT_ARGB8888:
            return NEMA_BGRA8888;

        case LV_COLOR_FORMAT_XRGB8888:
            return NEMA_BGRX8888;

        case LV_COLOR_FORMAT_NEMA_TSC4:
            return NEMA_TSC4;
        case LV_COLOR_FORMAT_NEMA_TSC6:
            return NEMA_TSC6;
        case LV_COLOR_FORMAT_NEMA_TSC6A:
            return NEMA_TSC6A;
        case LV_COLOR_FORMAT_NEMA_TSC12:
            return NEMA_TSC12;
        case LV_COLOR_FORMAT_NEMA_TSC12A:
            return NEMA_TSC12A;

        default:
            return COLOR_FORMAT_INVALID;
    }
}

nema_tex_format_t lv_ambiq_color_format_map_des(lv_color_format_t lvgl_cf)
{
    switch(lvgl_cf)
    {
        case LV_COLOR_FORMAT_RGB565:
            return NEMA_RGB565; 

        case LV_COLOR_FORMAT_RGB888:
            return NEMA_BGR24; 

        case LV_COLOR_FORMAT_ARGB8888:
            return NEMA_BGRA8888;

        case LV_COLOR_FORMAT_XRGB8888:
            return NEMA_BGRX8888;

        case LV_COLOR_FORMAT_L8:
            return NEMA_L8;
        
        case LV_COLOR_FORMAT_AL88:
            return NEMA_AL88;

        case LV_COLOR_FORMAT_A1:
            return NEMA_L1;
        case LV_COLOR_FORMAT_A2:
            return NEMA_L2;
        case LV_COLOR_FORMAT_A4:
            return NEMA_L4;
        case LV_COLOR_FORMAT_A8:
            return NEMA_L8;

        default:
            return COLOR_FORMAT_INVALID;
    }
}

uint32_t lv_ambiq_color_convert(lv_color_t color, lv_opa_t opa)
{
    return nema_rgba(color.red, color.green, color.blue, opa);
}



void lv_ambiq_blend_mode_change(lv_draw_ambiq_unit_t * unit, uint32_t blending_mode, 
                                nema_tex_t dst_tex, nema_tex_t fg_tex, nema_tex_t bg_tex, bool force)
{
    if(unit == NULL) 
        unit = lv_draw_ambiq_get_default_unit();
        
    if( (force == false) &&
        (blending_mode == unit->blend_mode) && (dst_tex == unit->dst_tex) && 
        (fg_tex == unit->fg_tex) && (bg_tex == unit->bg_tex))
    {
        return;
    }
    nema_set_blend(blending_mode, dst_tex, fg_tex, bg_tex);
    unit->blend_mode = blending_mode;
    unit->dst_tex = dst_tex;
    unit->fg_tex = fg_tex;
    unit->bg_tex = bg_tex;
}

void lv_ambiq_set_blend_fill(lv_draw_ambiq_unit_t * unit, uint32_t blending_mode)
{
    lv_ambiq_blend_mode_change(unit, blending_mode, NEMA_TEX0, NEMA_NOTEX, NEMA_NOTEX, false);
}

void lv_ambiq_set_blend_blit(lv_draw_ambiq_unit_t * unit, uint32_t blending_mode)
{
    lv_ambiq_blend_mode_change(unit, blending_mode, NEMA_TEX0, NEMA_TEX1, NEMA_NOTEX, false);
}

void lv_ambiq_blend_mode_clear(lv_draw_ambiq_unit_t * unit)
{
    if(unit == NULL) 
        unit = lv_draw_ambiq_get_default_unit();

    unit->blend_mode = 0;
    unit->dst_tex = NEMA_NOTEX;
    unit->fg_tex = NEMA_NOTEX;
    unit->bg_tex = NEMA_NOTEX;
}

void lv_ambiq_clip_area_change(lv_draw_ambiq_unit_t * unit, const lv_area_t* clip_area, bool force)
{
    if(unit == NULL) 
        unit = lv_draw_ambiq_get_default_unit();

    if( (force == false) &&
    (clip_area->x1 == unit->clip_area.x1) && (clip_area->y1 == unit->clip_area.y1) &&
    (clip_area->x2 == unit->clip_area.x2) && (clip_area->y2 == unit->clip_area.y2))
    {
        return;
    }

    nema_set_clip(clip_area->x1, clip_area->y1, 
                clip_area->x2 - clip_area->x1 + 1, 
                clip_area->y2 - clip_area->y1 + 1);
    unit->clip_area = *clip_area;
}

void lv_ambiq_clip_area_clear(lv_draw_ambiq_unit_t * unit)
{
    if(unit == NULL) 
        unit = lv_draw_ambiq_get_default_unit();

    nema_set_clip(0, 0, unit->des_buffer.header.w, unit->des_buffer.header.h);

    unit->clip_area.x1 = 0;
    unit->clip_area.y1 = 0;
    unit->clip_area.x2 = unit->des_buffer.header.w - 1;
    unit->clip_area.y2 = unit->des_buffer.header.h - 1;
}

static lv_result_t lv_draw_ambiq_nema_context_lock(lv_draw_ambiq_unit_t* unit)
{
#if LV_USE_OS
    LV_ASSERT_MSG(unit != NULL, "Ambiq GPU draw unit is not initialized!");
    lv_result_t res = lv_mutex_lock(&unit->mutex_nema_context);
    if(res != LV_RESULT_OK)
    {
        LV_LOG_ERROR("Ambiq GPU mutex lock failed!");
    }
    else
    {
        unit->nema_context_lock_count ++;
        LV_ASSERT_MSG(unit->nema_context_lock_count == 1, "Ambiq GPU mutex lock count error!");
    }
    return res;
#else
    unit->nema_context_lock_count ++;
    LV_ASSERT_MSG(unit->nema_context_lock_count == 1, "Ambiq GPU mutex lock count error!");
    return LV_RESULT_OK;
#endif
}

static lv_result_t lv_draw_ambiq_nema_context_unlock(lv_draw_ambiq_unit_t* unit)
{
#if LV_USE_OS
    LV_ASSERT_MSG(unit != NULL, "Ambiq GPU draw unit is not initialized!");
    lv_result_t res = lv_mutex_unlock(&unit->mutex_nema_context);
    if(res != LV_RESULT_OK)
    {
        LV_LOG_ERROR("Ambiq GPU mutex unlock failed!");
    }
    else
    {
        unit->nema_context_lock_count --;
        LV_ASSERT_MSG(unit->nema_context_lock_count == 0, "Ambiq GPU mutex lock count error!");
    }
    return res;
#else
    unit->nema_context_lock_count --;
    LV_ASSERT_MSG(unit->nema_context_lock_count == 0, "Ambiq GPU mutex lock count error!");    
    return LV_RESULT_OK;
#endif
}


lv_result_t lv_draw_ambiq_common_start(const lv_draw_buf_t *buf_dsc, const lv_area_t *clip_area_raw, bool extend_color_format_support)
{
	lv_draw_ambiq_unit_t* unit = lv_draw_ambiq_get_default_unit();

    // If clip_area is NULL, we need to set the clip area to the whole screen.
	lv_area_t buf_area = {0, 0, buf_dsc->header.w - 1, buf_dsc->header.h - 1};
	if(clip_area_raw == NULL) {
		clip_area_raw = &buf_area;
	}

    lv_area_t clip_area;
    if(!lv_area_intersect(&clip_area, clip_area_raw, &buf_area)) 
        return LV_RESULT_INVALID;

    if((clip_area.x2 - clip_area.x1 <= 0) || (clip_area.y2 - clip_area.y1 <= 0)) 
        return LV_RESULT_INVALID;

    // Check the buffer setting
    if((buf_dsc == NULL) || (buf_dsc->data == NULL) || (buf_dsc->header.w <= 0) || (buf_dsc->header.h <= 0))
    {
        LV_LOG_ERROR("Invalid buffer setting!");
        return LV_RESULT_INVALID;
    }

    //! check the color format
    //! if the color format is not supported, we need to return.
    nema_tex_format_t des_format = lv_ambiq_color_format_map_des(buf_dsc->header.cf);
    uintptr_t start_addr = (uintptr_t)buf_dsc->data;

    if(des_format == COLOR_FORMAT_INVALID  && extend_color_format_support == true)
    {
        if(buf_dsc->header.cf == LV_COLOR_FORMAT_RGB565A8)
        {
            des_format = NEMA_RGB565;
        }
        else if( LV_COLOR_FORMAT_IS_INDEXED(buf_dsc->header.cf))
        {
            uint32_t palette_size;

            switch (buf_dsc->header.cf)
            {
                case LV_COLOR_FORMAT_I1:
                    palette_size = 2;
                    des_format = NEMA_L1;
                    break;
                case LV_COLOR_FORMAT_I2:
                    palette_size = 4;
                    des_format = NEMA_L2;
                    break;
                case LV_COLOR_FORMAT_I4:
                    palette_size = 16;
                    des_format = NEMA_L4;
                    break;
                default:
                    palette_size = 256;
                    des_format = NEMA_L8;
                    break;
            }
            
            start_addr += palette_size * 4;
        }
    }

    if(des_format == COLOR_FORMAT_INVALID)
    {
        LV_LOG_ERROR("Unsupported layer color format!");
        return LV_RESULT_INVALID;
    }

#if NEMAGFX_POWER_SAVE
    uint32_t hal_ret = nemagfx_power_control(AM_HAL_SYSCTRL_WAKE, true);
    if(hal_ret != AM_HAL_STATUS_SUCCESS) {
        LV_LOG_ERROR("Power control failed: %d\r\n", hal_ret);
        return LV_RESULT_INVALID;
    }
#endif

    lv_draw_ambiq_nema_context_lock(unit);

	nema_cmdlist_t *cl = nema_cl_get_bound();
	if (cl == NULL) {
		nema_cl_rewind(&unit->cl);
		nema_cl_bind_sectored_circular(&unit->cl, LV_AMBIQ_COMMAND_LIST_SECTOR);
	}
	else {
		if(cl != &unit->cl) {
			// should never come here
            lv_draw_ambiq_nema_context_unlock(unit);
			LV_LOG_ERROR("Unexpected command list in the context!\r\n");
            return LV_RESULT_INVALID;
		}
	}
	// If a GPU reset has just been executed, we need to clear the GPU context.
	if (nema_get_last_cl_id() < 0 && nema_get_last_submission_id() == 0)
	{
        lv_memset(&unit->des_buffer, 0, sizeof(lv_draw_buf_t));
        lv_memset(&unit->clip_area, 0, sizeof(lv_area_t));
        lv_ambiq_blend_mode_clear(unit);
	}

    // if the buffer is different from the last one, we need to unbind the last one and bind the new one.
	if((buf_dsc->data != unit->des_buffer.data) 
    || (buf_dsc->header.w != unit->des_buffer.header.w) 
    || (buf_dsc->header.h != unit->des_buffer.header.h) 
    || (buf_dsc->header.cf != unit->des_buffer.header.cf)
    || (buf_dsc->header.stride != unit->des_buffer.header.stride)) {
        /* Set target buffer */
        nema_bind_tex(NEMA_TEX0, 
                     start_addr, 
                     buf_dsc->header.w, 
                     buf_dsc->header.h, 
                     des_format, 
                     buf_dsc->header.stride, 0);
		unit->des_buffer = *buf_dsc;
	}



	// if((clip_area.x1 != unit->clip_area.x1) || (clip_area.y1 != unit->clip_area.y1) ||
	// 		(clip_area.x2 != unit->clip_area.x2) || (clip_area.y2 != unit->clip_area.y2)) {
    //     nema_set_clip(clip_area.x1, clip_area.y1, 
    //                   clip_area.x2 - clip_area.x1 + 1, 
    //                   clip_area.y2 - clip_area.y1 + 1);
	// 	unit->clip_area = clip_area;
    // }
    lv_ambiq_clip_area_change(unit, &clip_area, false);

    return LV_RESULT_OK;
}

lv_result_t lv_draw_ambiq_stencil_buffer_adjust(lv_draw_ambiq_unit_t* unit, 
                                    uint32_t width, uint32_t height)
{
    if (unit == NULL) 
        unit = lv_draw_ambiq_get_default_unit();

    lv_draw_buf_t* stencil_buffer = unit->stencil_buffer;

    if((stencil_buffer != NULL) && 
    (stencil_buffer->header.w == width) && 
    (stencil_buffer->header.h == height))
    {
        return LV_RESULT_OK;
    }

    if(stencil_buffer == NULL)
    {
        stencil_buffer = lv_draw_buf_create(width, height, LV_COLOR_FORMAT_A8, 0);
        unit->stencil_buffer = stencil_buffer;
    }
    else
    {
        lv_draw_buf_t* reshaped_buffer = lv_draw_buf_reshape(stencil_buffer, 
                                                             LV_COLOR_FORMAT_A8, 
                                                             width, 
                                                             height, 0);

        if(reshaped_buffer == NULL)
        {
            lv_draw_buf_destroy(unit->stencil_buffer);
            unit->stencil_buffer = lv_draw_buf_create(width, height, LV_COLOR_FORMAT_A8, 0);

        }
        else
        {
            unit->stencil_buffer = reshaped_buffer;
        }
    }

    if(unit->stencil_buffer == NULL)
    {
        LV_LOG_ERROR("Failed to create stencil buffer!");
        return LV_RESULT_INVALID;
    }
    else
    {
        return LV_RESULT_OK;
    }
}   


lv_result_t lv_draw_ambiq_vg_start(uint32_t width, uint32_t hight)
{
#if LV_USE_AMBIQ_VG
	lv_draw_ambiq_unit_t* unit = lv_draw_ambiq_get_default_unit();
		nema_vg_path_clear(unit->vg_path);
		nema_vg_paint_clear(unit->vg_paint);
		nema_vg_reset_global_matrix();
        // clear the blend mode record
        lv_ambiq_blend_mode_clear(unit);

        // adjust the stencil buffer
        uint32_t des_buf_aligned_width = (width + 3) & ~3;
        uint32_t des_buf_aligned_hight = (hight + 3) & ~3;

        lv_result_t result = lv_draw_ambiq_stencil_buffer_adjust(unit, des_buf_aligned_width, des_buf_aligned_hight);
        if(result != LV_RESULT_OK)
        {
            LV_LOG_ERROR("Failed to adjust stencil buffer!");
            return result;
        }

        // bind the destination buffer
        nema_buffer_t stencil_buffer_in_nema_format = {
            .base_virt = unit->stencil_buffer->data,
            .base_phys = (uintptr_t)unit->stencil_buffer->data,
            .fd = 0,
            .size = unit->stencil_buffer->data_size,
        };
        nema_vg_bind_stencil_prealloc(des_buf_aligned_width, 
                                      des_buf_aligned_hight, 
                                      stencil_buffer_in_nema_format);

#endif
}

lv_result_t lv_draw_ambiq_common_end(bool sync)
{
    lv_draw_ambiq_unit_t* unit = lv_draw_ambiq_get_default_unit();

    if(sync) {
        nema_cl_submit(&unit->cl);
        nema_cl_wait(&unit->cl);
        nema_cl_unbind();
    }

    lv_draw_ambiq_nema_context_unlock(unit);

    // Wait for the command list to finish
    // if(sync) {
    //     nema_cl_wait(&unit->cl);
    //     nema_cl_unbind();
    // }

	// Check error
	uint32_t err = nema_get_error();
	if (err != NEMA_ERR_NO_ERROR) {
		LV_LOG_ERROR("NemaGFX error 0x%lx, %s\r\n", err, nema_raster_error_interpret(err));
	}
	err = nema_vg_get_error();
	if (err != NEMA_VG_ERR_NO_ERROR) {
		LV_LOG_ERROR("NemaVG error: 0x%lx, %s\r\n", err, nema_vg_error_interpret(err));
	}

    return LV_RESULT_OK;

}

uint32_t lv_draw_ambiq_bind_image_texture(const lv_draw_buf_t * decoded, uint32_t color_rgba, uint32_t tex_wrap_mode)
{
    uint32_t blend_op_internal = 0;
    lv_image_header_t*  header = &decoded->header; 
    uint32_t lut_size = 0;
    nema_tex_format_t nema_cf = lv_ambiq_color_format_map_src(header->cf);

    // handle look up table(LUT) color format
    if((header->cf == LV_COLOR_FORMAT_I1) ||
    (header->cf == LV_COLOR_FORMAT_I2) ||
    (header->cf == LV_COLOR_FORMAT_I4) ||
    (header->cf == LV_COLOR_FORMAT_I8))
    {
        blend_op_internal |= NEMA_BLOP_LUT;

        
        switch(header->cf) {
            case LV_COLOR_FORMAT_I1:
                lut_size = 2U;
                break;
            case LV_COLOR_FORMAT_I2:
                lut_size = 4U;
                break;
            case LV_COLOR_FORMAT_I4:
                lut_size = 16U;
                break;
            default:
                lut_size = 256U;
                break;
        }

        // LUT/PALETTE
        nema_bind_tex(NEMA_TEX2,
                      (uintptr_t)decoded->data,
                      lut_size,
                      1,
                      NEMA_BGRA8888,
                      0,
                      NEMA_TEX_REPEAT);
    }

    // handle alpha only color format
    bool is_alpha_only = false;
        if((header->cf == LV_COLOR_FORMAT_A1) ||
        (header->cf == LV_COLOR_FORMAT_A2) ||
        (header->cf == LV_COLOR_FORMAT_A4) ||
        (header->cf == LV_COLOR_FORMAT_A8))
        {
            uint32_t tex_color = color_rgba | 0xFF000000;
            nema_set_tex_color(tex_color);
            is_alpha_only = true;
        }
        else
        {
            nema_set_tex_color(0x0);
        }

    // handle mask
    if((header->cf == LV_COLOR_FORMAT_RGB565A8))
    {
        nema_bind_tex(NEMA_TEX3,
                          (uintptr_t)(decoded->data + header->h*header->stride),
                          header->w,
                          header->h,
                          NEMA_A8,
                          -1,
                          NEMA_TEX_BORDER);

        blend_op_internal |= NEMA_BLOP_STENCIL_TXTY;
    }

    uint8_t image_opa = (color_rgba >> 24) & 0xFF;
    if(image_opa < LV_OPA_MAX)
    {
        blend_op_internal |= NEMA_BLOP_MODULATE_A;
        uint32_t global_opa = image_opa;
        nema_set_const_color(global_opa<<24);
    }

    //bind image
    nema_bind_tex(NEMA_TEX1,
                (uintptr_t)decoded->data + lut_size * 4,
                header->w,
                header->h,
                nema_cf,
                header->stride,
                NEMA_FILTER_BL|tex_wrap_mode);
    
    //Set blend op
    return blend_op_internal;
}

uint32_t lv_draw_ambiq_bind_mask_texture(const lv_draw_buf_t * mask_image, bool multiply)
{
    lv_image_header_t*  header = &mask_image->header; 
    nema_tex_format_t nema_cf = lv_ambiq_color_format_map_src(header->cf);

    LV_ASSERT((nema_cf == NEMA_A8) || (nema_cf == NEMA_L8) );

    //bind image
    if(multiply)
    {
        nema_bind_tex(NEMA_TEX2,
                      (uintptr_t)mask_image->data,
                      mask_image->header.w,
                      mask_image->header.h,
                      NEMA_A8,
                      mask_image->header.stride,
                      NEMA_TEX_BORDER);

        lv_ambiq_blend_mode_change(NULL, NEMA_BL_SRC_IN, NEMA_TEX3, NEMA_TEX2, NEMA_NOTEX, false);

        nema_blit_rect(0, 0, mask_image->header.w, mask_image->header.h);

    }
    else
    {
        nema_bind_tex(NEMA_TEX3,
                      (uintptr_t)mask_image->data,
                      mask_image->header.w,
                      mask_image->header.h,
                      NEMA_A8,
                      mask_image->header.stride,
                      NEMA_TEX_BORDER);
    }

    return NEMA_BLOP_STENCIL_TXTY;
}


lv_result_t lv_draw_ambiq_decode_image(const void* src, bool transformed, lv_image_decoder_dsc_t* decoder_dsc, bool is_mask)
{

    lv_image_decoder_args_t args;
    args.premultiply = false;
    args.stride_align = false;
    args.use_indexed = transformed ? false : true;
    args.no_cache = false;
    args.flush_cache = true;

    lv_result_t res = lv_image_decoder_open(decoder_dsc, src, &args);
    if(res != LV_RESULT_OK) {
        LV_LOG_ERROR("Failed to open image");
        return res;
    }

    /*The whole image is not available, we can't draw it with GPU*/
    if(decoder_dsc->decoded == NULL) {
        lv_image_decoder_close(&decoder_dsc);
        LV_LOG_WARN("Ambiq GPU needs to load the whole image to GPU accessible RAM.\n");
        return;
    }

    lv_image_header_t*  header = &decoder_dsc->decoded->header;   

    nema_tex_format_t nema_cf = lv_ambiq_color_format_map_src(header->cf);
    if(nema_cf == COLOR_FORMAT_INVALID)
    {
        lv_image_decoder_close(&decoder_dsc);
        LV_LOG_WARN("GPU failed, not supported color format!");
        return LV_RESULT_INVALID;
    }

    if( is_mask && (header->cf != LV_COLOR_FORMAT_A8 && header->cf != LV_COLOR_FORMAT_L8))
    {
        LV_LOG_WARN("The mask image is not A8/L8 format. We will ignore it.");
        lv_image_decoder_close(&decoder_dsc);
        return LV_RESULT_INVALID;
    }

    return LV_RESULT_OK;

}

#endif