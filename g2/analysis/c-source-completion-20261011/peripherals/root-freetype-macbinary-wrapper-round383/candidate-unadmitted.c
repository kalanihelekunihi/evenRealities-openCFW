/* Whole resource-fork provider222bytes remains an explicit external boundary. */
extern uint32_t audio_uart_ft_read_mac_resource_5261ac(void *,void *,uint32_t,int32_t,void **);
extern uint32_t audio_uart_ft_read_mac_path_526356(void *,void *,int32_t,void **,const void *);
/* Whole MacBinary reader5262ac..526356170bytes. Native instruction ABI has four args. */
uint32_t audio_uart_ft_read_macbinary_5262ac(void *library,void *stream,int32_t index,void **face)
{
 if(stream==0)return 85u;
 uint32_t error=audio_uart_ft_stream_seek_5288e0(stream,0u);
 if(error!=0u)return error;
 uint8_t header[128];
 error=audio_uart_ft_stream_read_528928(stream,header,128u);
 if(error!=0u)return error;
 if(header[0]!=0u || header[74]!=0u || header[82]!=0u || header[1]==0u || header[1]>=34u || header[63]!=0u || header[(uint32_t)header[1]+2u]!=0u || header[83]>=128u)return 2u;
 uint32_t length=((uint32_t)header[83]<<24u)|((uint32_t)header[84]<<16u)|((uint32_t)header[85]<<8u)|header[86];
 uint32_t offset=((length+127u)&~127u)+128u;
 return audio_uart_ft_read_mac_resource_5261ac(library,stream,offset,index,face);
}
/* Whole Mac fallback526452..5264a684bytes; branch on low byte, preserve full R0 result. */
uint32_t audio_uart_ft_load_mac_face_526452(void *library,void *stream,int32_t index,void **face,const void *args)
{
 uint32_t error=audio_uart_ft_read_macbinary_5262ac(library,stream,index,face);
 if((uint8_t)error==2u)error=audio_uart_ft_read_mac_resource_5261ac(library,stream,0u,index,face);
 if(((uint8_t)error==2u || (uint8_t)error==85u) && ((*(const volatile uint8_t *)args)&4u)!=0u)error=audio_uart_ft_read_mac_path_526356(library,stream,index,face,args);
 return error;
}
