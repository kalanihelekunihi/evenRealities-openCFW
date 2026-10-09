#include "response.h"
#include "../codec_uart_drain_offline/drain.h"
extern uint64_t codec_tick_snapshot(void);
extern void codec_delay(uint32_t);
extern void *codec_allocate(uint32_t);
extern void codec_release(void *);
static uint16_t get16(const uint8_t *p){return p[0]|(uint16_t)p[1]<<8;}
static uint32_t get32(const uint8_t *p){return get16(p)|(uint32_t)get16(p+2)<<16;}
static void put16(uint8_t *p,uint16_t v){p[0]=v;p[1]=v>>8;}
static void put32(uint8_t *p,uint32_t v){put16(p,v);put16(p+2,v>>16);}
static void copy(uint8_t *d,const uint8_t *s,uint32_t n){while(n--)*d++=*s++;}
uint32_t codec_crc32(const uint8_t *p,uint32_t n,const uint32_t *previous){
 uint32_t c=previous?~*previous:0xffffffffu;
 while(n--){c^=*p++;for(unsigned j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320u:0);}
 return ~c;
}
/* Logging disabled contract: no omitted logging effect is claimed equivalent. */
int32_t codec_unpack(const uint8_t *wire,uint16_t available,uint8_t *m){
 if(!wire||!m||available<14)return -1;
 copy(m,wire,14);
 if(m[0]!='B'||m[1]!='U'||m[2]!='X'||m[3]!='X')return -2;
 uint16_t total=(uint16_t)(get16(m+8)+14);
 if(available<total)return -3;
 if(codec_crc32(wire,10,0)!=get32(m+10))return -4;
 uint16_t body=get16(m+8);if(m[7]&1)body=(uint16_t)(body-4);
 if(!body){put32(m+14,0);put16(m+18,0);}
 else{
  if(body>16)return -5;
  uint8_t *owned=codec_allocate(body);put32(m+14,(uint32_t)(uintptr_t)owned);
  if(!owned)return -6;
  copy(owned,wire+14,body);put16(m+18,body);
  if(m[7]&1){copy(m+20,wire+14+body,4);
   if(codec_crc32(owned,body,0)!=get32(m+20)){
    codec_release(owned);put32(m+14,0);return -7;
   }
  }
 }
 put16(m+24,total);return 0;
}
void codec_message_free(uint8_t *m){if(m&&get32(m+14)){codec_release((void *)(uintptr_t)get32(m+14));put32(m+14,0);put16(m+18,0);}}
int32_t codec_response_read(uint8_t *dst,uint16_t capacity,uint32_t timeout){
 if(!dst||!capacity)return -1;
 uint64_t start=codec_tick_snapshot();uint32_t n=0;
 while((uint16_t)n<14){if(codec_tick_snapshot()-start>=timeout)break;
  uint32_t got=codec_uart_read(dst+(uint16_t)n,14-(uint16_t)n);
  if((int32_t)got<1)codec_delay(1);else n+=got;
 }
 if((uint16_t)n<14)return -1;
 uint16_t total=(uint16_t)(get16(dst+8)+14);
 if(capacity<total)return -1;
 while((uint16_t)n<total){if(codec_tick_snapshot()-start>=timeout)break;
  uint32_t got=codec_uart_read(dst+(uint16_t)n,total-(uint16_t)n);
  if((int32_t)got<1)codec_delay(1);else n+=got;
 }
 return (uint16_t)n<total?-1:(int32_t)(uint16_t)n;
}

int32_t codec_read_uart_data(uint8_t *dst,uint16_t capacity,uint16_t *length,uint32_t ticks){
 if(!dst||!length||!capacity)return -1;
 int32_t result=codec_response_read(dst,capacity,ticks);
 if(result<0)return result;
 *length=(uint16_t)result;return 0;
}
