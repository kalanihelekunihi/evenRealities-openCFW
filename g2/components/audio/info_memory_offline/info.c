#include "info.h"
#define W(a) (*(volatile uint32_t *)(a))
extern uint32_t stock_info_read(uint32_t,uint32_t,uint32_t,uint32_t*);
_Static_assert(sizeof(audio_info1_cache)==128,"INFO1 cache layout");
/* Word offsets and spaces, recovered directly from locked instructions. */
static const uint16_t offset[9]={0x480,0x204,0x206,0x208,0x210,0x240,0x24a,0x250,0x245};
static const uint8_t space[9]={5,1,1,3,1,1,1,1,1};
static const uint8_t count[9]={2,1,1,8,1,3,2,12,1};
static const uint8_t destination[9]={4,12,16,20,52,56,72,80,68};
uint32_t audio_info1_populate(void){
 if(!(W(0x400201bc)&8)||!(W(0x40021008)&0x8000000))return 7;
 uint32_t buffer[12];
 for(uint32_t i=0;i<9;i++){
  uint32_t status=stock_info_read(space[i],offset[i],count[i],buffer);
  if(status)return status;
  for(uint32_t j=0;j<count[i];j++)W(0x20071948+destination[i]+4*j)=buffer[j];
 }
 W(0x20071948)=0x1f01600d;return 0;
}
