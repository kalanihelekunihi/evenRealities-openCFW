/* Independent extended-write orchestration; integrity/history/merge remain
 * explicit guarded provider boundaries. No physical flash implementation. */
#include <stdint.h>
#include "provider.h"
#include "history.h"
static uint32_t div32(uint32_t n,uint32_t d) { uint32_t q=0;for(unsigned k=32;k;k--) {unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q; }
uint8_t touch_row_checksum(const uint8_t *row,uint32_t size) {
 uint8_t crc=0xff; /* stock +1 byte, not conventional +4 */
 for(uint16_t i=0;i!=size-4u;i++) { crc^=row[1u+i];for(unsigned j=0;j<8;j++)crc=(uint8_t)((crc<<1)^((crc&0x80)?0x31u:0)); }
 return crc;
}
static uint32_t next_row(uint32_t address,const uint8_t *context) {
 uint32_t row=*(const uint16_t *)(context+2),base=*(const uint32_t *)(context+16);
 uint32_t end=base+row*(*(const uint16_t *)context)*context[12];
 address+=(row>>2)*4u;return address>=end?base:address;
}
uint32_t touch_extended_write(uint32_t address,const uint8_t *data,uint32_t size,uint8_t *context) {
 uint32_t capacity=*(uint16_t *)(context+22),rows=div32(size-1u,capacity)+1u,sequence[2];
 touch_integrity(sequence,context);
 uint32_t cursor=*(uint32_t *)(context+24),status=0,merge=0;
 uint8_t *scratch=(uint8_t *)0x20000cd4u;uint32_t physical=*(uint16_t *)(context+2);
 for(uint32_t i=0;i<rows;i++) {
  cursor=next_row(cursor,context);sequence[0]++;
  for(uint32_t j=0;j<physical;j++)scratch[j]=0;
  *(uint32_t *)(scratch+4)=sequence[0];*(uint32_t *)(scratch+8)=address;
  uint32_t take=i==rows-1u?size:capacity;*(uint32_t *)(scratch+12)=take;
  for(uint32_t j=0;j<take;j++)scratch[16u+j]=data[j];
  (void)touch_history(scratch,cursor,context);
  merge=touch_merge(scratch,cursor,context);
  *(uint32_t *)scratch=touch_row_checksum(scratch,physical);
  status=touch_eeprom_program_gate(cursor,scratch,context);if(status)break;
  if(context[14]) {
   uint32_t offset=(*(uint16_t *)context)*context[12]*((physical>>2)*4u);
   status=touch_eeprom_program_gate(cursor+offset,scratch,context);if(status)break;
  }
  *(uint32_t *)(context+24)=cursor;size-=capacity;address+=capacity;data+=capacity;
 }
 return status?status:merge;
}
