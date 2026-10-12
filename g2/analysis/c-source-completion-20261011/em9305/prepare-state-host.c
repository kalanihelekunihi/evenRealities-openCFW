#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t queue,uintptr_t handler){uint32_t node=*(volatile uint32_t *)queue;if(!node)return 0;*(volatile uint8_t *)handler=*(volatile uint8_t *)(uintptr_t)(node+4);return node+8;}
/* Authenticated preparation state 32d694 and queue/header children.
 * Native ARC EM listing: 313fcc, 32dedc..32df24, 32d694..32d738.
 * Preserve volatile read/store ordering and untouched optional fields. */
uint32_t opencfw_em9305_queue_single_313fcc(uintptr_t queue)
{
 uint32_t tail=*(volatile uint32_t *)(queue+4u);
 uint32_t head=*(volatile uint32_t *)queue;
 return head==tail;
}
uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t output,uintptr_t input)
{
 uint32_t b1=*(volatile uint8_t *)(input+1u);
 uint32_t b0=*(volatile uint8_t *)input;
 uint32_t packed=b0+(b1<<8),low=(uint8_t)packed;
 *(volatile uint8_t *)(output+5u)=(uint8_t)b1;
 *(volatile uint8_t *)output=(uint8_t)(packed&3u);
 uint32_t flag=(low>>5)&1u;
 *(volatile uint8_t *)(output+4u)=(uint8_t)flag;
 *(volatile uint8_t *)(output+3u)=(uint8_t)((low>>4)&1u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)((low>>3)&1u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)((low>>2)&1u);
 if(flag!=0u){
  uint32_t extra=*(volatile uint8_t *)(input+2u);
  *(volatile uint8_t *)(output+6u)=(uint8_t)(extra>>6);
  *(volatile uint8_t *)(output+7u)=(uint8_t)(extra&31u);
  return 3u;
 }
 return 2u;
}
uint32_t opencfw_em9305_radio_prepare_state_32d694(uintptr_t source,uintptr_t state,uintptr_t flagptr)
{
 uint8_t handler;
 uintptr_t queue=source+360u;
 uintptr_t packet=opencfw_em9305_wsf_event_peek(queue,(uintptr_t)&handler);
 uint32_t kind=0u,flagvalue=0u;
 if(packet!=0u){
  uint32_t single=opencfw_em9305_queue_single_313fcc(queue);
  if(handler==255u){
   uint8_t decoded[8];
   uint32_t header=opencfw_em9305_short_header_decode_32dedc((uintptr_t)decoded,packet);
   uint32_t length=*(volatile uint8_t *)(packet+1u);
   flagvalue=single^1u;
   *(volatile uint32_t *)(state+4u)=(uint32_t)packet;
   *(volatile uint16_t *)state=(uint16_t)(header+length);
   kind=1u;
  }else{
   uint32_t index=*(volatile uint8_t *)(packet+7u);
   uint32_t unit=*(volatile uint8_t *)(packet+6u);
   uint32_t length=*(volatile uint16_t *)(packet+4u);
   uint32_t product;
   product=unit*index;
   uint32_t end=product+unit;
   if(length<end)unit=length-product;
   uintptr_t base=packet+index*8u;
   *(volatile uint32_t *)(state+4u)=(uint32_t)(base+10u);
   uint32_t first=*(volatile uint8_t *)(base+8u);
   uint32_t extra=*(volatile uint8_t *)(base+9u);
   uint32_t data=*(volatile uint32_t *)packet;
   *(volatile uint16_t *)(state+8u)=(uint16_t)unit;
   *(volatile uint16_t *)state=(uint16_t)first;
   *(volatile uint32_t *)(state+12u)=data+product;
   if(extra!=0u){
    *(volatile uint16_t *)(state+16u)=(uint16_t)extra;
    *(volatile uint32_t *)(state+20u)=(uint32_t)(packet+12u+index*8u);
    kind=3u;
   }else kind=2u;
   if(single==0u)flagvalue=1u;
   else{
    length=*(volatile uint16_t *)(packet+4u);
    product+=(uint16_t)unit;
    flagvalue=product<length;
   }
  }
 }
 *(volatile uint8_t *)flagptr=(uint8_t)(flagvalue&1u);
 return kind;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t p=0x860000,state=0x870000,flag=0x880000,node=0x840000,packet=node+8;uint8_t in[3],out[8];
for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++){in[0]=a;in[1]=77;in[2]=c;memset(out,0xa5,8);unsigned n=opencfw_em9305_short_header_decode_32dedc((uintptr_t)out,(uintptr_t)in);assert(n==((a&32)?3:2));assert(out[0]==(a&3)&&out[1]==((a>>2)&1)&&out[2]==((a>>3)&1)&&out[3]==((a>>4)&1)&&out[4]==((a>>5)&1)&&out[5]==77);assert(out[6]==((a&32)?c>>6:0xa5)&&out[7]==((a&32)?c&31:0xa5));cases++;}
memset((void *)state,0xa5,24);assert(opencfw_em9305_radio_prepare_state_32d694(p,state,flag)==0&&*(uint8_t *)flag==0&&*(uint32_t *)state==0xa5a5a5a5);cases++;
for(unsigned single=0;single<2;single++)for(unsigned header=0;header<2;header++){*(uint32_t *)(p+360)=node;*(uint32_t *)(p+364)=single?node:node+100;*(uint8_t *)(node+4)=255;*(uint8_t *)packet=header?32:0;*(uint8_t *)(packet+1)=255;assert(opencfw_em9305_radio_prepare_state_32d694(p,state,flag)==1);assert(*(uint16_t *)state==255+2+header&&*(uint32_t *)(state+4)==packet&&*(uint8_t *)flag==!single);cases++;}
for(unsigned single=0;single<2;single++)for(unsigned ix=0;ix<8;ix++)for(unsigned unit=0;unit<256;unit++)for(unsigned len=0;len<300;len+=37)for(unsigned extra=0;extra<2;extra++){memset((void *)packet,0,100);memset((void *)state,0xa5,24);*(uint32_t *)(p+360)=node;*(uint32_t *)(p+364)=single?node:node+100;*(uint8_t *)(node+4)=2;*(uint32_t *)packet=0x830000;*(uint16_t *)(packet+4)=len;*(uint8_t *)(packet+6)=unit;*(uint8_t *)(packet+7)=ix;*(uint8_t *)(packet+ix*8+8)=23;*(uint8_t *)(packet+ix*8+9)=extra?17:0;unsigned product=unit*ix,u=len<product+unit?len-product:unit;unsigned kind=opencfw_em9305_radio_prepare_state_32d694(p,state,flag);assert(kind==2+extra);assert(*(uint16_t *)state==23&&*(uint16_t *)(state+8)==(uint16_t)u&&*(uint32_t *)(state+4)==packet+ix*8+10&&*(uint32_t *)(state+12)==0x830000+product);assert(*(uint8_t *)flag==(!single||product+(uint16_t)u<len));if(extra)assert(*(uint16_t *)(state+16)==17&&*(uint32_t *)(state+20)==packet+ix*8+12);else assert(*(uint32_t *)(state+16)==0xa5a5a5a5&&*(uint32_t *)(state+20)==0xa5a5a5a5);cases++;}
printf("PASS %u\n",cases);}
