#include <stdint.h>
typedef uint32_t (*audio_uart_ft_mac_rule_fn)(void *,void *,void *,void *,void *);
typedef struct {audio_uart_ft_mac_rule_fn handler;int32_t type_code;} audio_uart_ft_mac_rule_entry;
#include <stdint.h>
extern uint32_t audio_uart_ft_stream_seek_5288e0(void *,uint32_t);
extern const audio_uart_ft_mac_rule_entry audio_uart_ft_mac_rules_6fac7c[9];
void audio_uart_ft_raccess_guess_528470(void *library,void *stream,const char *base,void **names,uint32_t *offsets,uint32_t *errors)
{
 for(uint32_t i=0;i<9u;i++){
  names[i]=0;
  errors[i]=stream?audio_uart_ft_stream_seek_5288e0(stream,0u):0u;
  if(errors[i]==0u)errors[i]=audio_uart_ft_mac_rules_6fac7c[i].handler(library,stream,(void *)base,&names[i],&offsets[i]);
 }
}
