/* Independent reconstruction of actual checksum/recovery/history instructions.
 * Physical storage and SROM are supplied by the offline guest model. */
#include <stdint.h>
#include "history.h"
extern uint8_t touch_row_checksum(const uint8_t *,uint32_t);
static uint16_t h(const uint8_t *c,unsigned o) {return *(const uint16_t *)(c+o);}
static uint32_t w(const uint8_t *c,unsigned o) {return *(const uint32_t *)(c+o);}
static uint32_t stride(const uint8_t *c) {return (h(c,2)>>2)*4u;}
static uint32_t region(const uint8_t *c) {return h(c,0)*c[12]*stride(c);}
static uint32_t crc_check(uint32_t row,uint32_t size) {return w((const uint8_t *)row,0)==touch_row_checksum((const uint8_t *)row,size)?0:0x093e0001u;}
static uint32_t seq(uint32_t row) {return w((const uint8_t *)row,4);}
static uint32_t next(uint32_t row,const uint8_t *c) {row+=stride(c);return row>=w(c,16)+h(c,2)*h(c,0)*c[12]?w(c,16):row;}
static uint32_t previous_block(uint32_t row,const uint8_t *c) {
 if(c[12]>1) {uint32_t block=h(c,0)*h(c,2);row=row<w(c,16)+block?row+(c[12]-1u)*block:row-block;}
 return row;
}
static uint32_t copy(const uint8_t *c,uint32_t address,uint32_t size,uint8_t *data) {
 const uint32_t *p=(const uint32_t *)w(c,28);
 uint32_t (*fn)(uint32_t,uint32_t,uint32_t,uint8_t *)=(void *)p[5];return fn(p[0],address,size,data);
}
uint32_t touch_define_last(uint8_t *c) {
 uint32_t row=w(c,16);*(uint32_t *)(c+24)=row;if(c[13])return 0;
 uint32_t count=h(c,0)*c[12],best=0,chosen=row,status=0;
 for(uint32_t i=0;i<count;i++,row+=stride(c)) {uint32_t s=seq(row);if(s>best&&!crc_check(row,h(c,2))){best=s;chosen=row;}}
 if(c[14])for(uint32_t i=0;i<count;i++,row+=stride(c)){uint32_t s=seq(row);if(s>best&&!crc_check(row,h(c,2))){best=s;chosen=row;status=0x093e0004u;}}
 *(uint32_t *)(c+24)=chosen;return status;
}
uint32_t touch_integrity(uint32_t *out,uint8_t *c) {
 uint32_t s=0,status=0;
 if(!c[13]) {uint32_t row=w(c,24);if(!crc_check(row,h(c,2)))s=seq(row);
  else if(c[14]&&!crc_check(row+region(c),h(c,2))){s=seq(row+region(c));status=0x093e0004u;}
  else {touch_define_last(c);row=w(c,24);if(!crc_check(row,h(c,2)))s=seq(row);status=0x093e0001u;}
 }
 *out=s;return status;
}
uint32_t touch_history(uint8_t *out,uint32_t address,uint8_t *c) {
 uint32_t row=previous_block(address,c),size=h(c,2),offset=(size>>3)*4u,status;
 if(!crc_check(row,size))return copy(c,row+offset,h(c,20),out+offset)?0x093e0002u:0;
 status=0x093e0001u;
 if(c[14]) {row+=region(c);if(!crc_check(row,size))status=copy(c,row+offset,h(c,20),out+offset)?0x093e0002u:0x093e0004u;}
 if(!seq(row)&&!w((const uint8_t *)row,0))status=0;
 return status;
}
static uint32_t div32(uint32_t n,uint32_t d) {uint32_t q=0;for(unsigned k=32;k;k--){unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q;}
static uint32_t mod32(uint32_t n,uint32_t d) {return n-div32(n,d)*d;}
uint32_t touch_merge(uint8_t *out,uint32_t address,uint8_t *c) {
 uint32_t rows=h(c,0),size=h(c,2),cursor=previous_block(address,c),limit=seq((uint32_t)out);
 if(limit<rows)cursor=w(c,16);else {cursor=next(cursor,c);limit=rows;}
 if(!rows)return 0x093e0003u;
 uint32_t low=(size>>1)*mod32(div32(address-w(c,16),size),rows),high=low+(size>>1),status=0;
 for(uint32_t i=0;i<limit;i++) {
  uint32_t source;uint32_t in_ram=i==limit-1u;
  if(!in_ram) {source=cursor;status=crc_check(source,size);if(status&&c[14]){source+=region(c);status=crc_check(source,size);}}
  else source=(uint32_t)out;
  if(!status) {
   uint32_t start=w((const uint8_t *)source,8),count=w((const uint8_t *)source,12),end=start+count;
   if(start<high&&low<end) {
    uint32_t src_offset=0,dst_offset;
    if(start<low){src_offset=h(c,20)-mod32(start,h(c,20));count=end-low;dst_offset=0;}
    else {dst_offset=mod32(start,h(c,20));if(high<end)count=high-start;}
    uint8_t *dst=out+(size>>3)*4u+dst_offset;
    if(in_ram){const uint8_t *p=(const uint8_t *)(source+16u+src_offset);for(uint32_t j=0;j<count;j++)dst[j]=p[j];}
    else (void)copy(c,source+16u+src_offset,count,dst);
   }
  }
  cursor=next(cursor,c);
 }
 return status;
}
