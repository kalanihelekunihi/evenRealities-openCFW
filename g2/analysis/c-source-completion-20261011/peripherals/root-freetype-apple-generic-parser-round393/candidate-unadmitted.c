#include <stdint.h>
extern uint32_t audio_uart_ft_stream_read_ulong_528ba8(void *,int32_t *);
extern uint32_t audio_uart_ft_stream_read_ushort_528b4a(void *,int32_t *);
extern uint32_t audio_uart_ft_stream_skip_528914(void *,int32_t);
uint32_t audio_uart_ft_mac_apple_generic_528720(void *library,void *stream,void *name,uint32_t magic,void *offset_out)
{
 (void)library;(void)name;
 int32_t error=0;
 uint32_t actual=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
 if(error!=0)return (uint32_t)error;
 if(actual!=magic)return 2u;
 (void)audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
 if(error!=0)return (uint32_t)error;
 error=(int32_t)audio_uart_ft_stream_skip_528914(stream,16);
 if(error!=0)return (uint32_t)error;
 uint32_t count=audio_uart_ft_stream_read_ushort_528b4a(stream,&error);
 if(error!=0)return (uint32_t)error;
 if((uint16_t)count==0u)return 2u;
 for(uint32_t i=0;i<(uint16_t)count;i++){
  uint32_t id=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
  if(error!=0)return (uint32_t)error;
  if(id==2u){
   uint32_t offset=audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
   if(error==0){
    (void)audio_uart_ft_stream_read_ulong_528ba8(stream,&error);
    if(error==0){*(uint32_t *)offset_out=offset;return 0u;}
   }
  }else{
   error=(int32_t)audio_uart_ft_stream_skip_528914(stream,8);
   if(error!=0)return (uint32_t)error;
  }
 }
 return 2u;
}
