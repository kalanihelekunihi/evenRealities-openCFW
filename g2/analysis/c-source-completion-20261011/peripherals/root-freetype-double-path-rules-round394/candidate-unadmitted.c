#include <stdint.h>
extern char *audio_uart_ft_mac_path_insert_528842(void *,const char *,const char *);
extern void audio_uart_font_mem_free(void *,void *);
extern uint32_t audio_uart_ft_mac_double_from_file_528802(void *,const char *,void *);
uint32_t audio_uart_ft_mac_rule_528540(void *library,void *stream,void *name,void *out,void *offset)
{
 (void)stream;void *memory=*(void **)library;
 char *path=audio_uart_ft_mac_path_insert_528842(memory,(const char *)name,"._");
 if(path==0)return 0x40u;
 uint32_t error=audio_uart_ft_mac_double_from_file_528802(library,path,offset);
 if(error==0u)*(void **)out=path;else audio_uart_font_mem_free(memory,path);
 return error;
}
uint32_t audio_uart_ft_mac_rule_528674(void *library,void *stream,void *name,void *out,void *offset)
{
 (void)stream;void *memory=*(void **)library;
 char *path=audio_uart_ft_mac_path_insert_528842(memory,(const char *)name,"%");
 if(path==0)return 0x40u;
 uint32_t error=audio_uart_ft_mac_double_from_file_528802(library,path,offset);
 if(error==0u)*(void **)out=path;else audio_uart_font_mem_free(memory,path);
 return error;
}
uint32_t audio_uart_ft_mac_rule_5286b2(void *library,void *stream,void *name,void *out,void *offset)
{
 (void)stream;void *memory=*(void **)library;
 char *path=audio_uart_ft_mac_path_insert_528842(memory,(const char *)name,".AppleDouble/");
 if(path==0)return 0x40u;
 uint32_t error=audio_uart_ft_mac_double_from_file_528802(library,path,offset);
 if(error==0u)*(void **)out=path;else audio_uart_font_mem_free(memory,path);
 return error;
}
