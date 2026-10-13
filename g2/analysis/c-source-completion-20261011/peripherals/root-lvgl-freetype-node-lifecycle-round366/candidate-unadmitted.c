
/* Full native cache node creation4b220a..4b225c82bytes, no kerning write. */
extern uint32_t audio_uart_ft_new_face_525ade(void *,const char *,int32_t,void **);
extern void audio_uart_ft_italic_transform_4b1fd4(void *);
uint32_t audio_uart_ft_node_create_4b220a(void *node,void *user_data)
{
 (void)user_data;
 void *context=audio_uart_font_outline_context();void *face;
 void *library=draw360_pointer(context,0u);
 const char *pathname=draw360_pointer(node,0u);
 uint32_t error=audio_uart_ft_new_face_525ade(library,pathname,0,&face);
 if(error!=0u){
  audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c",371u,"cache_node_cache_create_cb","FT_New_Face error(0x%x)",error);return 0u;
 }
 draw360_store(node,8u,128u);
 if((*(const volatile uint8_t *)((const uint8_t *)node+4u)&1u)!=0u)audio_uart_ft_italic_transform_4b1fd4(face);
 draw360_store(node,12u,(uint32_t)(uintptr_t)face);
 audio_uart_lv_async_init_4d465c((uint8_t *)node+16u);return 1u;
}
/* Full native node free4b2308..4b2342 58bytes; rereads cache after non-null tests. */
extern uint32_t audio_uart_ft_done_face_526814(void *);
extern void audio_uart_lv_cache_destroy_4d4d6a(void *,void *);
void audio_uart_ft_node_free_4b2308(void *node,void *user_data)
{
 (void)audio_uart_ft_done_face_526814(draw360_pointer(node,12u));
 (void)audio_uart_lv_mutex_delete_4d46c2((uint8_t *)node+16u);
 if(draw360_word(node,24u)!=0u){audio_uart_lv_cache_destroy_4d4d6a(draw360_pointer(node,24u),user_data);draw360_store(node,24u,0u);}
 if(draw360_word(node,28u)!=0u){audio_uart_lv_cache_destroy_4d4d6a(draw360_pointer(node,28u),user_data);draw360_store(node,28u,0u);}
}
