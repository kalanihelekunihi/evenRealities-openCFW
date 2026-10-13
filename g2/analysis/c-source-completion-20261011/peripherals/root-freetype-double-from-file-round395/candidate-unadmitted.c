#include <stdint.h>
extern uint32_t audio_uart_ft_stream_new_524f96(void *,const void *,void **);
extern uint32_t audio_uart_ft_mac_rule_528508(void *,void *,void *,void *,void *);
extern void audio_uart_ft_stream_free_52502a(void *,uint32_t);
uint32_t audio_uart_ft_mac_double_from_file_528802(void *library,const char *path,void *offset)
{
 uint32_t args[8]={0};args[0]=4u;args[3]=(uint32_t)(uintptr_t)path;
 void *stream=0;void *unused=0;
 uint32_t error=audio_uart_ft_stream_new_524f96(library,args,&stream);
 if(error==0u){
  error=audio_uart_ft_mac_rule_528508(library,stream,(void *)path,&unused,offset);
  audio_uart_ft_stream_free_52502a(stream,0u);
 }
 return error;
}
