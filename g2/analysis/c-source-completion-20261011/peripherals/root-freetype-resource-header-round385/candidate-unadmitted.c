static uint32_t ft385_be32(const uint8_t *p)
{return ((uint32_t)p[0]<<24u)|((uint32_t)p[1]<<16u)|((uint32_t)p[2]<<8u)|p[3];}
/* Whole FT_Raccess_Get_HeaderInfo528064..528272526bytes. Output writes persist on later failure. */
uint32_t audio_uart_ft_raccess_header_528064(void *library,void *stream,uint32_t resource,uint32_t *map_out,uint32_t *data_out)
{
 (void)library;uint8_t h[32];int32_t error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,resource);
 if(error!=0)return (uint32_t)error;
 error=(int32_t)audio_uart_ft_stream_read_528928(stream,h,16u);
 if(error!=0)return (uint32_t)error;
 if(h[0]>=128u || h[4]>=128u || h[8]>=128u || h[12]>=128u)return 2u;
 volatile uint32_t *data=data_out;
 *data=ft385_be32(h);
 uint32_t map=ft385_be32(h+4u),data_length=ft385_be32(h+8u),map_length=ft385_be32(h+12u);
 if(map==0u)return 2u;
 if((int32_t)*data<(int32_t)map){if((int32_t)(map-data_length)<(int32_t)*data)return 2u;}
 else if((int32_t)(*data-map_length)<(int32_t)map)return 2u;
 if((int32_t)(0x7fffffffu-data_length)<(int32_t)*data || (int32_t)(0x7fffffffu-map_length)<(int32_t)map || (int32_t)(0x7fffffffu-*data-data_length)<(int32_t)resource || (int32_t)(0x7fffffffu-map-map_length)<(int32_t)resource || draw360_word(stream,4u)<data_length+*data+resource || draw360_word(stream,4u)<map_length+map+resource)return 2u;
 *data=resource+*data;map+=resource;
 error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,map);
 if(error!=0)return (uint32_t)error;
 h[31]=(uint8_t)(h[15]+1u);
 error=(int32_t)audio_uart_ft_stream_read_528928(stream,h+16u,16u);
 if(error!=0)return (uint32_t)error;
 uint32_t all_zero=1u,all_equal=1u;
 for(uint32_t i=0;i<16u;i++){if(h[i+16u]!=0u)all_zero=0u;if(h[i+16u]!=h[i])all_equal=0u;}
 if(all_zero==0u && all_equal==0u)return 2u;
 /* Native BE reader overwrites the skip status through its error output. */
 (void)audio_uart_ft_stream_skip_528914(stream,8);
 int32_t type_offset=(int16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
 if(error!=0)return (uint32_t)error;
 if(type_offset<0)return 2u;
 uint32_t type_position=map+(uint32_t)type_offset;
 error=(int32_t)audio_uart_ft_stream_seek_5288e0(stream,type_position);
 if(error==0)*map_out=type_position;
 return (uint32_t)error;
}
