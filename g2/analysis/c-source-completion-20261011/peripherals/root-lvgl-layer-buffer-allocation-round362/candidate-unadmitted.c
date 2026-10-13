
/* Whole lv_draw_layer_alloc_buf484836..4848b1124bytes andcreatewrapper48affa..48b00f22bytes. */
extern int32_t audio_uart_lv_area_width_451598(const int32_t *);
extern int32_t audio_uart_lv_area_height_4515a4(const int32_t *);
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
extern void *audio_uart_font_bitmap_allocate(void *,uint32_t,uint32_t,uint8_t,uint32_t);
extern void audio_uart_lv_draw_buf_clear_48ac40(void *,const void *);
void *audio_uart_display_surface_alloc(uint32_t width,uint32_t height,uint32_t format,uint32_t stride)
{return audio_uart_font_bitmap_allocate(audio_uart_display_lv_root+200u,width,height,(uint8_t)format,stride);}
void *audio_uart_lv_draw_layer_alloc_buf_484836(void *layer)
{
 if(draw360_word(layer,0u)!=0u)return draw360_pointer(draw360_pointer(layer,0u),16u);
 uint32_t width=(uint32_t)audio_uart_lv_area_width_451598((const int32_t *)((const uint8_t *)layer+4u));
 uint32_t height=(uint32_t)audio_uart_lv_area_height_4515a4((const int32_t *)((const uint8_t *)layer+4u));
 uint32_t stride=audio_uart_font_bitmap_stride(width,*(const volatile uint8_t *)((const uint8_t *)layer+20u));
 uint32_t bytes=stride*height;
 void *buffer=audio_uart_display_surface_alloc(width,height,*(const volatile uint8_t *)((const uint8_t *)layer+20u),0u);
 draw360_store(layer,0u,(uint32_t)(uintptr_t)buffer);
 if(draw360_word(layer,0u)==0u){
  audio_uart_lvgl_log(2u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw.c",471u,"lv_draw_layer_alloc_buf","Allocating layer buffer failed. Try later");return 0;
 }
 draw360_store(audio_uart_display_lv_root,324u,bytes+draw360_word(audio_uart_display_lv_root,324u));
 if(audio_uart_lv_color_has_alpha_440fc4(*(const volatile uint8_t *)((const uint8_t *)layer+20u))!=0u)
  audio_uart_lv_draw_buf_clear_48ac40(draw360_pointer(layer,0u),0);
 return draw360_pointer(draw360_pointer(layer,0u),16u);
}
