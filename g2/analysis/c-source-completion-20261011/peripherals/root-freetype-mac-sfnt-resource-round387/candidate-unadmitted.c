extern int32_t g2_lfs_memcmp(const void *,const void *,uint32_t);
/* Whole Mac_Read_sfnt_Resource5260a4..5261a8260bytes. R0 is status; scratch R1 is not API output. */
uint32_t audio_uart_ft_mac_read_sfnt_5260a4(void *library,void *stream,void *offsets,int32_t count,int32_t index,void **face)
{
 void *memory=draw360_pointer(library,0u);
 uint32_t normalized=index<0?~(uint32_t)index:(uint32_t)index;
 if((int32_t)normalized>=count)return 1u;
 uint32_t offset=draw360_word(offsets,normalized*4u);
 int32_t error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,offset);
 if(error!=0)return (uint32_t)error;
 uint32_t length=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
 if(error!=0)return (uint32_t)error;
 if((int32_t)length<1)return 1u;
 if(length>=0x01000000u)return 9u;
 uint32_t ps_error=audio_uart_ft_open_ps_sfnt_525d32(library,stream,(int32_t)normalized,0,0,face);
 if(ps_error==0u)return 0u;
 error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,offset+4u);
 if(error!=0)return (uint32_t)error;
 void *buffer=audio_uart_font_mem_alloc(memory,(int32_t)length,&error);
 if(error!=0)return (uint32_t)error;
 error=(int32_t)audio_uart_ft_stream_read_528928(stream,buffer,length);
 if(error!=0){audio_uart_font_mem_free(memory,buffer);return (uint32_t)error;}
 const char *driver="truetype";
 if(length>=5u && g2_lfs_memcmp(buffer,"OTTO",4u)==0)driver="cff";
 return audio_uart_ft_open_face_from_buffer_525b6e(library,buffer,length,0,driver,face);
}
