#include "initialize.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
uint32_t pcm_variant_initialize(void) {
 uint32_t major=W(0x4002000c)&255, rev=W(0x200001e8), date=W(0x2007198c);
 B(0x20074f6e)=major==0x21&&rev==2;
 B(0x20074f6f)=(major==0x21&&(rev==2||rev==3))||(major==0x22&&rev==0);
 uint32_t screened=((date&0x3fe00000)==0x31800000&&((date>>16)&31)>=20&&(date&65535)==0)||(((date>>25)&31)>=25&&(date&65535)==0);
 B(0x20074f70)=(major==0x22&&rev==1)||(major==0x23&&rev==0&&!screened);
 return 0;
}
uint32_t pcm_capture_trim_block(void) {
 if(B(0x20074f63)) return 0;
 W(0x20074280)=(W(0x4002036c)>>20)&63;
 W(0x20074284)=W(0x40020088)&63;
 W(0x20074288)=W(0x4002036c)>>26;
 W(0x2007428c)=(W(0x40020088)>>18)&63;
 W(0x2007426c)=W(0x40020044)&127;
 W(0x20074270)=W(0x4002004c)&127;
 W(0x20074274)=(W(0x40020374)>>29)&3;
 W(0x20074278)=(W(0x40020080)>>10)&15;
 W(0x2007427c)=W(0x40020080)&1023;
 uint32_t major=W(0x4002000c)&255,rev=W(0x200001e8);
 if(((W(0x40021108)>>4)&3)==3&&((major==0x21&&rev!=0)||major>=0x22)) {
  if((major==0x21&&rev>=3)||(major==0x22&&rev==1)||(major==0x23&&rev==0)) W(0x2007427c)+=7;
  else if((major==0x21&&rev<3)||(major==0x22&&rev==0)) W(0x2007427c)+=6;
 }
 W(0x20074290)=W(0x400201b0);
 W(0x20074294)=(W(0x40020344)>>25)&31;
 W(0x20074298)=(W(0x40020344)>>11)&31;
 W(0x2007429c)=(W(0x4002034c)>>25)&31;
 W(0x200742a0)=(W(0x4002034c)>>11)&31;
 W(0x200742a4)=(W(0x40020358)>>8)&31;
 W(0x200742a8)=(W(0x40020354)>>17)&31;
 B(0x20074f63)=1;return 0;
}
uint32_t pcm_early_initialize_noop(void){return 0;}
uint32_t pcm_middle_reset_noop(void){return 0;}
