/* Independent complete write dispatch for the tested128-byte provider geometry.
 * Extent+address raw modulo32 check is preserved; no physical storage promise. */
#include <stdint.h>
#include "provider.h"
extern uint32_t touch_extended_write(uint32_t,const uint8_t *,uint32_t,uint8_t *);
static uint32_t divide(uint32_t n,uint32_t d) {uint32_t q=0;for(unsigned k=32;k;k--){unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q;}
uint32_t touch_simple_write(uint32_t address,const uint8_t *data,uint32_t size,uint8_t *c) {
 uint32_t step=*(uint32_t *)(c+4),offset=address-divide(address,step)*step;
 uint32_t count=divide(offset+size-1u,step)+1u,cursor=*(uint32_t *)(c+16)+(address-offset);
 uint8_t *scratch=(uint8_t *)0x20000cd4u;
 const uint32_t *p=*(const uint32_t **)(c+28);
 uint32_t (*read)(uint32_t,uint32_t,uint32_t,uint8_t *)=(void *)p[5];
 for(uint32_t i=0;i<count;i++) {
  (void)read(p[0],cursor,step,scratch);
  uint32_t take=step-offset;if(take>size)take=size;
  for(uint32_t j=0;j<take;j++)scratch[offset+j]=data[j];
  uint32_t status=touch_eeprom_program_gate(cursor,scratch,c);if(status)return status;
  *(uint32_t *)(c+24)=cursor;size-=take;data+=take;cursor+=*(uint32_t *)(c+4)&~3u;offset=0;
 }
 return 0;
}
uint32_t touch_eeprom_write(uint32_t address,const uint8_t *data,uint32_t size,uint8_t *c) {
 if(!size || address+size>*(uint32_t *)(c+8) || !data)return 0x093e0000u;
 return c[13]?touch_simple_write(address,data,size,c):touch_extended_write(address,data,size,c);
}
