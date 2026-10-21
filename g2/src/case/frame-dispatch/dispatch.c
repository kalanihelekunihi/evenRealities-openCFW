/* Independent case085c/9b94 and selected poll fragment6e86..6e9a.
 * Command child handlers and event-clear wrapper remain explicit dependencies. */
#include "dispatch.h"
#define COUNT (*(volatile uint16_t *)0x2000010au)
#define FRAME ((uint8_t *)0x20000974u)
extern void case_legacy_command(uint8_t *,uint16_t);
extern void case_binary_command(uint8_t *,uint16_t,uint32_t);
extern uint32_t case_clear_event(void *,uint32_t);
uint32_t case_hex_digit(uint32_t x){if(x-0x30u<10)return(x-0x30u)&255;if(x-0x61u<6)return(x-0x61u+10)&255;if(x-0x41u<6)return(x-0x41u+10)&255;return 0;}
void case_dispatch_received_frame(void){
 uint32_t n=COUNT;if(n<2)return;
 volatile uint8_t *retry=(volatile uint8_t *)0x20000893u;if(*retry<30)*retry=0;
 if(FRAME[0]==0xde){case_legacy_command(FRAME+1,(uint16_t)(n-1));return;}
 if(case_hex_digit(FRAME[0])==13 && case_hex_digit(FRAME[1])==14){
  for(uint16_t k=1;k<(COUNT>>1);k++)FRAME[k]=(uint8_t)((case_hex_digit(FRAME[2*k])<<4)|case_hex_digit(FRAME[2*k+1]));
  case_legacy_command(FRAME+1,(uint16_t)((COUNT>>1)-1));return;
 }
 n=COUNT;if(n<5 || FRAME[0]!=0x5a || FRAME[1]!=0xa5)return;
 if(FRAME[2]==0x7f){if(FRAME[3]!=n-5)return;case_binary_command(FRAME+4,(uint16_t)(n-4),0);return;}
 if(FRAME[2]==0xcf){uint32_t body=n-6;if(FRAME[3]!=(body&255) || (int32_t)FRAME[4]!=((int32_t)body>>8))return;case_binary_command(FRAME+5,(uint16_t)(n-5),1);}
}
void case_poll_frame_action(uint32_t snapshot){if(snapshot&8){(void)case_clear_event(*(void **)0x200000f0u,8);case_dispatch_received_frame();COUNT=0;}}
