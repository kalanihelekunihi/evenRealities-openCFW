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

