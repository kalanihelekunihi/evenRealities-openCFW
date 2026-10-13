
/* Full ft_glyphslot_done525334..52538682bytes. Driver/memory cached before callback. */
extern void audio_uart_font_slot_bitmap_release(void *);
extern void audio_uart_ft_glyph_loader_done_524c1e(void *);
void audio_uart_ft_glyph_slot_done_525334(void *slot)
{
 void *driver=draw360_pointer(draw360_pointer(slot,4u),96u);
 void *clazz=draw360_pointer(driver,12u);
 void *memory=draw360_pointer(driver,8u);
 if(draw360_word(clazz,68u)!=0u){uint32_t callback=draw360_word(clazz,68u);((void (*)(void *))(uintptr_t)callback)(slot);}
 audio_uart_font_slot_bitmap_release(slot);
 if(draw360_word(slot,156u)!=0u){
  void *module_class=draw360_pointer(driver,0u);
  if((draw360_word(module_class,0u)&512u)==0u){
   audio_uart_ft_glyph_loader_done_524c1e(draw360_pointer(draw360_pointer(slot,156u),0u));
   draw360_store(draw360_pointer(slot,156u),0u,0u);
  }
  audio_uart_font_mem_free(memory,draw360_pointer(slot,156u));draw360_store(slot,156u,0u);
 }
}

/* Full FT_GlyphLoader_Done524c1e..524c3a28bytes; memory cached before reset. */
extern void audio_uart_ft_glyph_loader_reset_524bc4(void *);
void audio_uart_ft_glyph_loader_done_524c1e(void *loader)
{
 if(loader==0)return;
 void *memory=draw360_pointer(loader,0u);
 audio_uart_ft_glyph_loader_reset_524bc4(loader);
 audio_uart_font_mem_free(memory,loader);
}

/* Whole FT_GlyphLoader_Rewind524ba8..524bc4 28bytes. */
void audio_uart_ft_glyph_loader_rewind_524ba8(void *loader)
{
 uint8_t *base=(uint8_t *)loader+20u;
 *(volatile uint16_t *)(void *)(base+2u)=0u;
 *(volatile uint16_t *)(void *)base=0u;
 draw360_store(base,28u,0u);
 audio_uart_checksum_copy((uint8_t *)loader+56u,base,36u);
}
/* Whole FT_GlyphLoader_Reset524bc4..524c1e90bytes; fresh each allocation read. */
void audio_uart_ft_glyph_loader_reset_524bc4(void *loader)
{
 void *memory=draw360_pointer(loader,0u);
 static const uint8_t offsets[5]={24u,28u,32u,40u,52u};
 for(uint32_t i=0;i<5u;i++){
  audio_uart_font_mem_free(memory,draw360_pointer(loader,offsets[i]));
  draw360_store(loader,offsets[i],0u);
 }
 draw360_store(loader,44u,0u);draw360_store(loader,4u,0u);
 draw360_store(loader,8u,0u);draw360_store(loader,12u,0u);
 audio_uart_ft_glyph_loader_rewind_524ba8(loader);
}
