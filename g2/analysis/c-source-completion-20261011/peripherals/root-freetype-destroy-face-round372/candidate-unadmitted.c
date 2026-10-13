
/* Whole destroy_face5258a8..525936142bytes, FreeType2.9.1. */
extern void audio_uart_ft_done_glyph_slot_5253f4(void *);
extern void audio_uart_ft_destroy_size_525832(void *,void *,void *);
extern void audio_uart_ft_list_finalize_529378(void *,void (*)(void *,void *,void *),void *,void *);
extern void audio_uart_ft_destroy_charmaps_52586e(void *,void *);
extern void audio_uart_ft_stream_free_52502a(void *,uint32_t);
void audio_uart_ft_destroy_face_5258a8(void *memory,void *face,void *driver)
{
 void *clazz=draw360_pointer(driver,12u);
 if(draw360_word(face,120u)!=0u){
  void *data=draw360_pointer(face,116u);
  uint32_t callback=draw360_word(face,120u);
  ((void (*)(void *))(uintptr_t)callback)(data);
 }
 while(draw360_word(face,84u)!=0u)audio_uart_ft_done_glyph_slot_5253f4(draw360_pointer(face,84u));
 audio_uart_ft_list_finalize_529378((uint8_t *)face+108u,audio_uart_ft_destroy_size_525832,memory,driver);
 draw360_store(face,88u,0u);
 if(draw360_word(face,48u)!=0u){uint32_t callback=draw360_word(face,48u);((void (*)(void *))(uintptr_t)callback)(face);}
 audio_uart_ft_destroy_charmaps_52586e(face,memory);
 if(draw360_word(clazz,52u)!=0u){uint32_t callback=draw360_word(clazz,52u);((void (*)(void *))(uintptr_t)callback)(face);}
 uint32_t external=(draw360_word(face,8u)>>10u)&1u;
 audio_uart_ft_stream_free_52502a(draw360_pointer(face,104u),external);
 draw360_store(face,104u,0u);
 if(draw360_word(face,128u)!=0u){audio_uart_font_mem_free(memory,draw360_pointer(face,128u));draw360_store(face,128u,0u);}
 audio_uart_font_mem_free(memory,face);
}
