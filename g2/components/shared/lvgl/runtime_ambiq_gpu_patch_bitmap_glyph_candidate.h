/* SPDX-License-Identifier: GPL-3.0-only */
#ifndef OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_BITMAP_GLYPH_CANDIDATE_H
#define OPEN_CFW_RUNTIME_AMBIQ_GPU_PATCH_BITMAP_GLYPH_CANDIDATE_H
#include <stdbool.h>
#include <stdint.h>
typedef float open_cfw_ambiq_gpu_matrix[9];
struct open_cfw_ambiq_gpu_bitmap_glyph {
 const void *bitmap; uint32_t bitmap_width, bitmap_height; int32_t raster_x, raster_y;
 uint32_t raster_width, raster_height, format, color, stride; int32_t rotate_angle, pivot_x, pivot_y;
 bool temporary_used; void *temporary; uint32_t temporary_width, temporary_height, temporary_format, temporary_stride;
};
struct open_cfw_ambiq_gpu_bitmap_glyph_ports {
 void *context;
 void (*bind_source)(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,void*);
 void (*bind_texture)(uint8_t,uintptr_t,uint32_t,uint32_t,uint32_t,int32_t,uint32_t,void*);
 void (*set_blend)(uint32_t,uint32_t,uint32_t,uint32_t,void*);
 void (*set_clip_temp)(int32_t,int32_t,uint32_t,uint32_t,void*);
 void (*matrix_identity)(open_cfw_ambiq_gpu_matrix,void*);
 void (*matrix_translate)(float,float,open_cfw_ambiq_gpu_matrix,void*);
 void (*matrix_rotate)(float,open_cfw_ambiq_gpu_matrix,void*);
 void (*matrix_copy)(open_cfw_ambiq_gpu_matrix,const open_cfw_ambiq_gpu_matrix,void*);
 void (*matrix_invert)(open_cfw_ambiq_gpu_matrix,void*);
 void (*matrix_mul_vec)(const open_cfw_ambiq_gpu_matrix,float*,float*,void*);
 void (*set_matrix)(const open_cfw_ambiq_gpu_matrix,void*);
 void (*set_const_color)(uint32_t,void*);
 void (*set_texture_color)(uint32_t,void*);
 void (*raster_rect)(int32_t,int32_t,uint32_t,uint32_t,void*);
 void (*raster_quad)(float,float,float,float,float,float,float,float,void*);
 void (*set_clip_pop)(void*);
};
void open_cfw_ambiq_gpu_draw_bitmap_glyph_candidate(struct open_cfw_ambiq_gpu_bitmap_glyph *,const struct open_cfw_ambiq_gpu_bitmap_glyph_ports *);
#endif
