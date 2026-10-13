#include <stdint.h>
/* Native Mac resource search rule table at 0x6fac7c, nine 8-byte entries. */
typedef uint32_t (*audio_uart_ft_mac_rule_fn)(void *,void *,void *,void *,void *);
typedef struct { audio_uart_ft_mac_rule_fn handler; int32_t type_code; } audio_uart_ft_mac_rule_entry;
extern uint32_t audio_uart_ft_mac_rule_528508(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_528524(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_528540(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_5285d4(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_52857e(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_52862c(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_528650(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_528674(void *,void *,void *,void *,void *);
extern uint32_t audio_uart_ft_mac_rule_5286b2(void *,void *,void *,void *,void *);
const audio_uart_ft_mac_rule_entry audio_uart_ft_mac_rules_6fac7c[9]={
 {audio_uart_ft_mac_rule_528508,0},
 {audio_uart_ft_mac_rule_528524,1},
 {audio_uart_ft_mac_rule_528540,2},
 {audio_uart_ft_mac_rule_5285d4,3},
 {audio_uart_ft_mac_rule_52857e,4},
 {audio_uart_ft_mac_rule_52862c,5},
 {audio_uart_ft_mac_rule_528650,6},
 {audio_uart_ft_mac_rule_528674,7},
 {audio_uart_ft_mac_rule_5286b2,8}
};
int32_t audio_uart_ft_mac_rule_code_5284de(void *library,uint32_t index)
{
 (void)library;
 return index<9u?(int8_t)audio_uart_ft_mac_rules_6fac7c[index].type_code:-2;
}
uint32_t audio_uart_ft_mac_rule_is_3_or_4_5284f4(void *library,uint32_t index)
{
 uint32_t code=(uint32_t)audio_uart_ft_mac_rule_code_5284de(library,index);
 return code-3u<2u?1u:0u;
}
