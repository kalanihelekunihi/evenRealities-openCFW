#include "request.h"
#include "../codec_response_offline/response.h"
extern uint32_t codec_channel_tx(uint32_t,const uint8_t *,uint32_t);
static void copy(uint8_t *d,const uint8_t *s,uint32_t n){while(n--)*d++=*s++;}
static void put16(uint8_t *p,uint16_t v){p[0]=v;p[1]=v>>8;}
static void put32(uint8_t *p,uint32_t v){put16(p,v);put16(p+2,v>>16);}
int32_t codec_pack(uint16_t low,uint16_t high,const uint8_t *payload,uint16_t length,uint8_t crcflag,uint8_t *wire,uint16_t *total){
 if(!wire||!total)return -1;
 uint16_t declared=(uint16_t)(length+(crcflag?4:0));
 if(declared>16)return -2;
 wire[0]='B';wire[1]='U';wire[2]='X';wire[3]='X';
 put16(wire+4,(low&0xff)|(high&0xff00));
 volatile uint8_t *sequence=(volatile uint8_t *)(uintptr_t)0x20075013;
 uint8_t current=*sequence;wire[6]=current;*sequence=(uint8_t)(current+1);
 wire[7]=crcflag!=0;put16(wire+8,declared);
 if(payload&&length){copy(wire+14,payload,length);if(crcflag)put32(wire+14+length,codec_crc32(payload,length,0));}
 put32(wire+10,codec_crc32(wire,10,0));*total=(uint16_t)(declared+14);return 0;
}
int32_t codec_uart_tx(const uint8_t *wire,uint32_t total){return codec_channel_tx(3,wire,total)==0?0:-1;}
int32_t codec_send(uint16_t low,uint16_t high,const uint8_t *payload,uint16_t length,uint8_t flag){
 uint8_t *wire=(uint8_t *)(uintptr_t)0x2007399c;uint16_t total=0;
 int32_t r=codec_pack(low,high,payload,length,flag,wire,&total);
 return r?r:codec_uart_tx(wire,total);
}

extern uint32_t codec_hal_blocking(void *,const void *);
extern void codec_wrapper_delay(uint32_t);
uint32_t codec_channel_tx(uint32_t input,const uint8_t *payload,uint32_t count){
 uint8_t channel=(uint8_t)input;
 if(channel>=4)return 1;
 volatile uint8_t *descriptor=(volatile uint8_t *)(uintptr_t)(0x20000d2c+28u*channel);
 if(descriptor[24]!=1)return 1;
 uint32_t transfer[14];for(unsigned i=0;i<14;i++)((volatile uint32_t *)transfer)[i]=0;transfer[0]=(uint32_t)(uintptr_t)payload;transfer[1]=count;
 descriptor[25]=0;
 uint32_t handle=*(volatile uint32_t *)(descriptor+4);
 uint32_t result=codec_hal_blocking((void *)(uintptr_t)handle,transfer);
 for(uint32_t i=0;i<1000&&descriptor[25]!=1;i++)codec_wrapper_delay(10);
 return result?1:0;
}
