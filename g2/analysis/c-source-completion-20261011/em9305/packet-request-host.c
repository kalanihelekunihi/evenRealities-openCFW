#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static char trace[32];static unsigned n,mode,length;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_radio_request_enter_310678(void){mark('E');return 0;}
uint32_t opencfw_em9305_radio_window_start_3103e0(uint32_t a,uint32_t b){assert(a==0&&b==70&&*(uint32_t *)0x805e84==500&&*(uint8_t *)0x805e78==3&&*(uint16_t *)0x805d24==0&&*(uint32_t *)0x805d34==0x830001&&*(uint16_t *)0x805d38==(uint16_t)length);mark('W');*(uint8_t *)0x805e78=mode;return 99;}
uint32_t opencfw_em9305_radio_state_310260(void){mark('S');return *(uint8_t *)0x805e78;}
uint32_t opencfw_em9305_radio_followup_driver_310374(uint32_t a,uint32_t b){assert(a==0x830000&&b==length);mark('F');return 111;}
static uint32_t cb(uint32_t a,uint32_t b,uint32_t c,uint32_t d){assert(a==1&&b==0&&c==9&&d==0);mark('C');return 222;}
uint32_t opencfw_em9305_radio_request_exit_31069c(void){mark('X');if(mode==3)assert(*(uint8_t *)0x805d22==1&&*(uint32_t *)0x805d18==0);*(uint8_t *)0x805e78=0;*(uint8_t *)0x805e99=9;*(uint32_t *)0x805e7c=(uint32_t)(uintptr_t)cb;return 333;}
/* Authenticated packet request30faec and native window/callback tails. */
uint32_t opencfw_em9305_radio_window_request_31041c(uint32_t base,uint32_t size)
{
 *(volatile uint32_t *)(uintptr_t)0x805e84u=base;
 *(volatile uint8_t *)(uintptr_t)0x805e78u=3u;
 return opencfw_em9305_radio_window_start_3103e0(0u,size);
}
uint32_t opencfw_em9305_radio_failure_callback_310360(void)
{
 uint32_t kind=*(volatile uint8_t *)(uintptr_t)0x805e99u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805e7cu;
 return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t))callback)(1u,0u,kind,0u);
}
uint32_t opencfw_em9305_radio_request_30faec(uintptr_t packet,uint32_t length)
{
 (void)opencfw_em9305_radio_request_enter_310678();
 uintptr_t root=0x805cfcu;
 uint32_t extra=*(volatile uint16_t *)(root+32u);
 uint32_t lead=*(volatile uint32_t *)(root+4u);
 *(volatile uint32_t *)(root+56u)=(uint32_t)(packet+1u);
 uint32_t size=extra+lead;
 uint32_t base=*(volatile uint32_t *)root;
 *(volatile uint16_t *)(root+60u)=(uint16_t)length;
 *(volatile uint16_t *)(root+40u)=0u;
 uint32_t result=opencfw_em9305_radio_window_request_31041c(base,size);
 uint32_t state=opencfw_em9305_radio_state_310260();
 if(state==3u){
  result=opencfw_em9305_radio_followup_driver_310374((uint32_t)packet,length);
  *(volatile uint8_t *)(root+38u)=1u;
  *(volatile uint32_t *)(root+28u)=0u;
 }
 result=opencfw_em9305_radio_request_exit_31069c();
 if(state==0u)result=opencfw_em9305_radio_failure_callback_310360();
 return result;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned lengths[]={0,1,65535,65536,0xffffffff};for(mode=0;mode<4;mode++)for(unsigned i=0;i<5;i++){memset((void *)0x800000,0,0x100000);memset(trace,0,sizeof(trace));n=0;length=lengths[i];*(uint32_t *)0x805cfc=500;*(uint32_t *)0x805d00=50;*(uint16_t *)0x805d1c=20;*(uint16_t *)0x805d24=99;unsigned r=opencfw_em9305_radio_request_30faec(0x830000,length);assert(r==(mode==0?222:333)&&strcmp(trace,mode==0?"EWSXC":mode==3?"EWSFX":"EWSX")==0);cases++;}printf("PASS %u\n",cases);}
