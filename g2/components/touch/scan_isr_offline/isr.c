/* Independent614c/6462/6530/664c/6780. External callbacks remain explicit.
 * Synthetic ARM32 offline contexts; LP count>0, coherent allocated slots. */
#include "isr.h"
#include "../mode_offline/mode.h"
#include "../scan_preparation_offline/prepare.h"
static uint8_t *ptr(const uint8_t *c,unsigned n){return *(uint8_t *const *)(c+n);}
static uint16_t u16(const uint8_t *c,unsigned n){return *(const uint16_t *)(c+n);}
static volatile uint32_t *hardware(const uint8_t *c){return *(volatile uint32_t **)ptr(ptr(c,0),8);}
static uint32_t enabled(uint32_t id,const uint8_t *c){return id<3 && ((ptr(c,16)[id*60+35]&6u)==6u);}
void touch_clear_busy(uint8_t *c){
 uint8_t *common=ptr(c,4);*(uint32_t *)(common+8)&=~1u;*(uint32_t *)(common+8)&=~128u;
 void (*callback)(void *)=*(void (**)(void *))(ptr(c,8)+4);if(callback)callback(0);
}
void touch_transfer_active(uint32_t start,uint32_t count,uint8_t *c){
 volatile uint32_t *hw=hardware(c);uint32_t *frame=(uint32_t *)(ptr(c,40)+start*28u);volatile uint32_t *buffer=hw+0x2000/4;
 uint32_t end=start+count-1u;
 for(uint32_t slot=start;slot<=end;slot++,frame+=7,buffer+=11){
  const uint8_t *d=ptr(c,48)+slot*4u;uint32_t widget=u16(d,0);if(!enabled(widget,c))continue;
  uint32_t fifo=hw[0x3200/4];uint8_t *w=ptr(c,12)+widget*144u,*sensor=ptr(w,4)+u16(d,2)*10u;
  sensor[6]&=(uint8_t)~4u;if(fifo&0x10000u)sensor[6]|=4u;*(uint16_t *)sensor=(uint16_t)fifo;
  uint32_t coefficient=frame[6]&0xff000000u;
  if(ptr(c,8)[118])frame[6]=coefficient|(buffer[3]&0xffffffu);
  else frame[6]=coefficient|((uint32_t)*(uint16_t *)sensor<<8);
 }
}
void touch_transfer_low_power(uint32_t start,uint32_t count,uint8_t *c){
 uint8_t *common=ptr(c,4);volatile uint32_t *hw=hardware(c);uint16_t *out=(uint16_t *)ptr(c,56);
 uint32_t available=hw[0x3410/4]&0x7ffu;uint32_t sign=hw[0x3414/4];common[28]=(sign&0x80000000u)?1u:3u;
 common[24]=(uint8_t)start;common[25]=(uint8_t)count;common[26]=(uint8_t)(available/count);
 for(unsigned cycle=0;cycle<common[26];cycle++)for(uint32_t slot=start;slot<=start+count-1u;slot++){
  uint32_t value=hw[0x3200/4]&65535u;uint32_t widget=u16(ptr(c,52)+slot*4u,0);if(enabled(widget,c)){
   uint8_t *w=ptr(c,12)+widget*144u;if(w[122]==2 || w[122]==10){uint32_t maximum=u16(ptr(w,0),4);value=maximum>value?maximum-value:0;}
   *out=(uint16_t)value;
  }
  out++; /* Disabled slots reserve history positions without writing. */
 }
}
void touch_scan_slots(uint32_t start,uint32_t count,uint8_t *c){
 uint8_t *i=ptr(c,8);volatile uint32_t *hw=hardware(c);uint32_t slots=count>21u?21u:count;*(uint16_t *)(i+70)=(uint16_t)slots;if(!count)return;
 const uint32_t *frame=(const uint32_t *)(ptr(c,40)+start*28u);volatile uint32_t *out=hw+0x2000/4;
 hw[0]&=0x7fffffffu;
 if(hw[0x180/4]&0x1000000u)hw[0x144/4]=0x10000u;
 else{hw[0x144/4]=1;(void)touch_wait_mrss(441,2,c);}
 for(unsigned j=0;j<slots;j++,frame+=7,out+=11){out[0]=(frame[6]>>24)&15u;out[1]=0;out[2]=0;out[3]=frame[6]&0xffffffu;out[4]=0;for(unsigned k=0;k<6;k++)out[5+k]=frame[k];}
 out[-1]|=4u;hw[3]&=0xfc00ffffu;hw[0]&=0xffff0fffu;hw[2]=(hw[2]&0xfc00ffffu)|(((256u-slots)<<16)&0x3ff0000u);
 void (*callback)(void *)=*(void (**)(void *))i;if(callback && i[97]==1)callback(ptr(c,28));
 if(i[97]==1 && (hw[0x180/4]&0x1000000u))hw[0x144/4]=0x100u;
 hw[0]|=0x80000000u;hw[0x140/4]=1;
}
void touch_scan_isr(uint8_t *c){
 volatile uint32_t *hw=hardware(c);uint8_t *i=ptr(c,8),*common=ptr(c,4);
 uint32_t intr=hw[0x120/4],mask=hw[0x128/4];
 if(!((intr&mask)&0x10000u)){
  if(hw[0x120/4]&1u)*(uint32_t *)(common+8)|=0x400u;
  if(u16(common,22)&1u){touch_transfer_low_power(u16(i,52),u16(i,70),c);common[27]++;}
  hw[0]&=0x7fffffffu;hw[0x120/4]=0x01110011u;(void)hw[0x120/4];hw[0x144/4]=0x100u;touch_clear_busy(c);
 }else{
  hw[0x120/4]=0x01110011u;(void)hw[0x120/4];touch_transfer_active(u16(i,52),u16(i,70),c);
  uint16_t next=(uint16_t)(u16(i,52)+u16(i,70));*(uint16_t *)(i+52)=next;
  if(next<=u16(i,54)){hw[0x70/4]&=0xffff0000u;i[97]=0;touch_scan_slots(next,(uint32_t)u16(i,54)-next+1u,c);}
  else{hw[0]&=0x7fffffffu;hw[0x144/4]=0x100u;*(uint16_t *)(common+4)=(uint16_t)(u16(common,4)+1u);touch_clear_busy(c);}
 }
}
uint32_t touch_prepare_scan_isr_bound(uint8_t *c){uint32_t status=touch_prepare_scan(c);*(void (**)(uint8_t *))(ptr(c,8)+16)=touch_scan_isr;return status;}
/* Stock5fba/5c98 dispatch arguments are ignored except for context.
 * Callback must already be initialized; stock has no null guard. */
void touch_interrupt_dispatch(uint32_t channel,uint8_t *c){
 (void)channel;void (*callback)(uint8_t *)=*(void (**)(uint8_t *))(ptr(c,8)+16);callback(c);
}
void touch_msclp_interrupt(volatile uint32_t *block,uint8_t *c){(void)block;touch_interrupt_dispatch(0,c);}
void touch_project_msclp_irq(void){touch_msclp_interrupt((volatile uint32_t *)0x40290000u,(uint8_t *)0x200004ecu);}
