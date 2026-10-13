
/* Whole native lv_draw_buf_clear 48ac40..48ad42, 258 bytes.
 * Pinned LVGL source supplies structure; native instructions govern ABI/read order. */
void audio_uart_lv_draw_buf_clear_48ac40(void *buffer,const void *area)
{
 const volatile uint32_t *b=buffer;
 if(b==0)cache_assert(165u,"lv_draw_buf_clear","draw_buf != NULL");
 const volatile uint32_t *handlers=(const void *)(uintptr_t)b[6];
 if(handlers[6]!=0u){
  uint32_t callback=handlers[6];
  ((void (*)(void *,const void *))(uintptr_t)callback)(buffer,area);return;
 }
 uint32_t stride=(uint16_t)b[2];
 if(area==0){
  void *data=audio_uart_lv_draw_buf_goto_xy_48b2aa(buffer,0u,0u);
  uint32_t height=b[1]>>16u;
  audio_uart_lv_draw_memzero_48aa54(data,stride*height);
  audio_uart_lv_draw_flush_cache_48abb8(buffer,area);return;
 }
 int32_t bounds[4],clipped[4];
 bounds[0]=0;bounds[1]=0;
 bounds[2]=(int32_t)((uint32_t)(uint16_t)b[1]-1u);
 bounds[3]=(int32_t)((b[1]>>16u)-1u);
 if(audio_uart_lv_area_intersect_450bcc(clipped,area,bounds)==0u)return;
 if(audio_uart_lv_area_width_451598(clipped)<1)return;
 if(audio_uart_lv_area_height_4515a4(clipped)<1)return;
 uint32_t data=(uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(buffer,(uint32_t)clipped[0],(uint32_t)clipped[1]);
 uint32_t bits=audio_uart_lv_color_bpp_440f44((uint8_t)(b[0]>>8u));
 uint32_t width=(uint32_t)audio_uart_lv_area_width_451598(clipped);
 uint32_t length=(uint32_t)((int32_t)((uint8_t)bits*width+7u)>>3u);
 int32_t y=clipped[1];
 while(y<=clipped[3]){
  audio_uart_lv_draw_memzero_48aa54((void *)(uintptr_t)data,length);
  data+=stride;y=(int32_t)((uint32_t)y+1u);
 }
 audio_uart_lv_draw_flush_cache_48abb8(buffer,area);
}
