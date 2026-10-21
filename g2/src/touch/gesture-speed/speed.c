/* Independent helper0x3efc. State80 bytes, valid ringindex0..2,count0..3.
 * Counter units are delivered SysTick callbacks; no physical speed units claim. */
#include "speed.h"
static uint32_t divide(uint32_t n,uint32_t d){uint32_t q=0;for(unsigned k=32;k;k--){unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q;}
uint32_t touch_gesture_speed(uint8_t *s,uint8_t position,uint32_t counter){
 if(!s)return 0;
 uint32_t index=s[72];s[48+index*8]=position;*(uint32_t *)(s+52+index*8)=counter;
 uint32_t next=index+1;if(next>=3)next-=3;s[72]=(uint8_t)next;
 if(s[73]<3)s[73]++;
 if(s[73]<=1)return 0;
 uint32_t previous=next+1;if(previous>=3)previous-=3;
 uint32_t newest=next+2;if(newest>=3)newest-=3;
 int32_t delta=(int32_t)s[48+newest*8]-(int32_t)s[48+previous*8];
 int32_t direction=delta>3?1:delta < -3?-1:0;
 int32_t prior=(int8_t)s[75];
 if(prior && direction && prior!=direction)s[74]=0;
 if(direction)s[75]=(uint8_t)direction;
 uint32_t current=*(uint32_t *)(s+52+newest*8),old=*(uint32_t *)(s+52+previous*8),elapsed=current-old;
 if(current==old)return s[74]?s[74]:1;
 uint32_t magnitude=delta<0?(uint32_t)-delta:(uint32_t)delta;
 uint32_t speed=divide(magnitude*100u+(elapsed>>1),elapsed);if(speed>255)speed=255;
 s[74]=s[74]?(uint8_t)divide(speed*4u+s[74]*6u,10u):(uint8_t)speed;
 return s[74];
}
