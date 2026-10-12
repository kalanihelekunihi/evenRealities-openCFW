#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static char trace[32];static unsigned n,mode,expected,which;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_radio_request_enter_310678(void){mark('E');return 0;}
uint32_t opencfw_em9305_radio_request_exit_31069c(void){mark('X');return 888;}
uint32_t opencfw_em9305_radio_request_base_310640(uint32_t base){assert(base==500&&*(uint16_t *)0x805d24==0);mark('B');*(uint8_t *)0x805e78=mode;return 0;}
uintptr_t opencfw_em9305_radio_flatten_333064(uintptr_t p,uint32_t s){assert(p==0x810000&&s<5);mark('F');*(uint16_t *)p=65530;*(uint16_t *)(p+8)=20;*(uint16_t *)(p+16)=10;return 0x830000;}
uint32_t opencfw_em9305_radio_request_3105b8(uintptr_t p,uint32_t size){assert(p==0x830000&&size==expected);mark('R');if(which==0){*(uint8_t *)0x805d1e=7;*(uint8_t *)0x805d20=9;}else{*(uint8_t *)0x805d1f=7;*(uint8_t *)0x805d21=9;*(uint32_t *)0x805d18=1000;}return 0;}
static uint32_t host_mpy(uint32_t a,uint32_t b){assert(a==expected+9&&b==7);mark('M');return 0x12345;}
/* Authenticated record requests30fc68/30fcd8. Flattened buffer remains
 * native R0 through halfword length reads and is passed to3105b8. */
uint32_t opencfw_em9305_radio_state_310260(void)
{ return *(volatile uint8_t *)(uintptr_t)0x805e78u; }
uint32_t opencfw_em9305_radio_record_request_30fc68(uintptr_t descriptor,uint32_t selector)
{
 (void)opencfw_em9305_radio_request_enter_310678();
 uintptr_t root=0x805cfcu;
 uint32_t base=*(volatile uint32_t *)root;
 *(volatile uint16_t *)(root+40u)=0u;
 (void)opencfw_em9305_radio_request_base_310640(base);
 if(opencfw_em9305_radio_state_310260()==2u){
  uintptr_t buffer=opencfw_em9305_radio_flatten_333064(descriptor,selector);
  uint32_t size=0u;
  if(selector==1u)size=*(volatile uint16_t *)descriptor;
  else if(selector==3u){
   uint32_t first=*(volatile uint16_t *)descriptor;
   uint32_t second=*(volatile uint16_t *)(descriptor+8u);
   uint32_t third=*(volatile uint16_t *)(descriptor+16u);
   size=first+second+third;
  }else if(selector==2u){
   uint32_t second=*(volatile uint16_t *)(descriptor+8u);
   uint32_t first=*(volatile uint16_t *)descriptor;
   size=second+first;
  }
  size=(uint16_t)size;
  (void)opencfw_em9305_radio_request_3105b8(buffer,size);
  uint32_t unit=*(volatile uint8_t *)(root+34u);
  uint32_t extra=*(volatile uint8_t *)(root+36u);
  uint32_t product;
  product=host_mpy(size+9u,unit);
  *(volatile uint8_t *)(root+38u)=0u;
  *(volatile uint32_t *)(root+28u)=product+extra;
 }
 return opencfw_em9305_radio_request_exit_31069c();
}
uint32_t opencfw_em9305_radio_request_30fcd8(uintptr_t descriptor,uint32_t selector)
{
 uintptr_t buffer=opencfw_em9305_radio_flatten_333064(descriptor,selector);
 uint32_t size=0u;
 if(selector==1u)size=*(volatile uint16_t *)descriptor;
 else if(selector==3u){
  uint32_t first=*(volatile uint16_t *)descriptor;
  uint32_t second=*(volatile uint16_t *)(descriptor+8u);
  uint32_t third=*(volatile uint16_t *)(descriptor+16u);
  size=first+second+third;
 }else if(selector==2u){
  uint32_t second=*(volatile uint16_t *)(descriptor+8u);
  uint32_t first=*(volatile uint16_t *)descriptor;
  size=second+first;
 }
 size=(uint16_t)size;
 (void)opencfw_em9305_radio_request_3105b8(buffer,size);
 uintptr_t root=0x805d18u;
 uint32_t unit=*(volatile uint8_t *)(root+7u);
 uint32_t extra=*(volatile uint8_t *)(root+9u);
 uint32_t time=*(volatile uint32_t *)root,product;
 product=host_mpy(size+9u,unit);
 time+=extra+product;
 *(volatile uint32_t *)root=time;
 return time;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(which=0;which<2;which++)for(mode=0;mode<4;mode++)for(unsigned selector=0;selector<5;selector++){memset((void *)0x800000,0,0x100000);memset(trace,0,sizeof(trace));n=0;*(uint32_t *)0x805cfc=500;*(uint16_t *)0x805d24=99;expected=selector==1?65530:selector==2?14:selector==3?24:0;unsigned r=which?opencfw_em9305_radio_request_30fcd8(0x810000,selector):opencfw_em9305_radio_record_request_30fc68(0x810000,selector);if(which){assert(r==1000+9+0x12345&&*(uint32_t *)0x805d18==r&&strcmp(trace,"FRM")==0);}else{assert(r==888&&*(uint16_t *)0x805d24==0);if(mode==2){assert(strcmp(trace,"EBFRMX")==0&&*(uint32_t *)0x805d18==9+0x12345&&*(uint8_t *)0x805d22==0);}else assert(strcmp(trace,"EBX")==0);}cases++;}printf("PASS %u\n",cases);}
