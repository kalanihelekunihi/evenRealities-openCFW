#include <stdint.h>
extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *);
char *audio_uart_ft_mac_path_insert_528842(void *memory,const char *name,const char *insertion)
{
 uint32_t name_len=0u,insert_len=0u;
 while(name[name_len]!=0)name_len++;
 while(insertion[insert_len]!=0)insert_len++;
 int32_t error=0;
 char *result=(char *)audio_uart_font_mem_alloc(memory,(int32_t)(name_len+insert_len+1u),&error);
 if(error!=0)return 0;
 uint32_t slash=0u;uint32_t has_slash=0u;
 for(uint32_t i=0;i<name_len;i++)if(name[i]=='/'){slash=i;has_slash=1u;}
 uint32_t prefix=has_slash?slash+1u:0u;
 for(uint32_t i=0;i<prefix;i++)result[i]=name[i];
 result[prefix]=0;
 uint32_t pos=prefix;
 for(uint32_t i=0;i<insert_len;i++)result[pos++]=insertion[i];
 for(uint32_t i=prefix;i<name_len;i++)result[pos++]=name[i];
 result[pos]=0;
 return result;
}
uint32_t audio_uart_ft_mac_rule_52862c(void *library,void *stream,void *name,void *out,void *offset)
{
 (void)stream;
 char *path=audio_uart_ft_mac_path_insert_528842(*(void **)library,(const char *)name,"resource.frk/");
 if(path==0)return 0x40u;
 *(void **)out=path;*(uint32_t *)offset=0u;return 0u;
}
uint32_t audio_uart_ft_mac_rule_528650(void *library,void *stream,void *name,void *out,void *offset)
{
 (void)stream;
 char *path=audio_uart_ft_mac_path_insert_528842(*(void **)library,(const char *)name,".resource/");
 if(path==0)return 0x40u;
 *(void **)out=path;*(uint32_t *)offset=0u;return 0u;
}
