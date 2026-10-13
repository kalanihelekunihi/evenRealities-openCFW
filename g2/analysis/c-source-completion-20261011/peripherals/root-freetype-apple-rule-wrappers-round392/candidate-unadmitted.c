#include <stdint.h>
extern uint32_t audio_uart_ft_mac_apple_generic_528720(void *,void *,void *,uint32_t,void *);
uint32_t audio_uart_ft_mac_rule_528508(void *library,void *stream,void *name,void *out,void *offset)
{
 *(void **)out=0;
 if(stream==0)return 0x51u;
 return audio_uart_ft_mac_apple_generic_528720(library,stream,name,0x00051607u,offset);
}
uint32_t audio_uart_ft_mac_rule_528524(void *library,void *stream,void *name,void *out,void *offset)
{
 *(void **)out=0;
 if(stream==0)return 0x51u;
 return audio_uart_ft_mac_apple_generic_528720(library,stream,name,0x00051600u,offset);
}
