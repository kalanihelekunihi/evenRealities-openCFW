/* Independent product callback6544, resynca358 and DE predicatebe74. */
#include "frame.h"
#define CUR (*(volatile uint8_t *)0x20000108u)
#define LAST (*(volatile uint8_t *)0x20000109u)
#define COUNT (*(volatile uint16_t *)0x2000010au)
#define FRAME ((volatile uint8_t *)0x20000974u)
#define UART ((case_start_handle *)0x20000e24u)
#define EVENT (*(uint32_t *)0x200000f0u)
extern uint32_t case_bulk_receive(case_start_handle *,uint8_t *,uint16_t,uint32_t);
extern uint32_t case_event_post(uint32_t,uint32_t);
uint32_t case_frame_de_prefix(const uint8_t *p){return (p[0]=='D'||p[0]=='d')&&(p[1]=='E'||p[1]=='e');}
void case_frame_resync(void){if(COUNT>=2 && LAST==0x5a){FRAME[0]=0x5a;COUNT=1;}else COUNT=0;}
void case_frame_callback(case_start_handle *h){
 if((uint32_t)h->Instance!=0x40013800u)return;
 uint16_t n=COUNT;uint8_t ch=CUR;
 if(n==0){if(ch!=0x5a && ch!='D' && ch!='d')goto rearm;}
 if(n<1200){FRAME[n]=ch;COUNT=n+1;LAST=ch;}
 if(ch=='\n' && case_frame_de_prefix((const uint8_t *)FRAME))goto complete;
 n=COUNT;
 if(FRAME[0]!=0x5a){
  if(n>1 && !case_frame_de_prefix((const uint8_t *)FRAME))goto bad;
  if(COUNT>=61)goto bad;
  goto rearm;
 }
 if(n==1)goto rearm;
 if(n==2){if(FRAME[1]!=0xa5)goto bad;goto rearm;}
 if(n==3){if(FRAME[1]!=0xa5 || (FRAME[2]!=0x7f && FRAME[2]!=0xcf))goto bad;goto rearm;}
 if(n==4){
  if(FRAME[2]==0x7f){
   if(case_bulk_receive(UART,(uint8_t *)FRAME+4,FRAME[3],10)==3)goto bad;
   COUNT=(uint16_t)(COUNT+FRAME[3]);LAST=FRAME[(int32_t)COUNT-1];goto tail;
  }
  if(FRAME[2]==0xcf)goto rearm;
  goto bad;
 }
 if(n==5){
  if(FRAME[2]==0xcf){
   uint16_t len=FRAME[3]|((uint16_t)FRAME[4]<<8);
   if(case_bulk_receive(UART,(uint8_t *)FRAME+5,len,20)==3)goto bad;
   COUNT=(uint16_t)(COUNT+len);LAST=FRAME[(int32_t)COUNT-1];goto tail;
  }
  if(FRAME[2]==0x7f)goto rearm;
  goto bad;
 }
 if(FRAME[2]!=0x7f && FRAME[2]!=0xcf)goto bad;
 {
  uint32_t total=FRAME[2]==0x7f?FRAME[3]+5u:(uint16_t)(FRAME[3]|((uint16_t)FRAME[4]<<8))+6u;
  if(n==total)goto complete;
  if(n>total)goto bad;
  goto tail;
 }
complete:
 (void)case_event_post(EVENT,8);goto tail;
bad:
 case_frame_resync();
tail:
 if(COUNT==1200)case_frame_resync();
rearm:
 if(case_uart_start_api(UART,(uint8_t *)0x20000108u,1)!=0)(void)case_event_post(EVENT,0x40);
}
