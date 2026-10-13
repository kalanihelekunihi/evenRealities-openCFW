
/* Full native FT_New_Library5274b2..5274f6 68bytes, selected FreeType2.9.1. */
extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *);
uint32_t audio_uart_ft_new_library_5274b2(void *memory,void *out_library)
{
 if(memory==0 || out_library==0)return 6u;
 int32_t error;
 void *library=audio_uart_font_mem_alloc(memory,184,&error);
 if(error!=0)return (uint32_t)error;
 draw360_store(library,0u,(uint32_t)(uintptr_t)memory);
 draw360_store(library,4u,2u);draw360_store(library,8u,9u);draw360_store(library,12u,1u);
 draw360_store(library,180u,1u);
 draw360_store(out_library,0u,(uint32_t)(uintptr_t)library);return 0u;
}
