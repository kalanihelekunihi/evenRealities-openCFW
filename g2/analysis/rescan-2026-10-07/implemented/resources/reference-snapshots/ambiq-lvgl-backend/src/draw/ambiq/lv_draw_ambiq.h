/**
 * @file lv_draw_ambiq.h
 *
 */

#ifndef LV_DRAW_AMBIQ_H
#define LV_DRAW_AMBIQ_H

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
#include "../lv_draw_private.h"

/**
 * Initialize the AMBIQ GPU renderer.
 */
void lv_draw_ambiq_init(void);

/**
 * Deinitialize the AMBIQ GPU renderer.
 */
void lv_draw_ambiq_deinit(void);

/**
 * Fill an area using AMBIQ GPU render. Handle gradient and radius.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the rectangle
 */
void lv_draw_ambiq_fill(lv_draw_task_t * t, const lv_draw_fill_dsc_t * dsc, const lv_area_t * coords);

/**
 * Draw border with AMBIQ GPU render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the rectangle
 */
void lv_draw_ambiq_border(lv_draw_task_t * t, const lv_draw_border_dsc_t * dsc, const lv_area_t * coords);

/**
 * Draw box shadow with AMBIQ GPU render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the rectangle for which the box shadow should be drawn
 */
void lv_draw_ambiq_box_shadow(lv_draw_task_t * t, const lv_draw_box_shadow_dsc_t * dsc, const lv_area_t * coords);

/**
 * Draw an image with AMBIQ GPU render. It handles image decoding, tiling, transformations, and recoloring.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the image
 */
void lv_draw_ambiq_image(lv_draw_task_t * t, const lv_draw_image_dsc_t * draw_dsc,
                      const lv_area_t * coords);

/**
 * Draw a label with AMBIQ GPU render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the label
 */
void lv_draw_ambiq_label(lv_draw_task_t * t, const lv_draw_label_dsc_t * dsc, const lv_area_t * coords);

/**
 * Draw a letter with AMBIQ GPU render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the letter
 */
void lv_draw_ambiq_letter(lv_draw_task_t * t, const lv_draw_letter_dsc_t * dsc, const lv_area_t * coords);

/**
 * Draw an arc with AMBIQ GPU render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the arc
 */
void lv_draw_ambiq_arc(lv_draw_task_t * t, const lv_draw_arc_dsc_t * dsc, const lv_area_t * coords);

/**
 * Draw a line with AMBIQ GPU render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 */
void lv_draw_ambiq_line(lv_draw_task_t * t, const lv_draw_line_dsc_t * dsc);

/**
 * Blend a layer with AMBIQ GPU render
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the layer
 */
void lv_draw_ambiq_layer(lv_draw_task_t * t, const lv_draw_image_dsc_t * draw_dsc, const lv_area_t * coords);

/**
 * Draw a triangle with AMBIQ GPU render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 */
void lv_draw_ambiq_triangle(lv_draw_task_t * t, const lv_draw_triangle_dsc_t * dsc);

/**
 * Mask out a rectangle with radius from a current layer
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 * @param coords        the coordinates of the mask
 */
void lv_draw_ambiq_mask_rect(lv_draw_task_t * t, const lv_draw_mask_rect_dsc_t * dsc, const lv_area_t * coords);

#if LV_USE_VECTOR_GRAPHIC
/**
 * Draw vector graphics with AMBIQ render.
 * @param draw_task     pointer to a draw task
 * @param dsc           the draw descriptor
 */
void lv_draw_ambiq_vector(lv_draw_task_t * t, const lv_draw_vector_task_dsc_t * dsc);
#endif

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

#endif /*LV_DRAW_AMBIQ_H*/
