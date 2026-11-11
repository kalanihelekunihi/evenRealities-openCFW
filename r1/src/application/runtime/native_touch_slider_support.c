#include <stdint.h>
#include "../board/native_battery_memory.h"
extern volatile uint8_t r1_touch_contact_state[100];
extern volatile uint32_t r1_touch_client_bits;
/* Stock 0x59aac. The ring index is a state invariant in 0..2. Each slot
 * holds one byte coordinate and a little-endian uint32 timestamp at +4. */
uint32_t r1_touch_slider_velocity_filter(uint32_t position,uint32_t timestamp)
{
 volatile uint8_t *s=r1_touch_contact_state;
 s[68+8u*s[92]]=(uint8_t)position;
 write32(s+72+8u*s[92],timestamp);
 uint32_t next=(s[92]+1u)%3u;
 s[92]=(uint8_t)next;
 uint32_t count=s[93];
 if(count<3u)s[93]=(uint8_t)++count;
 if(count<2u)return 0;
 uint32_t older=(next+1u)%3u,newer=(next+2u)%3u;
 int32_t delta=(int32_t)s[68+8u*newer]-(int32_t)s[68+8u*older];
 int32_t direction=delta>3?1:delta< -3?-1:0;
 int32_t previous=(int8_t)s[96];
 if(previous && direction){if(previous!=direction)s[95]=0;s[96]=(uint8_t)direction;}
 else if(!previous && direction)s[96]=(uint8_t)direction;
 uint32_t elapsed=read32(s+72+8u*newer)-read32(s+72+8u*older);
 if(!elapsed)return s[95]?s[95]:1u;
 uint32_t distance=(uint32_t)(delta<0?-delta:delta);
 /* The addition wraps in uint32 before the native unsigned division. */
 uint32_t speed=(distance*100u+(elapsed>>1))/elapsed;
 if(speed>255u)speed=255u;
 s[94]=(uint8_t)speed;
 uint32_t smoothed=s[95];
 if(smoothed)speed=(speed*4u+smoothed*6u)/10u;
 s[95]=(uint8_t)speed;
 return (uint8_t)speed;
}
/* Stock 0x92c70. This helper reads the shared sequence timestamp; its
 * caller owns timestamp updates. Do not start a separate time window here. */
uint32_t r1_touch_release_debounce(uint32_t timestamp)
{
 volatile uint8_t *s=r1_touch_contact_state;
 if(!(*(const volatile uint8_t *)&r1_touch_client_bits&2u)){s[49]=0;return 0;}
 if((uint32_t)(timestamp-read32(s+52))>2500u){s[49]=1;return 0;}
 uint8_t count=(uint8_t)(s[49]+1u);s[49]=count;
 if(count>=5u){s[49]=0;return 1;}
 return 0;
}
