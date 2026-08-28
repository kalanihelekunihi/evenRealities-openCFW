/* SPDX-License-Identifier: MIT */

#include "../../components/shared/lvgl/runtime_ambiq_gpu_patch_small_raster_candidate.h"

#include <string.h>

enum operation {
    OP_BIND = 1, OP_BLEND, OP_CLIP, OP_COLOR, OP_RECT, OP_RGBA, OP_ARC, OP_POP,
    OP_IDENTITY, OP_MATRIX, OP_TEX_COLOR, OP_CONST_COLOR
};

struct record { uint32_t operation; uint64_t arguments[7]; float values[9]; };
static struct record records[24];
static uint32_t record_count;

static struct record *append(uint32_t op) { records[record_count].operation = op; return &records[record_count++]; }
static void bind(uint8_t t, uintptr_t a, uint32_t w, uint32_t h, uint32_t f, int32_t s, uint32_t m, void *c)
{ struct record *r; (void)c; r=append(OP_BIND); r->arguments[0]=t;r->arguments[1]=a;r->arguments[2]=w;r->arguments[3]=h;r->arguments[4]=f;r->arguments[5]=(uint32_t)s;r->arguments[6]=m; }
static void blend(uint32_t m,uint32_t d,uint32_t f,uint32_t b,void*c)
{ struct record*r;(void)c;r=append(OP_BLEND);r->arguments[0]=m;r->arguments[1]=d;r->arguments[2]=f;r->arguments[3]=b; }
static void clip(int32_t x,int32_t y,uint32_t w,uint32_t h,void*c)
{ struct record*r;(void)c;r=append(OP_CLIP);r->arguments[0]=(uint32_t)x;r->arguments[1]=(uint32_t)y;r->arguments[2]=w;r->arguments[3]=h; }
static void color(uint32_t v,void*c) { (void)c;append(OP_COLOR)->arguments[0]=v; }
static void rect(int32_t x,int32_t y,uint32_t w,uint32_t h,void*c)
{ struct record*r;(void)c;r=append(OP_RECT);r->arguments[0]=(uint32_t)x;r->arguments[1]=(uint32_t)y;r->arguments[2]=w;r->arguments[3]=h; }
static uint32_t rgba(uint8_t r,uint8_t g,uint8_t b,uint8_t a,void*c)
{ uint32_t v=(uint32_t)r<<24|(uint32_t)g<<16|(uint32_t)b<<8|a;struct record*x;(void)c;x=append(OP_RGBA);x->arguments[0]=r;x->arguments[1]=g;x->arguments[2]=b;x->arguments[3]=a;x->arguments[4]=v;return v; }
static void arc(float x,float y,float radius,float width,float start,float end,void*c)
{ struct record*r;(void)c;r=append(OP_ARC);r->values[0]=x;r->values[1]=y;r->values[2]=radius;r->values[3]=width;r->values[4]=start;r->values[5]=end; }
static void pop(void*c) { (void)c;(void)append(OP_POP); }
static void identity(float m[9],void*c)
{ uint32_t i;(void)c;memset(m,0,9*sizeof(float));m[0]=m[4]=m[8]=1.0f;(void)append(OP_IDENTITY);for(i=0;i<9;i++)records[record_count-1].values[i]=m[i]; }
static void matrix(const float m[9],void*c)
{ uint32_t i;struct record*r;(void)c;r=append(OP_MATRIX);for(i=0;i<9;i++)r->values[i]=m[i]; }
static void tex_color(uint32_t v,void*c) { (void)c;append(OP_TEX_COLOR)->arguments[0]=v; }
static void const_color(uint32_t v,void*c) { (void)c;append(OP_CONST_COLOR)->arguments[0]=v; }

static const struct open_cfw_ambiq_gpu_corner_mask_ports corner_ports={0,bind,blend,clip,color,rect,rgba,arc,pop};
static const struct open_cfw_ambiq_gpu_l8_l4_ports convert_ports={0,bind,clip,identity,matrix,blend,tex_color,const_color,rect,pop};

void open_cfw_test_small_corner(uint32_t size,uint32_t sw,uintptr_t buffer)
{ memset(records,0,sizeof(records));record_count=0;open_cfw_ambiq_gpu_create_corner_mask_candidate(size,sw,(uint32_t*)buffer,&corner_ports); }
uint32_t open_cfw_test_small_convert(uint32_t width,uint32_t height,uintptr_t l8,uintptr_t l4)
{ memset(records,0,sizeof(records));record_count=0;return open_cfw_ambiq_gpu_l8_l4_convert_candidate((void*)l8,(void*)l4,width,height,&convert_ports); }
uint32_t open_cfw_test_small_count(void){return record_count;}
uint32_t open_cfw_test_small_operation(uint32_t i){return records[i].operation;}
uint64_t open_cfw_test_small_argument(uint32_t i,uint32_t a){return records[i].arguments[a];}
float open_cfw_test_small_value(uint32_t i,uint32_t v){return records[i].values[v];}
