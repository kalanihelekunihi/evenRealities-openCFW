
/* Entire LVGL draw unit/dispatch/task selector bodies. Unadmitted draft. */
extern void *audio_uart_lv_heap_alloc(uint32_t);
extern uint32_t audio_uart_lv_display_width_44fa7e(void *);
extern uint32_t audio_uart_lv_display_height_44faa8(void *);
extern uint32_t audio_uart_lv_draw_task_independent_4848b2(void *,void *);
static uint32_t draw360_word(const void *p,uint32_t offset)
{return *(const volatile uint32_t *)((const uint8_t *)p+offset);}
static void draw360_store(void *p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)((uint8_t *)p+offset)=value;}
static void *draw360_pointer(const void *p,uint32_t offset)
{return (void *)(uintptr_t)draw360_word(p,offset);}
void *audio_uart_lv_refreshing_display_453604(void)
{return draw360_pointer(audio_uart_display_lv_root,16u);}
void *audio_uart_lv_draw_unit_create_484398(uint32_t size)
{
 void *unit=audio_uart_lv_heap_alloc(size);
 if(unit==0){
  audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw.c",84u,"lv_draw_create_unit","Asserted at expression: %s (%s)","new_unit != NULL","Out of memory");
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 draw360_store(unit,0u,draw360_word(audio_uart_display_lv_root,316u));
 draw360_store(audio_uart_display_lv_root,316u,(uint32_t)(uintptr_t)unit);
 draw360_store(audio_uart_display_lv_root,320u,draw360_word(audio_uart_display_lv_root,320u)+1u);
 draw360_store(unit,8u,draw360_word(audio_uart_display_lv_root,320u));return unit;
}
void audio_uart_lv_draw_dispatch_request_48462e(void)
{(void)audio_uart_lv_thread_sync_signal_4d4724(audio_uart_display_lv_root+328u);}
void *audio_uart_lv_draw_first_available_4849fc(void *layer)
{
 void *task=draw360_pointer(layer,68u);
 if(task!=0 && draw360_word(task,80u)!=1u)return 0;
 return task;
}
void *audio_uart_lv_draw_next_available_484656(void *layer,void *previous,uint32_t unit_id)
{
 if(draw360_word(layer,68u)!=0u){
  uint32_t width=audio_uart_lv_display_width_44fa7e(audio_uart_lv_refreshing_display_453604());
  uint32_t height=audio_uart_lv_display_height_44faa8(audio_uart_lv_refreshing_display_453604());
  void *head=draw360_pointer(layer,68u);
  if(draw360_word(head,80u)!=1u && (int32_t)draw360_word(head,8u)<=0
   && (int32_t)draw360_word(head,16u)>=(int32_t)(width-1u)
   && (int32_t)draw360_word(head,12u)<=0
   && (int32_t)draw360_word(head,20u)>=(int32_t)(height-1u))return 0;
 }
 void *task=previous?draw360_pointer(previous,0u):draw360_pointer(layer,68u);
 for(;task!=0;task=draw360_pointer(task,0u)){
  if(draw360_word(task,80u)==1u
   && (*(const volatile uint8_t *)((const uint8_t *)task+88u)==0u
    || *(const volatile uint8_t *)((const uint8_t *)task+88u)==(uint8_t)unit_id)
   && audio_uart_lv_draw_task_independent_4848b2(layer,task)!=0u)return task;
 }
 return 0;
}
void *audio_uart_lv_draw_get_available_task_48463a(void *layer,void *previous,uint32_t unit_id)
{
 if(draw360_word(audio_uart_display_lv_root,320u)==1u)return audio_uart_lv_draw_first_available_4849fc(layer);
 return audio_uart_lv_draw_next_available_484656(layer,previous,(uint8_t)unit_id);
}
