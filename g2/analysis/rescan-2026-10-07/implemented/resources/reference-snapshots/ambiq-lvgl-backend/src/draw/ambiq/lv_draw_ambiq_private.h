/**
 * @file lv_draw_ambiq_private.h
 *
 */

#ifndef LV_DRAW_AMBIQ_PRIVATE_H
#define LV_DRAW_AMBIQ_PRIVATE_H

#ifdef __cplusplus
extern "C" {
#endif

/*********************
 *      INCLUDES
 *********************/
#include "../lv_draw_private.h"
#if LV_USE_DRAW_AMBIQ


#include "../../misc/lv_area.h"
#include "../../misc/lv_color.h"
#include "../../display/lv_display.h"
#include "../../osal/lv_os.h"

#include "../lv_draw_vector.h"
#include "../lv_draw_triangle.h"
#include "../lv_draw_label.h"
#include "../lv_draw_image.h"
#include "../lv_draw_line.h"
#include "../lv_draw_arc.h"

#include "../../misc/lv_area_private.h"

#include "am_mcu_apollo.h"

#include "nema_hal.h"
#include "nema_math.h"
#include "nema_core.h"
#include "nema_regs.h"
#include "nema_utils.h"
#include "nema_event.h"
#include "nema_raster.h"
#include "nema_graphics.h"
#include "nema_provisional.h"
#include "nema_interpolators.h"
#include "nema_error.h"
#include "nema_raster.h"
#include "nema_blender.h"
#include "nema_sys_defs.h"
#include "nema_interpolators.h"
#include "nema_matrix3x3.h"
#include "nema_programHW.h"

#if LV_USE_AMBIQ_VG
#include "nema_vg.h"
#include "nema_vg_paint.h"
#include "nema_vg_path.h"
#include "nema_vg_font.h"
#include "nema_vg_tsvg.h"
#include "nema_vg_context.h"
#endif

#include "gpu_patch.h"

/*********************
 *      DEFINES
 *********************/
#define COLOR_FORMAT_INVALID    (0xffffffffUL)

/**********************
 *      TYPEDEFS
 **********************/

typedef struct {
    lv_draw_unit_t base_unit;
    lv_draw_task_t * task_act;
#if LV_USE_OS
    lv_thread_sync_t sync;
    lv_thread_t thread;
    volatile bool inited;
    volatile bool exit_status;
#endif

    //! gradient buffer and small texture buffer
    lv_draw_buf_t* small_texture_buffer;

    //! stencil buffer for VG and other widgets
    lv_draw_buf_t* stencil_buffer;

#if LV_USE_AMBIQ_VG

    //! VG path handle
    NEMA_VG_PATH_HANDLE  vg_path;

    //! VG paint handle
    NEMA_VG_PAINT_HANDLE vg_paint;

    //! VG gradient handle
    NEMA_VG_GRAD_HANDLE vg_grad;
#endif

    //! the current blend mode
    uint32_t blend_mode;

    //! current destination texture
    nema_tex_t dst_tex;
    
    //! current foreground texture
    nema_tex_t fg_tex;
    
    //! current background texture
    nema_tex_t bg_tex;

    //! the destination buffer
    lv_draw_buf_t des_buffer;

    //! the clip area
    lv_area_t clip_area;

    //! mutex for inserted_cl_ll, prevent ll operations from different threads
    lv_mutex_t mutex_nema_context;
    uint32_t nema_context_lock_count;

    //! the command list used for drawing.
    nema_cmdlist_t cl;

    // link list of opened and decoded images
    lv_ll_t opened_img_ll;

    // link list of loaded glyph bitmaps
    lv_ll_t loaded_glyph_ll;

} lv_draw_ambiq_unit_t;

/**********************
 * GLOBAL PROTOTYPES
 **********************/

extern uint32_t nema_enable_aa_flags(uint32_t aa);


/**
 * Initialize the draw buffer handlers, see lv_ambiq_buffer.c.
 */
void lv_draw_ambiq_init_buf_handlers(void);


nema_tex_format_t lv_ambiq_color_format_map_src(lv_color_format_t lvgl_cf);
nema_tex_format_t lv_ambiq_color_format_map_des(lv_color_format_t lvgl_cf);
uint32_t lv_ambiq_color_convert(lv_color_t color, lv_opa_t opa);

void lv_ambiq_set_blend_blit(lv_draw_ambiq_unit_t* unit, uint32_t blending_mode);
void lv_ambiq_set_blend_fill(lv_draw_ambiq_unit_t* unit, uint32_t blending_mode);
void lv_ambiq_blend_mode_change(lv_draw_ambiq_unit_t* unit, uint32_t blending_mode, 
                                 nema_tex_t dst_tex, nema_tex_t fg_tex, nema_tex_t bg_tex, bool force);
void lv_ambiq_blend_mode_clear(lv_draw_ambiq_unit_t* unit);
lv_draw_ambiq_unit_t * lv_draw_ambiq_get_default_unit(void);
uint32_t lv_draw_ambiq_bind_image_texture(const lv_draw_buf_t * decoded, uint32_t color_rgba, uint32_t tex_wrap_mode);
uint32_t lv_draw_ambiq_bind_mask_texture(const lv_draw_buf_t * mask_image, bool multiply);
lv_result_t lv_draw_ambiq_decode_image(const void* src, bool transformed, lv_image_decoder_dsc_t* decoder_dsc, bool is_mask);


void lv_ambiq_clip_area_change(lv_draw_ambiq_unit_t * unit, const lv_area_t* clip_area, bool force);
void lv_ambiq_clip_area_clear(lv_draw_ambiq_unit_t * unit);

lv_result_t lv_draw_ambiq_stencil_buffer_adjust(lv_draw_ambiq_unit_t* unit, uint32_t width, uint32_t height);

lv_result_t lv_draw_ambiq_common_start(const lv_draw_buf_t *buf_dsc, const lv_area_t *clip_area_raw, bool extend_color_format_support);
lv_result_t lv_draw_ambiq_common_end(bool sync);
lv_result_t lv_draw_ambiq_vg_start(uint32_t width, uint32_t hight);

void lv_draw_ambiq_vector_font_init(lv_draw_unit_t * draw_unit);
void lv_draw_ambiq_vector_font(lv_draw_task_t * t, lv_draw_glyph_dsc_t * glyph_draw_dsc);

/***********************
 * GLOBAL VARIABLES
 ***********************/

/**********************
 *      MACROS
 **********************/

#endif /*LV_USE_DRAW_AMBIQ*/

#ifdef __cplusplus
} /*extern "C"*/
#endif

#endif /*LV_DRAW_AMBIQ_PRIVATE_H*/
