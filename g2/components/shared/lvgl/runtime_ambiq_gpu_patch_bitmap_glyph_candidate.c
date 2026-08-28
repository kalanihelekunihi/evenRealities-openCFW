/* SPDX-License-Identifier: MIT */
#include "runtime_ambiq_gpu_patch_bitmap_glyph_candidate.h"
#include <stdint.h>
#define NOTEX UINT32_MAX

static uint32_t bits_per_row(uint32_t format,uint32_t width)
{ if(format==0x30U)return width<<1;if(format==0x34U)return width<<2;if(format==0x0CU)return width;return width<<3; }

__attribute__((used,noinline))
void open_cfw_ambiq_gpu_draw_bitmap_glyph_candidate(struct open_cfw_ambiq_gpu_bitmap_glyph *g,const struct open_cfw_ambiq_gpu_bitmap_glyph_ports *p)
{
 uint32_t row_bits=bits_per_row(g->format,g->bitmap_width),stride=g->stride;
 int32_t angle=g->rotate_angle%3600;
 open_cfw_ambiq_gpu_matrix m,inverted;
 if(stride==0U && (row_bits&7U)!=0U && g->bitmap_width*g->bitmap_height<0x7ffU && angle==0){
  p->bind_source((uintptr_t)g->bitmap,g->bitmap_width*g->bitmap_height,1U,g->format,0U,0U,p->context);
  p->matrix_identity(m,p->context);m[1]=(float)g->bitmap_width;m[2]=-(float)(g->raster_y*(int32_t)g->bitmap_width)- (float)g->raster_x-(float)g->bitmap_width*0.5f;
  p->set_matrix(m,p->context);p->raster_rect(g->raster_x,g->raster_y,g->raster_width,g->raster_height,p->context);return;
 }
 if(stride==0U && (row_bits&7U)==0U)stride=row_bits>>3;
 if(stride!=0U){
  p->bind_source((uintptr_t)g->bitmap,g->bitmap_width,g->bitmap_height,g->format,stride,angle!=0,p->context);
  p->matrix_identity(m,p->context);
 }
 else {
  uint32_t current=0;
  p->bind_texture(1U,(uintptr_t)g->temporary,g->temporary_width,g->temporary_height,g->temporary_format,(int32_t)g->temporary_stride,angle!=0,p->context);
  p->set_blend(1U,1U,2U,NOTEX,p->context);p->set_clip_temp(0,0,g->temporary_width,g->temporary_height,p->context);
  while(current<g->bitmap_height){
   uint32_t aligned=current,maximum_rows,remaining,texture_rows,next;int32_t overlap;
   while(aligned>0U && ((row_bits*aligned)&31U)!=0U)--aligned;
   overlap=(int32_t)aligned-(int32_t)current;remaining=g->bitmap_height-aligned;
   maximum_rows=g->bitmap_width==0U?g->bitmap_height:0x7feU/g->bitmap_width;if(maximum_rows==0U)maximum_rows=1U;
   texture_rows=remaining<maximum_rows?remaining:maximum_rows;
   p->matrix_identity(m,p->context);
   p->bind_texture(2U,(uintptr_t)g->bitmap+((row_bits*aligned)>>3),g->bitmap_width*texture_rows,1U,g->format,0,0U,p->context);
   m[1]=(float)g->bitmap_width;m[2]=-(float)(aligned*g->bitmap_width)-(float)g->bitmap_width*0.5f;p->set_matrix(m,p->context);
   next=aligned+texture_rows;p->raster_rect(0,(int32_t)current,g->bitmap_width,(uint32_t)((int32_t)texture_rows+overlap),p->context);current=next;
  }
  p->set_clip_pop(p->context);g->temporary_used=true;
  if((g->color&0xff000000U)==0xff000000U)p->set_blend(0x504U,0U,1U,NOTEX,p->context);
  else {p->set_blend(0x08000504U,0U,1U,NOTEX,p->context);p->set_const_color(g->color,p->context);}
  p->set_texture_color(g->color,p->context);p->matrix_identity(m,p->context);
 }
 if(angle!=0){
  float x0=0,y0=0,x1=(float)g->raster_width,y1=0,x2=x1,y2=(float)g->raster_height,x3=0,y3=y2;
  p->matrix_translate((float)-g->pivot_x,(float)-g->pivot_y,m,p->context);p->matrix_rotate((float)angle/10.0f,m,p->context);p->matrix_translate((float)g->pivot_x,(float)g->pivot_y,m,p->context);p->matrix_translate((float)g->raster_x,(float)g->raster_y,m,p->context);
  p->matrix_copy(inverted,m,p->context);p->matrix_invert(inverted,p->context);p->set_matrix(inverted,p->context);
  p->matrix_mul_vec(m,&x0,&y0,p->context);p->matrix_mul_vec(m,&x1,&y1,p->context);p->matrix_mul_vec(m,&x2,&y2,p->context);p->matrix_mul_vec(m,&x3,&y3,p->context);p->raster_quad(x0,y0,x1,y1,x2,y2,x3,y3,p->context);return;
 }
 p->matrix_translate((float)g->raster_x,(float)g->raster_y,m,p->context);p->matrix_copy(inverted,m,p->context);p->matrix_invert(inverted,p->context);p->set_matrix(inverted,p->context);p->raster_rect(g->raster_x,g->raster_y,g->raster_width,g->raster_height,p->context);
}
