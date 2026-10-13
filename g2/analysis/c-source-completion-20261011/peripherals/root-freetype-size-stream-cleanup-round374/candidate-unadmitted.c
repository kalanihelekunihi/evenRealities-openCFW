
/* Full destroy_size525832..52586e60bytes. */
void audio_uart_ft_destroy_size_525832(void *memory,void *size,void *driver)
{
 if(draw360_word(size,8u)!=0u){uint32_t callback=draw360_word(size,8u);((void (*)(void *))(uintptr_t)callback)(size);}
 void *clazz=draw360_pointer(driver,12u);
 if(draw360_word(clazz,60u)!=0u){clazz=draw360_pointer(driver,12u);uint32_t callback=draw360_word(clazz,60u);((void (*)(void *))(uintptr_t)callback)(size);}
 audio_uart_font_mem_free(memory,draw360_pointer(size,40u));
 draw360_store(size,40u,0u);audio_uart_font_mem_free(memory,size);
}
/* Full FT_Stream_Close5288ce..5288e018bytes, fresh callback reread. */
void audio_uart_ft_stream_close_5288ce(void *stream)
{
 if(stream!=0 && draw360_word(stream,24u)!=0u){uint32_t callback=draw360_word(stream,24u);((void (*)(void *))(uintptr_t)callback)(stream);}
}
/* Full FT_Stream_Free52502a..52504c34bytes, allocator cached before close. */
void audio_uart_ft_stream_free_52502a(void *stream,uint32_t external)
{
 if(stream==0)return;
 void *memory=draw360_pointer(stream,28u);
 audio_uart_ft_stream_close_5288ce(stream);
 if(external==0u)audio_uart_font_mem_free(memory,stream);
}
