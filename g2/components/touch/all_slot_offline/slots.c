/* Independent0x56a4; composes sealed independent sensor/CDAC/mask source. */
#include "slots.h"
#include "../frame_generation_offline/generator.h"
static uint32_t pad(uint8_t n){return n<32?1u<<n:0;}
void touch_generate_all_slots(uint32_t type,uint8_t *c){
 const uint8_t *common=*(const uint8_t **)c,*i=*(const uint8_t **)(c+8),*pins=*(const uint8_t **)(c+20),*shields=*(const uint8_t **)(c+24);uint32_t project=0;
 for(uint32_t n=0;n<*(const uint16_t *)(common+12);n++)project|=pad(pins[n*8+5]);for(uint32_t n=0;n<common[44];n++)project|=pad(shields[n*8+5]);
 uint32_t mutual=i[117]==2?i[100]:i[117]==5?i[109]:i[99];uint32_t self=i[116]==2?i[100]:i[116]==4?i[107]:i[99];
 const uint8_t *descriptors=*(const uint8_t **)(c+(type==1?52:48));uint32_t *frame=*(uint32_t **)(c+(type==1?44:40));uint32_t count=type==1?4:5;
 for(uint32_t slot=0;slot<count;slot++){
  (void)touch_generate_sensor_closed(type,slot,frame,c);uint32_t id=*(const uint16_t *)(descriptors+slot*4),sensor=*(const uint16_t *)(descriptors+slot*4+2);const uint8_t *w=(const uint8_t *)(*(const uint32_t *)(c+12)+id*144u);uint32_t method=w[122],state=method==1?self:method==2?mutual:i[100];uint32_t *mask=frame+(type==1?5:0);touch_frame_mask(project,state,mask);
  if(common[44]){uint32_t shieldmask=0;for(uint32_t n=0;n<common[44];n++)shieldmask|=pad(shields[n*8+5]);if(method==1)state=i[107];touch_frame_mask(shieldmask,state,mask);}
  if(method==1){const uint8_t *electrode=*(const uint8_t **)(w+8)+sensor*8;const uint8_t *group=*(const uint8_t **)electrode;uint32_t active=0;for(uint32_t n=0;n<electrode[5];n++)active|=pad(group[n*8+5]);touch_frame_mask(active,i[104],mask);}
  frame+=type==1?11:7;
 }
}
