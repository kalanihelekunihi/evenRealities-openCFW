#include <stdint.h>

/* Whole ft_lookup_PS_in_sfnt_stream525c08..525d32 298bytes. */
extern uint32_t audio_uart_ft_stream_read_ulong_528ba8(void *,int32_t *);
extern uint32_t audio_uart_ft_stream_read_ushort_528b4a(void *,int32_t *);
extern uint32_t audio_uart_ft_stream_skip_528914(void *,int32_t);
uint32_t audio_uart_ft_lookup_ps_sfnt_525c08(void *stream,int32_t index,uint32_t *offset,uint32_t *length,uint8_t *cid)
{
 *offset=0u;*length=0u;*cid=0u;
 int32_t error=index;
 uint32_t tag=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
 if(error!=0)return (uint32_t)error;
 if(tag!=0x74797031u)return 2u;
 uint32_t count=(uint16_t)audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
 if(error!=0)return (uint32_t)error;
 error=(int32_t)audio_uart_ft_stream_skip_528914(stream,6);
 if(error!=0)return (uint32_t)error;
 int32_t found=-1;*cid=0u;
 for(uint32_t i=0;i<count;i++){
  uint32_t table=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
  if(error!=0)return (uint32_t)error;
  error=(int32_t)audio_uart_ft_stream_skip_528914(stream,4);
  if(error!=0)return (uint32_t)error;
  uint32_t value=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);*offset=value;
  if(error!=0)return (uint32_t)error;
  value=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);*length=value;
  if(error!=0)return (uint32_t)error;
  if(table==0x43494420u){found=(int32_t)((uint32_t)found+1u);*offset+=22u;*length-=22u;*cid=1u;if(index<0)return 0u;}
  else if(table==0x54595031u){found=(int32_t)((uint32_t)found+1u);*offset+=24u;*length-=24u;*cid=0u;if(index<0)return 0u;}
  if(index>=0 && found==index)return 0u;
 }
 return 142u;
}
