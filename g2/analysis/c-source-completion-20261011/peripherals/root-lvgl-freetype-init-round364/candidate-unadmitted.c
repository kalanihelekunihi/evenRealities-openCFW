
/* Complete lv_freetype_init 4b1b98..4b1c9c (260 bytes).
 * Historical import alias retained; native return value is LV_RESULT 0/1. */
extern void *audio_uart_font_outline_context(void);
extern uint32_t audio_uart_ft_init_freetype_52431c(void *);
extern int32_t audio_uart_ft_node_compare_4b2342(const void *,const void *);
extern uint32_t audio_uart_ft_node_create_4b220a(void *,void *);
extern void audio_uart_ft_node_free_4b2308(void *,void *);
extern const uintptr_t audio_uart_font_cache_backend_vtable[];
static const uintptr_t freetype364_ops[3]={
 (uintptr_t)&audio_uart_ft_node_compare_4b2342,
 (uintptr_t)&audio_uart_ft_node_create_4b220a,
 (uintptr_t)&audio_uart_ft_node_free_4b2308
};
uint32_t audio_uart_lv_init_draw_unit_4b1b98(uint32_t max_glyphs)
{
 static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c";
 static const char name[]="lv_freetype_init";
 if(draw360_word(audio_uart_display_lv_root,448u)!=0u){
  audio_uart_lvgl_log(2u,path,68u,name,"freetype already initialized");return 0u;
 }
 void *allocated=audio_uart_lv_heap_alloc(28u);
 draw360_store(audio_uart_display_lv_root,448u,(uint32_t)(uintptr_t)allocated);
 if(draw360_word(audio_uart_display_lv_root,448u)==0u){
  audio_uart_lvgl_log(3u,path,73u,name,"Asserted at expression: %s (%s)","(&lv_global)->ft_context != NULL","Out of memory");
  for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
 }
 if(draw360_word(audio_uart_display_lv_root,448u)==0u){
  audio_uart_lvgl_log(3u,path,75u,name,"malloc failed for lv_freetype_context_t");return 0u;
 }
 void *context=audio_uart_font_outline_context();
 draw360_store(context,20u,max_glyphs);
 uint32_t error=audio_uart_ft_init_freetype_52431c(context);
 if(error!=0u){audio_uart_lvgl_log(3u,path,87u,name,"FT_Init_FreeType error(0x%x)",error);return 0u;}
 audio_uart_lv_array_init_482b00((uint8_t *)context+4u,8u);
 void *cache=audio_uart_lv_cache_create_4d4cd4((const uint32_t *)(const void *)audio_uart_font_cache_backend_vtable,
 32u,0x7fffffffu,(uint32_t)freetype364_ops[0],(uint32_t)freetype364_ops[1],(uint32_t)freetype364_ops[2]);
 draw360_store(context,24u,(uint32_t)(uintptr_t)cache);
 audio_uart_lv_cache_set_name_4d5114(draw360_pointer(context,24u),"FREETYPE_CACHE_NODE");return 1u;
}
