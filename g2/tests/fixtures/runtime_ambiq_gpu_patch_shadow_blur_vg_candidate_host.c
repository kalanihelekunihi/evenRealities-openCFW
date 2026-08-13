/* SPDX-License-Identifier: GPL-3.0-only */
#include "../../components/shared/lvgl/runtime_ambiq_gpu_patch_shadow_blur_vg_candidate.h"
#include <string.h>
enum { OP_SNAPSHOT=1,OP_BIND,OP_BLEND,OP_CLIP,OP_COLOR,OP_RECT,OP_FILL_RULE,OP_VG_BLEND,OP_GRAD,OP_TYPE,OP_RADIAL,OP_CIRCLE };
struct rec{uint32_t op;uint64_t a[7];float f[12];};static struct rec r[16];static uint32_t n;static struct rec*add(uint32_t op){r[n].op=op;return&r[n++];}
static void snap(struct open_cfw_ambiq_gpu_vg_context_snapshot*s,void*c){(void)c;add(OP_SNAPSHOT);s->clip_x=3;s->clip_y=4;s->clip_width=50;s->clip_height=60;s->texture_address=0x12345000;s->texture_width=70;s->texture_height=80;s->texture_stride=0x00ab0090;s->texture_format=0x22;}
static void bind(uint8_t t,uintptr_t a,uint32_t w,uint32_t h,uint32_t f,int32_t s,uint32_t m,void*c){struct rec*x;(void)c;x=add(OP_BIND);x->a[0]=t;x->a[1]=a;x->a[2]=w;x->a[3]=h;x->a[4]=f;x->a[5]=(uint32_t)s;x->a[6]=m;}
static void blend(uint32_t m,uint32_t d,uint32_t f,uint32_t b,void*c){struct rec*x;(void)c;x=add(OP_BLEND);x->a[0]=m;x->a[1]=d;x->a[2]=f;x->a[3]=b;}
static void clip(int32_t x,int32_t y,uint32_t w,uint32_t h,void*c){struct rec*z;(void)c;z=add(OP_CLIP);z->a[0]=(uint32_t)x;z->a[1]=(uint32_t)y;z->a[2]=w;z->a[3]=h;}
static void color(uint32_t v,void*c){(void)c;add(OP_COLOR)->a[0]=v;}static void rect(int32_t x,int32_t y,uint32_t w,uint32_t h,void*c){struct rec*z;(void)c;z=add(OP_RECT);z->a[0]=(uint32_t)x;z->a[1]=(uint32_t)y;z->a[2]=w;z->a[3]=h;}
static void fill_rule(uint8_t v,void*c){(void)c;add(OP_FILL_RULE)->a[0]=v;}static void vgblend(uint32_t v,void*c){(void)c;add(OP_VG_BLEND)->a[0]=v;}
static void grad(void*g,int count,const float*s,const struct open_cfw_ambiq_gpu_vg_color*colors,void*c){struct rec*x;uint32_t i;(void)c;x=add(OP_GRAD);x->a[0]=(uintptr_t)g;x->a[1]=(uint32_t)count;x->f[0]=s[0];x->f[1]=s[1];for(i=0;i<2;i++){x->f[2+i*4]=colors[i].red;x->f[3+i*4]=colors[i].green;x->f[4+i*4]=colors[i].blue;x->f[5+i*4]=colors[i].alpha;}}
static void type(void*p,uint8_t v,void*c){struct rec*x;(void)c;x=add(OP_TYPE);x->a[0]=(uintptr_t)p;x->a[1]=v;}
static void radial(void*p,void*g,float x0,float y0,float radius,uint32_t mode,void*c){struct rec*x;(void)c;x=add(OP_RADIAL);x->a[0]=(uintptr_t)p;x->a[1]=(uintptr_t)g;x->a[2]=mode;x->f[0]=x0;x->f[1]=y0;x->f[2]=radius;}
static void circle(float x0,float y0,float radius,const float*m,void*p,void*c){struct rec*x;(void)c;x=add(OP_CIRCLE);x->a[0]=(uintptr_t)m;x->a[1]=(uintptr_t)p;x->f[0]=x0;x->f[1]=y0;x->f[2]=radius;}
static const struct open_cfw_ambiq_gpu_shadow_blur_vg_ports ports={0,snap,bind,blend,clip,color,rect,fill_rule,vgblend,grad,type,radial,circle};
void open_cfw_test_vg_run(float size,float sw,uintptr_t buf,uintptr_t paint,uintptr_t gradp){memset(r,0,sizeof(r));n=0;open_cfw_ambiq_gpu_shadow_blur_corner_vg_candidate(size,sw,(uint32_t*)buf,(void*)paint,(void*)gradp,&ports);}uint32_t open_cfw_test_vg_count(void){return n;}uint32_t open_cfw_test_vg_op(uint32_t i){return r[i].op;}uint64_t open_cfw_test_vg_arg(uint32_t i,uint32_t a){return r[i].a[a];}float open_cfw_test_vg_float(uint32_t i,uint32_t f){return r[i].f[f];}
