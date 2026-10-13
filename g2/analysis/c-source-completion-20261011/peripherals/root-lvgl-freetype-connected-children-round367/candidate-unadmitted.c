
/* Native FT_Init_FreeType52431c..52435456bytes. */
extern void *audio_uart_ft_new_memory_5676a0(void);
extern uint32_t audio_uart_ft_new_library_5274b2(void *,void *);
extern void audio_uart_ft_done_memory_5676c6(void *);
extern void audio_uart_ft_add_default_modules_5242fc(void *);
uint32_t audio_uart_ft_init_freetype_52431c(void *out_library)
{
 void *memory=audio_uart_ft_new_memory_5676a0();
 if(memory==0)return 7u;
 uint32_t error=audio_uart_ft_new_library_5274b2(memory,out_library);
 if(error!=0u)audio_uart_ft_done_memory_5676c6(memory);
 else audio_uart_ft_add_default_modules_5242fc(draw360_pointer(out_library,0u));
 (void)draw360_word(out_library,0u);return error;
}
/* Native italic transform4b1fd4..4b201e74bytes. */
extern void audio_uart_ft_set_transform_525444(void *,const int32_t *,const int32_t *);
void audio_uart_ft_italic_transform_4b1fd4(void *face)
{
 if(face==0){
  audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c",216u,"lv_freetype_italic_transform","Asserted at expression: %s (%s)","face != NULL","NULL pointer");
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 int32_t matrix[4]={65536,13930,0,65536};
 audio_uart_ft_set_transform_525444(face,matrix,0);
}
/* Native cache destroy4d4d6a..4d4dca96bytes. */
void audio_uart_lv_cache_destroy_4d4d6a(void *cache,void *user_data)
{
 if(cache==0){
  audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c",72u,"lv_cache_destroy","Asserted at expression: %s (%s)","cache != NULL","NULL pointer");
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 (void)audio_uart_lv_lock_core((uint8_t *)cache+28u);
 void *vtable=draw360_pointer(cache,0u);
 uint32_t callback=draw360_word(vtable,8u);
 ((void (*)(void *,void *))(uintptr_t)callback)(cache,user_data);
 (void)audio_uart_lv_unlock_core((uint8_t *)cache+28u);
 (void)audio_uart_lv_mutex_delete_4d46c2((uint8_t *)cache+28u);
 audio_uart_lv_heap_free(cache);
}
