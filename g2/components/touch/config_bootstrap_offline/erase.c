/* Independent erase API0x8ae0. Tested row=sector=128 installed geometry;
 * generic sector>row wrappers are intentionally outside this module. */
#include "bootstrap.h"
#include "provider.h"
#include "history.h"
extern uint8_t touch_row_checksum(const uint8_t *,uint32_t);
static uint32_t div32(uint32_t n,uint32_t d){uint32_t q=0;for(unsigned k=32;k;k--){unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q;}
static uint32_t next(uint32_t a,const uint8_t *c){uint32_t row=*(const uint16_t *)(c+2),base=*(const uint32_t *)(c+16);a+=(row>>2)*4;return a>=base+row*(*(const uint16_t *)c)*c[12]?base:a;}
uint32_t touch_eeprom_erase(uint8_t *c) {
 uint32_t rows=(*(uint16_t *)c)*c[12],physical=*(uint16_t *)(c+2),status=0;
 uint8_t *scratch=(uint8_t *)0x20000cd4u;
 for(uint32_t i=0;i<physical;i++)scratch[i]=0;
 if(c[13]) {
  uint32_t sectors=div32(rows*physical-1u,*(uint32_t *)(c+4))+1u,cursor=*(uint32_t *)(c+16);
  for(uint32_t i=0;i<sectors;i++){uint32_t s=touch_eeprom_program_gate(cursor,scratch,c);if(!status)status=s;cursor+=*(uint32_t *)(c+4)&~3u;}
  return status;
 }
 uint32_t sequence;touch_integrity(&sequence,c);
 uint32_t cursor=next(*(uint32_t *)(c+24),c),offset=rows*((physical>>2)*4u);
 *(uint32_t *)(scratch+4)=sequence+1u;*(uint32_t *)scratch=touch_row_checksum(scratch,physical);
 status=touch_eeprom_program_gate(cursor,scratch,c);
 if(c[14]){uint32_t s=touch_eeprom_program_gate(cursor+offset,scratch,c);if(!status)status=s;}
 if(status)return status;
 *(uint32_t *)(c+24)=cursor;
 for(uint32_t i=0;i<rows-1u;i++) {
  cursor=next(cursor,c);uint32_t s=touch_eeprom_program_gate(cursor,scratch,c);if(!status)status=s;
  if(c[14]){s=touch_eeprom_program_gate(cursor+offset,scratch,c);if(!status)status=s;}
 }
 return status;
}
