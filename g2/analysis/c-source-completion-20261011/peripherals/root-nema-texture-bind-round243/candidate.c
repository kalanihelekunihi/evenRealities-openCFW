#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_child_52262e(uint32_t);
extern void audio_uart_nema_child_52264e(uint32_t);
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t);
static uint32_t bind243_align4(uint32_t x){x+=3u;return (x+((uint32_t)((int32_t)x>>1)>>30))&~3u;}
static uint32_t bind243_round8(uint32_t x){x+=7u;x+=(uint32_t)((int32_t)x>>2)>>29;return (uint32_t)((int32_t)x>>3);}
/* Native4b1298..4b146c: G2 format strides, context slots and three command pairs. */
void audio_uart_nema_bind_tex_4b1298(uint32_t unit,uint32_t address,uint32_t width,uint32_t height,int32_t format,uint32_t stride,uint32_t flags){
 if((int32_t)unit<0)return;
 uint32_t fmt=(uint32_t)format&127u;
 if(stride==UINT32_MAX){
  stride=width;
  if(flags&16u)stride=bind243_align4(stride);
  if(fmt==18u||fmt==22u||fmt==23u||fmt==78u)stride=bind243_align4(stride);
  if(fmt==76u||fmt==77u){stride+=1u;stride=(stride+(stride>>31))&~1u;}
  switch(fmt){
  case 11u:case 12u:case 39u:case 42u:stride=bind243_round8(stride);break;
  case 18u:stride*=2u;break;
  case 22u:case 23u:case 76u:case 77u:case 78u:stride*=3u;break;
  case 40u:case 43u:case 48u:case 49u:stride=bind243_round8(stride*2u);break;
  case 41u:case 44u:case 52u:case 53u:stride=bind243_round8(stride*4u);break;
  default:{uint32_t factor=4u;switch(fmt){
   case 4u:case 5u:case 6u:case 13u:case 19u:case 29u:case 61u:case 62u:case 63u:case 68u:case 70u:case 71u:case 72u:case 73u:case 74u:case 75u:case 76u:case 77u:factor=2u;break;
   case 7u:case 8u:case 9u:case 12u:case 18u:case 22u:case 23u:case 24u:case 25u:case 26u:case 39u:case 40u:case 48u:case 49u:case 52u:case 53u:case 56u:case 64u:case 65u:case 66u:case 67u:case 69u:case 78u:factor=1u;break;
   case 57u:case 60u:factor=3u;break;
   default:break;}stride*=factor;break;}
  }
 }
 if(unit==0u){
  volatile uint8_t *ctx=(volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
  if(fmt==18u||fmt==22u||fmt==23u){ctx[8]=1;audio_uart_nema_child_52262e(1u);}
  else if(fmt==76u||fmt==77u){ctx[8]=1;audio_uart_nema_child_52264e(1u);}
  else audio_uart_nema_child_52262e(ctx[9]);
 }
 uint32_t offset=unit*24u;
 volatile uint32_t *slot=(volatile uint32_t *)(uintptr_t)(audio_uart_nema_context_cell[0]+offset+56u);
 slot[0]=address;slot[1]=width;slot[2]=height;
 slot[3]=(flags<<16)|((uint32_t)format<<24)|(stride&65535u);
 slot[4]=1;slot[5]=(uint32_t)format;
 volatile uint32_t *packet=audio_uart_nema_cl_get_space_514aec(3u);
 if(packet){
  uint32_t reg=unit*16u;
  packet[0]=reg;packet[1]=address;packet[2]=reg+4u;
  volatile uint32_t *fresh=(volatile uint32_t *)(uintptr_t)(audio_uart_nema_context_cell[0]+offset);
  uint32_t packed=fresh[17];packet[3]=packed;packet[4]=reg+8u;packet[5]=width|(height<<16);
 }
}
