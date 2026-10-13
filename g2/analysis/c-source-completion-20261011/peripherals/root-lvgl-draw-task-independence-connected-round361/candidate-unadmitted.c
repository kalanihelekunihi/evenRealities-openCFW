
/* Entire native is_independent4848b2..4848e754bytes; pinned lv_draw.c525. */
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
uint32_t audio_uart_lv_draw_task_independent_4848b2(void *layer,void *check)
{
 void *task=draw360_pointer(layer,68u);
 while(task!=0 && task!=check){
  if(draw360_word(task,80u)!=3u){
   int32_t intersection[4];
   if(audio_uart_lv_area_intersect_450bcc(intersection,
    (const int32_t *)((const uint8_t *)task+24u),
    (const int32_t *)((const uint8_t *)check+24u))!=0u)return 0u;
  }
  task=draw360_pointer(task,0u);
 }
 return 1u;
}
