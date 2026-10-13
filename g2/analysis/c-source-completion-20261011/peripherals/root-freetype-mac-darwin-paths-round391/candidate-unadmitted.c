#include <stdint.h>
extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *);
uint32_t audio_uart_ft_mac_rule_52857e(void *library,void *stream,void *name,void *out,void *offset)
{
 (void)stream;
 const char *base=(const char *)name;uint32_t length=0u;while(base[length]!=0)length++;
 int32_t error=0;char *path=(char *)audio_uart_font_mem_alloc(*(void **)library,(int32_t)(length+6u),&error);
 if(error!=0)return (uint32_t)error;
 for(uint32_t i=0;i<length;i++)path[i]=base[i];
 const char suffix[6]="/rsrc";for(uint32_t i=0;i<6u;i++)path[length+i]=suffix[i];
 *(void **)out=path;*(uint32_t *)offset=0u;return 0u;
}
uint32_t audio_uart_ft_mac_rule_5285d4(void *library,void *stream,void *name,void *out,void *offset)
{
 (void)stream;
 const char *base=(const char *)name;uint32_t length=0u;while(base[length]!=0)length++;
 int32_t error=0;char *path=(char *)audio_uart_font_mem_alloc(*(void **)library,(int32_t)(length+18u),&error);
 if(error!=0)return (uint32_t)error;
 for(uint32_t i=0;i<length;i++)path[i]=base[i];
 const char suffix[18]="/..namedfork/rsrc";for(uint32_t i=0;i<18u;i++)path[length+i]=suffix[i];
 *(void **)out=path;*(uint32_t *)offset=0u;return 0u;
}
