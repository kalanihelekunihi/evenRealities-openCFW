#include <stddef.h>
#include "src/draw/lv_draw_label_private.h"
#include "src/draw/lv_draw_private.h"
#define CHECK(t,f,n) _Static_assert(offsetof(t,f)==n,#t "." #f)
CHECK(lv_draw_label_dsc_t,text,0x1c);
CHECK(lv_draw_label_dsc_t,font,0x20);
CHECK(lv_draw_label_dsc_t,color,0x24);
CHECK(lv_draw_label_dsc_t,line_space,0x28);
CHECK(lv_draw_label_dsc_t,letter_space,0x2c);
CHECK(lv_draw_label_dsc_t,ofs_x,0x30);
CHECK(lv_draw_label_dsc_t,ofs_y,0x34);
CHECK(lv_draw_label_dsc_t,rotation,0x38);
CHECK(lv_draw_label_dsc_t,sel_start,0x3c);
CHECK(lv_draw_label_dsc_t,sel_end,0x40);
CHECK(lv_draw_label_dsc_t,sel_color,0x44);
CHECK(lv_draw_label_dsc_t,sel_bg_color,0x47);
CHECK(lv_draw_label_dsc_t,text_length,0x4c);
CHECK(lv_draw_label_dsc_t,opa,0x50);
CHECK(lv_draw_label_dsc_t,align,0x51);
CHECK(lv_draw_label_dsc_t,bidi_dir,0x52);
CHECK(lv_draw_label_dsc_t,hint,0x58);
CHECK(lv_draw_label_dsc_t,outline_stroke_opa,0x5c);
CHECK(lv_draw_label_dsc_t,outline_stroke_color,0x5d);
CHECK(lv_draw_label_dsc_t,outline_stroke_width,0x60);
CHECK(lv_draw_task_t,clip_area,0x38);
