#include <stdint.h>
extern void audio_uart_ft_raccess_guess_528470(void *,void *,const char *,void **,uint32_t *,uint32_t *);
extern uint32_t audio_uart_ft_mac_rule_is_3_or_4_5284f4(void *,uint32_t);
extern uint32_t audio_uart_ft_stream_new_524f96(void *,const void *,void **);
extern uint32_t audio_uart_ft_read_mac_resource_5261ac(void *,void *,uint32_t,int32_t,void **);
extern void audio_uart_ft_stream_free_52502a(void *,uint32_t);
extern void audio_uart_font_mem_free(void *,void *);
uint32_t audio_uart_ft_mac_path_search_526356(void *library,void *stream,int32_t index,void **face,const void *args)
{
 void *memory=*(void **)library;
 uint32_t status=2u,seen_special=0u;
 void *names[9];uint32_t offsets[9],errors[9];
 const char *base=*(const char *const *)((const uint8_t *)args+12u);
 audio_uart_ft_raccess_guess_528470(library,stream,base,names,offsets,errors);
 for(uint32_t i=0;i<9u;i++){
  uint32_t special=audio_uart_ft_mac_rule_is_3_or_4_5284f4(library,i);
  if((special==0u || seen_special==0u) && errors[i]==0u){
   uint32_t open_args[8]={0};open_args[0]=4u;
   open_args[3]=(uint32_t)(uintptr_t)(names[i]?names[i]:(void *)base);
   void *opened=0;
   status=audio_uart_ft_stream_new_524f96(library,open_args,&opened);
   if(special!=0u && (status&0xffu)==0x51u)seen_special=1u;
   if(status==0u){
    status=audio_uart_ft_read_mac_resource_5261ac(library,opened,offsets[i],index,face);
    audio_uart_ft_stream_free_52502a(opened,0u);
    if(status==0u)break;
    if(special!=0u)seen_special=1u;
   }
  }
 }
 for(uint32_t i=0;i<9u;i++)if(names[i]!=0)audio_uart_font_mem_free(memory,names[i]);
 return status==0u?0u:2u;
}
