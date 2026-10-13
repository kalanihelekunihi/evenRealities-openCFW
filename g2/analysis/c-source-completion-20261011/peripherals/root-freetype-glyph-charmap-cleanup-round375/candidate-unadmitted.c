
/* Full FT_Done_GlyphSlot5253f4..52544480bytes. */
extern void audio_uart_ft_glyph_slot_done_525334(void *);
void audio_uart_ft_done_glyph_slot_5253f4(void *slot)
{
 if(slot==0)return;
 void *driver=draw360_pointer(draw360_pointer(slot,4u),96u);
 void *memory=draw360_pointer(driver,8u);
 void *previous=0,*current=draw360_pointer(draw360_pointer(slot,4u),84u);
 while(current!=0){
  if(current==slot){
   void *next=draw360_pointer(current,8u);
   if(previous==0)draw360_store(draw360_pointer(slot,4u),84u,(uint32_t)(uintptr_t)next);
   else draw360_store(previous,8u,(uint32_t)(uintptr_t)next);
   if(draw360_word(slot,20u)!=0u){uint32_t callback=draw360_word(slot,20u);((void (*)(void *))(uintptr_t)callback)(slot);}
   audio_uart_ft_glyph_slot_done_525334(slot);audio_uart_font_mem_free(memory,slot);return;
  }
  previous=current;current=draw360_pointer(current,8u);
 }
}
/* Full ft_cmap_done_internal526e38..526e5a34bytes. Cached class and memory. */
void audio_uart_ft_cmap_done_internal_526e38(void *cmap)
{
 void *clazz=draw360_pointer(cmap,12u);
 void *face=draw360_pointer(cmap,0u);
 void *memory=draw360_pointer(face,100u);
 if(draw360_word(clazz,8u)!=0u){uint32_t callback=draw360_word(clazz,8u);((void (*)(void *))(uintptr_t)callback)(cmap);}
 audio_uart_font_mem_free(memory,cmap);
}
/* Full destroy_charmaps52586e..5258a8 58bytes. Array/count freshly reread. */
void audio_uart_ft_destroy_charmaps_52586e(void *face,void *memory)
{
 if(face==0)return;
 uint32_t index=0u;
 while((int32_t)index<(int32_t)draw360_word(face,36u)){
  void *array=draw360_pointer(face,40u);
  audio_uart_ft_cmap_done_internal_526e38(draw360_pointer(array,index*4u));
  draw360_store(draw360_pointer(face,40u),index*4u,0u);index+=1u;
 }
 audio_uart_font_mem_free(memory,draw360_pointer(face,40u));
 draw360_store(face,40u,0u);draw360_store(face,36u,0u);
}
