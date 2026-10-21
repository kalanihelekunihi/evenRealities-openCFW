/* Independent machine0x4070; stable80-byte state and callback-counter units.
 * Uses independently validated speed and software-delay source, no firmware calls. */
#include "gesture.h"
#include "speed.h"
extern void touch_bootstrap_delay(uint32_t);
#define U32(s,n) (*(uint32_t *)((s)+(n)))
static uint32_t magnitude(int32_t x){return x<0?(uint32_t)-x:(uint32_t)x;}
void touch_gesture_attention_rearm(void){
 *(volatile uint32_t *)0x40040444u=2;
 touch_bootstrap_delay(200);
 *(volatile uint32_t *)0x40040440u=2;
}
static void motion(uint8_t *s,int32_t delta,uint32_t counter,uint8_t position,uint8_t release){
 U32(s,40)=counter;s[44]=position;
 s[77]=release?(uint8_t)(s[77]|(delta<0?0x20:0x40)):(delta<0?0x20:0x40);
 s[78]=(uint8_t)magnitude(delta);s[79]=s[74];
}
uint8_t *touch_gesture_step(uint8_t *s,uint32_t active,uint8_t position,uint32_t counter){
 if(!s)return 0;
 if(!*(uint16_t *)s)*(uint16_t *)s=1000;
 s[77]=s[78]=s[79]=0;
 for(unsigned i=0;i<8;i++)s[4+i]=s[12+i];
 s[12]=(uint8_t)active;s[13]=position;U32(s,16)=counter;
 if(active==0){
  if(s[4]){
   s[77]=2;uint32_t elapsed=counter-U32(s,24);U32(s,28)=elapsed;
   int32_t delta=(int32_t)position-s[44];
   if(s[76]==2){s[76]=0;s[33]=s[32]=0;U32(s,36)=counter;}
   else if(s[76]==1){s[76]=0;U32(s,36)=counter;if(magnitude(delta)>14)motion(s,delta,counter,position,1);}
   else if(elapsed>=300)U32(s,36)=counter;
   else {s[33]=1;U32(s,36)=counter;if(s[32]==2){s[77]|=8;s[78]=2;}}
  }else{
   uint32_t elapsed=counter-U32(s,36);
   if((uint8_t)(s[32]-5u)<=4u && elapsed>300){s[32]=0;touch_gesture_attention_rearm();}
   else if(s[33] && elapsed>300){s[33]=0;uint8_t count=s[32];if(count==1 || count>9)s[77]=4;s[78]=count;s[32]=0;}
  }
 }else if(active==1){
  if(s[4]){
   (void)touch_gesture_speed(s,position,counter);uint32_t elapsed=counter-U32(s,24);U32(s,28)=elapsed;
   if(s[76]==0){
    int32_t delta=(int32_t)position-s[21];
    if(magnitude(delta)>24){s[76]=1;s[33]=s[32]=0;if(counter-U32(s,40)>99)motion(s,delta,counter,position,0);}
    else if(elapsed>=*(uint16_t *)s){s[76]=2;s[33]=s[32]=0;s[77]=0x10;}
   }else if(s[76]==1){
    int32_t delta=(int32_t)position-s[44];if(magnitude(delta)>14 && counter-U32(s,40)>99)motion(s,delta,counter,position,0);
   }
  }else{
   for(unsigned i=48;i<76;i++)s[i]=0;
   (void)touch_gesture_speed(s,position,counter);s[76]=0;U32(s,28)=0;
   for(unsigned i=0;i<8;i++)s[20+i]=s[12+i];
   if(s[33] && counter-U32(s,36)<=300){if(s[32]!=255)s[32]++;}else s[32]=1;
   U32(s,40)=counter;s[44]=position;s[77]=1;
  }
 }
 return s+77;
}
