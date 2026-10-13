/* Full native440a3c..440c2d/440c2e..440d47, pinned lv_obj_pos.c1077..1230.
 * Native wrap, repeated LV_MAX margin fetches, scroll mutation and child order retained. */
#include <stdint.h>
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern uint32_t audio_uart_lv_layout_positioned_43f612(void *);
extern int32_t audio_uart_lv_self_width_43ff44(void *);
extern int32_t audio_uart_lv_self_height_43ff5e(void *);
extern int32_t audio_uart_lv_style_x_43eee2(void *,uint32_t);
extern int32_t audio_uart_lv_style_y_43eeec(void *,uint32_t);
extern uint8_t audio_uart_lv_style_align_43eef6(void *,uint32_t);
extern uint8_t audio_uart_lv_style_base_dir_43efba(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_right_43eff4(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_bottom_43f050(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_left_43ef84(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_right_43ef8e(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_top_43ef70(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_bottom_43ef7a(void *,uint32_t);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
static uint32_t lv322_read(const void *p,uint32_t offset){return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void lv322_write(void *p,uint32_t offset,uint32_t value){*(volatile uint32_t *)((uint8_t *)p+offset)=value;}
static int32_t lv322_add(int32_t a,int32_t b){return (int32_t)((uint32_t)a+(uint32_t)b);}
static int32_t lv322_extent(uint32_t end,uint32_t start){return (int32_t)(end-start+1u);}
static void *lv322_child(void *o,uint32_t i){uint32_t spec=lv322_read(o,8);uint32_t children=lv322_read((void *)(uintptr_t)spec,0);return (void *)(uintptr_t)lv322_read((void *)(uintptr_t)children,i*4u);}
int32_t audio_uart_lv_calc_content_width_440a3c(void *object)
{
 int32_t old_scroll=audio_uart_lv_obj_x_44e486(object);
 if(lv322_read(object,8))lv322_write((void *)(uintptr_t)lv322_read(object,8),32,0);
 int32_t right=audio_uart_lv_style_pad_right_43eff4(object,0);
 int32_t left=audio_uart_lv_style_pad_left_43efc6(object,0,0,0);
 int32_t self=lv322_add(lv322_add(audio_uart_lv_self_width_43ff44(object),left),right);
 int32_t result=(int32_t)0xe0000001u;uint32_t count=audio_uart_lv_child_count_44ddea(object);
 uint8_t rtl=audio_uart_lv_style_base_dir_43efba(object,0)==1;
 for(uint32_t i=0;i<count;i++){
  int32_t tmp=(int32_t)0xe0000001u;void *child=lv322_child(object,i);
  if(audio_uart_lv_obj_has_flag_any_43e11c(child,0x40001u))continue;
  uint32_t positioned=audio_uart_lv_layout_positioned_43f612(child);
  uint8_t align=0;if(!positioned)align=audio_uart_lv_style_align_43eef6(child,0);
  if(positioned || (rtl?(align==0 || align==3 || align==6 || align==8):(align==0 || align==1 || align==4 || align==7))){
   tmp=rtl?lv322_extent(lv322_read(object,28),lv322_read(child,20)):lv322_extent(lv322_read(child,28),lv322_read(object,20));
  }else if(audio_uart_lv_style_x_43eee2(child,0)==0){
   tmp=lv322_add(audio_uart_lv_area_width_451598((uint8_t *)child+20),rtl?right:left);
   tmp=lv322_add(tmp,rtl?audio_uart_lv_style_margin_left_43ef84(child,0):audio_uart_lv_style_margin_right_43ef8e(child,0));
  }
  int32_t margin=rtl?audio_uart_lv_style_margin_left_43ef84(child,0):audio_uart_lv_style_margin_right_43ef8e(child,0);
  if(lv322_add(tmp,margin)>=result){
   margin=rtl?audio_uart_lv_style_margin_left_43ef84(child,0):audio_uart_lv_style_margin_right_43ef8e(child,0);
   result=lv322_add(tmp,margin);
  }
 }
 if(result!=(int32_t)0xe0000001u)result=lv322_add(result,rtl?left:right);
 if(lv322_read(object,8))lv322_write((void *)(uintptr_t)lv322_read(object,8),32,0u-(uint32_t)old_scroll);
 if(result==(int32_t)0xe0000001u)return self;
 return result>self?result:self;
}
int32_t audio_uart_lv_calc_content_height_440c2e(void *object)
{
 int32_t old_scroll=audio_uart_lv_obj_y_44e498(object);
 if(lv322_read(object,8))lv322_write((void *)(uintptr_t)lv322_read(object,8),36,0);
 int32_t top=audio_uart_lv_style_pad_top_43f022(object,0,0,0);
 int32_t bottom=audio_uart_lv_style_pad_bottom_43f050(object,0);
 int32_t self=lv322_add(lv322_add(audio_uart_lv_self_height_43ff5e(object),top),bottom);
 int32_t result=(int32_t)0xe0000001u;uint32_t count=audio_uart_lv_child_count_44ddea(object);
 for(uint32_t i=0;i<count;i++){
  int32_t tmp=(int32_t)0xe0000001u;void *child=lv322_child(object,i);
  if(audio_uart_lv_obj_has_flag_any_43e11c(child,0x40001u))continue;
  uint32_t positioned=audio_uart_lv_layout_positioned_43f612(child);
  uint8_t align=0;if(!positioned)align=audio_uart_lv_style_align_43eef6(child,0);
  if(positioned || align<=3){tmp=lv322_extent(lv322_read(child,32),lv322_read(object,24));}
  else if(audio_uart_lv_style_y_43eeec(child,0)==0){
   tmp=lv322_add(audio_uart_lv_area_height_4515a4((uint8_t *)child+20),top);
   tmp=lv322_add(tmp,audio_uart_lv_style_margin_top_43ef70(child,0));
  }
  int32_t margin=audio_uart_lv_style_margin_bottom_43ef7a(child,0);
  if(lv322_add(tmp,margin)>=result)result=lv322_add(tmp,audio_uart_lv_style_margin_bottom_43ef7a(child,0));
 }
 if(lv322_read(object,8))lv322_write((void *)(uintptr_t)lv322_read(object,8),36,0u-(uint32_t)old_scroll);
 if(result==(int32_t)0xe0000001u)return self;
 int32_t combined=lv322_add(result,bottom);return combined>=self?combined:self;
}
