/* Independent reconstruction of locked touch read bodies 7e44/82e0/8a78.
 * SDK release-v2.20.0 is a behavioral comparator, not copied source.
 * Bounded coherent geometry and stable memory/provider are preconditions. */
#include <stdint.h>
#include "history.h"
extern uint8_t touch_row_checksum(const uint8_t *,uint32_t);
static uint32_t w(const uint8_t *c,unsigned o){return *(const uint32_t *)(c+o);}
static uint16_t h(const uint8_t *c,unsigned o){return *(const uint16_t *)(c+o);}
static uint32_t div32(uint32_t n,uint32_t d){uint32_t q=0;for(unsigned k=32;k;k--){unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q;}
static uint32_t rem(uint32_t n,uint32_t d){return n-div32(n,d)*d;}
static uint32_t mirror(const uint8_t *c){return h(c,0)*c[12]*(h(c,2)&~3u);}
static uint32_t next(uint32_t r,const uint8_t *c){r+=h(c,2)&~3u;return r>=w(c,16)+h(c,2)*h(c,0)*c[12]?w(c,16):r;}
static uint32_t previous(uint32_t r,const uint8_t *c){if(c[12]>1){uint32_t b=h(c,0)*h(c,2);r=r<w(c,16)+b?r+(c[12]-1u)*b:r-b;}return r;}
static uint32_t check(uint32_t r,const uint8_t *c){return w((const uint8_t *)r,0)==touch_row_checksum((const uint8_t *)r,h(c,2))?0:0x093e0001u;}
static uint32_t copy(const uint8_t *c,uint32_t r,uint32_t n,uint8_t *out){const uint32_t *p=(const uint32_t *)w(c,28);uint32_t (*fn)(uint32_t,uint32_t,uint32_t,uint8_t *)=(void *)p[5];return fn(p[0],r,n,out);}
uint32_t touch_simple_read(uint32_t address,uint8_t *out,uint32_t size,uint8_t *c){return copy(c,w(c,16)+address,size,out)?0x093e0002u:0;}
uint32_t touch_extended_read(uint32_t address,uint8_t *out,uint32_t size,uint8_t *c){
 for(uint32_t i=0;i<size;i++)out[i]=0;
 uint32_t sequence; (void)touch_integrity(&sequence,c);
 uint32_t half=h(c,20),rows=h(c,0),physical=h(c,2),count=div32(address+size-1u,half)-div32(address,half)+1u;
 uint32_t row=w(c,16)+physical*div32(address,half),current=address,left=size,result=0;uint8_t *dst=out;
 for(uint32_t i=0;i<count;i++){
  if(c[12]>1){row=previous(w(c,24),c);for(uint32_t k=0;k<rows;k++){row=next(row,c);uint32_t low=(physical>>1)*rem(div32(row-w(c,16),physical),rows);if(current>=low&&current<low+(physical>>1))break;}}
  uint32_t offset=rem(current,half),take=half-offset;if(i>=count-1u)take=left;
  uint32_t status=check(row,c);
  if(status&&c[14]){row+=mirror(c);if(!check(row,c))status=0x093e0004u;}
  if(status!=0x093e0001u)(void)copy(c,row+half+offset,take,dst);
  else{for(uint32_t j=0;j<take;j++)dst[j]=0;if(!w((const uint8_t *)row,4)&&!w((const uint8_t *)row,0))status=0;}
  if(c[12]<=1)row=next(row,c);
  left-=take;current+=take;dst+=take;
  if(status==0x093e0001u)result=status;else if(!result)result=status;
 }
 row=previous(w(c,24),c);
 for(uint32_t i=0;i<rows;i++){
  row=next(row,c);uint32_t source=row,status=check(source,c);
  if(status&&c[14]){source+=mirror(c);status=check(source,c);}
  if(!status){uint32_t start=w((const uint8_t *)source,8),end=start+w((const uint8_t *)source,12),high=address+size;
   if(start<high&&address<end){uint32_t lo=start>address?start:address,hi=end<high?end:high;(void)copy(c,source+16u+lo-start,hi-lo,out+lo-address);}
  }
 }
 return result;
}
uint32_t touch_eeprom_read(uint32_t address,uint8_t *out,uint32_t size,uint8_t *c){if(!size||address+size>w(c,8)||!out)return 0x093e0000u;return c[13]?touch_simple_read(address,out,size,c):touch_extended_read(address,out,size,c);}
