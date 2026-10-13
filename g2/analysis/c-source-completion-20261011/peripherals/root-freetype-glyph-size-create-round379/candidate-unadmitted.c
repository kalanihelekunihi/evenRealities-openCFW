
/* Complete FT_GlyphLoader_New524b88..524ba8 32bytes; output only written on success. */
uint32_t audio_uart_ft_glyph_loader_new_524b88(void *memory,void **out)
{
 int32_t error;void *loader=audio_uart_font_mem_alloc(memory,96,&error);
 if(error==0){draw360_store(loader,0u,(uint32_t)(uintptr_t)memory);draw360_store(out,0u,(uint32_t)(uintptr_t)loader);}
 return (uint32_t)error;
}
/* Complete ft_glyphslot_init52504c..5250a2 86bytes; typed hidden loader output. */
uint32_t audio_uart_ft_glyph_slot_init_52504c(void *slot)
{
 void *driver=draw360_pointer(draw360_pointer(slot,4u),96u);
 void *clazz=draw360_pointer(driver,12u),*memory=draw360_pointer(driver,8u);
 draw360_store(slot,0u,draw360_word(driver,4u));
 int32_t error;void *internal=audio_uart_font_mem_alloc(memory,40,&error);
 if(error!=0)return (uint32_t)error;
 draw360_store(slot,156u,(uint32_t)(uintptr_t)internal);
 if((draw360_word(draw360_pointer(driver,0u),0u)&512u)==0u)
  error=(int32_t)audio_uart_ft_glyph_loader_new_524b88(memory,draw360_pointer(slot,156u));
 if(error==0 && draw360_word(clazz,64u)!=0u){uint32_t callback=draw360_word(clazz,64u);error=(int32_t)((uint32_t (*)(void *))(uintptr_t)callback)(slot);}
 return (uint32_t)error;
}
/* Complete FT_New_GlyphSlot525386..5253f4110bytes; only allocation failure clears output. */
uint32_t audio_uart_ft_new_glyph_slot_525386(void *face,void **out)
{
 if(face==0)return 35u;
 if(draw360_word(face,96u)==0u)return 6u;
 void *driver=draw360_pointer(face,96u),*clazz=draw360_pointer(driver,12u),*memory=draw360_pointer(driver,8u);
 int32_t error;void *slot=audio_uart_font_mem_alloc(memory,(int32_t)draw360_word(clazz,44u),&error);
 if(error!=0){if(out!=0)draw360_store(out,0u,0u);return (uint32_t)error;}
 draw360_store(slot,4u,(uint32_t)(uintptr_t)face);
 error=(int32_t)audio_uart_ft_glyph_slot_init_52504c(slot);
 if(error!=0){audio_uart_ft_glyph_slot_done_525334(slot);audio_uart_font_mem_free(memory,slot);return (uint32_t)error;}
 draw360_store(slot,8u,draw360_word(face,84u));draw360_store(face,84u,(uint32_t)(uintptr_t)slot);
 if(out!=0)draw360_store(out,0u,(uint32_t)(uintptr_t)slot);
 return (uint32_t)error;
}
/* Complete FT_New_Size52687e..526944198bytes; retained native cleanup scope. */
uint32_t audio_uart_ft_new_size_52687e(void *face,void **out)
{
 if(face==0)return 35u;
 if(out==0)return 6u;
 if(draw360_word(face,96u)==0u)return 34u;
 draw360_store(out,0u,0u);
 void *clazz=draw360_pointer(draw360_pointer(face,96u),12u),*memory=draw360_pointer(face,100u);
 void *node=0;int32_t error;
 void *size=audio_uart_font_mem_alloc(memory,(int32_t)draw360_word(clazz,40u),&error);
 if(error==0)node=audio_uart_font_mem_alloc(memory,12,&error);
 if(error==0){
  draw360_store(size,0u,(uint32_t)(uintptr_t)face);
  void *internal=audio_uart_font_mem_alloc(memory,36,&error);
  if(error==0){
   draw360_store(size,40u,(uint32_t)(uintptr_t)internal);
   if(draw360_word(clazz,56u)!=0u){uint32_t callback=draw360_word(clazz,56u);error=(int32_t)((uint32_t (*)(void *))(uintptr_t)callback)(size);}
   if(error==0){draw360_store(out,0u,(uint32_t)(uintptr_t)size);draw360_store(node,8u,(uint32_t)(uintptr_t)size);audio_uart_ft_list_add_529304((uint8_t *)face+108u,node);}
  }
 }
 if(error!=0){audio_uart_font_mem_free(memory,node);audio_uart_font_mem_free(memory,size);}
 return (uint32_t)error;
}

/* Complete FT_List_Add529304..52932432bytes; tail cached before node writes. */
void audio_uart_ft_list_add_529304(void *list,void *node)
{
 if(list==0 || node==0)return;
 void *tail=draw360_pointer(list,4u);
 draw360_store(node,4u,0u);draw360_store(node,0u,(uint32_t)(uintptr_t)tail);
 if(tail!=0)draw360_store(tail,4u,(uint32_t)(uintptr_t)node);
 else draw360_store(list,0u,(uint32_t)(uintptr_t)node);
 draw360_store(list,4u,(uint32_t)(uintptr_t)node);
}
