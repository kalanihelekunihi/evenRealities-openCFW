#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static char trace[32];static unsigned n,expected,mutate,request;
static void mark(char c){trace[n++]=c;}
static uint32_t cb(uint32_t status){assert(status==expected);mark('B');return 123;}
static uint32_t cb2(uint32_t status){assert(status==expected);mark('C');return 456;}
uint32_t opencfw_em9305_radio_window_resume_310430(uint32_t a,uint32_t b){assert(a==147&&b==16&&*(uint32_t *)0x805d18==650);mark('W');return 0;}
uint32_t opencfw_em9305_radio_finish_310454(uint32_t a){assert(a==3);mark('F');*(uint32_t *)0x805d18=900;*(uint32_t *)0x805d0c=0x833000;return 0;}
uint32_t opencfw_em9305_radio_configure_3104d8(uint32_t a,uint32_t b){assert(a==4&&b==9);mark('Q');if(mutate)*(uint32_t *)0x805d18=777;return 0;}
uint32_t opencfw_em9305_radio_window_base_310654(uint32_t a){assert(a==150);mark('V');return 0;}
uint32_t opencfw_em9305_radio_setup_310450(uint32_t a){assert(a==44);mark('S');*(uint32_t *)0x805d0c=0x831000;return 0;}
uint32_t opencfw_em9305_radio_timestamp_310474(uint32_t a){assert(a==55);mark('T');*(uint32_t *)0x805d0c=0x832000;return 0;}
uint32_t opencfw_em9305_radio_transform_33322c(uintptr_t a){assert(a==0x833014);mark('X');*(uint16_t *)0x805d24=1;return 0;}
uint32_t opencfw_em9305_radio_request_state_310600(uint32_t a){request=a;mark('R');return 0;}
uint32_t opencfw_em9305_common_activate_310580(uint32_t a){assert(a==0);mark('A');return 0;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t l){assert(d==(void *)0x840000&&s==(void *)0x805d28&&l==4);mark('M');memcpy(d,s,l);*(uint32_t *)0x805cf4=(uint32_t)(uintptr_t)cb2;return d;}
/* Authenticated radio follow-up callback333268..333338. Mode2's
 * owner-null path compares the captured incremented counter's low half;
 * the owner-present path reloads root48 after the transform child. */
uint32_t opencfw_em9305_radio_callback_333268(uint32_t status)
{
 uintptr_t source=0x805d18u,root=0x805cf4u;
 uint32_t count=*(volatile uint16_t *)(source+12u);
 uint32_t increment=count+1u;
 *(volatile uint16_t *)(source+12u)=(uint16_t)increment;
 if(status==0u){
  uint32_t mode=*(volatile uint8_t *)(root+16u);
  if(mode==1u){
   uint32_t time=*(volatile uint32_t *)source;
   uint32_t size=*(volatile uint16_t *)(source+4u);
   time+=150u;
   *(volatile uint32_t *)source=time;
   (void)opencfw_em9305_radio_window_resume_310430(147u,size+6u);
  }else if(mode==3u){
   uintptr_t owner=*(volatile uint32_t *)(root+24u);
   if(owner!=0u)(void)opencfw_em9305_radio_finish_310454(*(volatile uint8_t *)(owner+1u));
   uint32_t time=*(volatile uint32_t *)source;
   uint32_t first=*(volatile uint8_t *)(source+14u);
   uint32_t other=*(volatile uint8_t *)(source+15u);
   time+=150u;
   *(volatile uint32_t *)source=time;
   if(first!=other){
    uint32_t second=*(volatile uint8_t *)(source+25u);
    (void)opencfw_em9305_radio_configure_3104d8(first,second);
   }
   (void)opencfw_em9305_radio_window_base_310654(150u);
  }else if(mode==2u){
   uintptr_t owner=*(volatile uint32_t *)(root+24u);
   uint32_t comparison=increment;
   if(owner!=0u){
    (void)opencfw_em9305_radio_setup_310450(*(volatile uint32_t *)(owner+4u));
    owner=*(volatile uint32_t *)(root+24u);
    (void)opencfw_em9305_radio_timestamp_310474(*(volatile uint32_t *)(owner+8u));
    owner=*(volatile uint32_t *)(root+24u);
    (void)opencfw_em9305_radio_finish_310454(*(volatile uint8_t *)(owner+1u));
    owner=*(volatile uint32_t *)(root+24u);
    (void)opencfw_em9305_radio_transform_33322c(owner+20u);
    comparison=*(volatile uint16_t *)(root+48u);
   }
   uint32_t base=*(volatile uint32_t *)(root+8u);
   uint32_t time=*(volatile uint32_t *)(root+20u);
   uint32_t delta=time-base;
   *(volatile uint32_t *)(root+36u)=delta;
   if((uint16_t)comparison==1u){
    uint32_t first=*(volatile uint8_t *)(source+14u);
    uint32_t other=*(volatile uint8_t *)(source+15u);
    if(first!=other){
     uint32_t second=*(volatile uint8_t *)(source+25u);
     (void)opencfw_em9305_radio_configure_3104d8(first,second);
     delta=*(volatile uint32_t *)source;
    }
   }
   (void)opencfw_em9305_radio_request_state_310600(delta);
  }else (void)opencfw_em9305_common_activate_310580(mode);
 }
 uintptr_t destination=*(volatile uint32_t *)(source+20u);
 if(destination!=0u){
  uint32_t length=*(volatile uint8_t *)(source+24u);
  (void)opencfw_em9305_memcpy((void *)destination,(const void *)(source+16u),length);
  *(volatile uint32_t *)(source+20u)=0u;
 }
 uintptr_t callback=*(volatile uint32_t *)root;
 return ((uint32_t (*)(uint32_t))callback)(status!=0u);
}


static void reset(unsigned status,unsigned mode,unsigned count,unsigned copy){memset((void *)0x800000,0,0x100000);memset(trace,0,sizeof(trace));n=mutate=request=0;expected=status!=0;*(uint32_t *)0x805cf4=(uint32_t)(uintptr_t)cb;*(uint32_t *)0x805d18=500;*(uint16_t *)0x805d1c=10;*(uint16_t *)0x805d24=count;*(uint8_t *)0x805d04=mode;*(uint8_t *)0x805d26=4;*(uint8_t *)0x805d27=5;*(uint8_t *)0x805d31=9;*(uint32_t *)0x805cfc=100;*(uint32_t *)0x805d08=2000;if(copy){*(uint32_t *)0x805d2c=0x840000;*(uint8_t *)0x805d30=4;*(uint32_t *)0x805d28=0x12345678;}}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned counts[]={0,1,65535};for(unsigned status=0;status<4;status++)for(unsigned mode=0;mode<4;mode++)for(unsigned ci=0;ci<3;ci++)for(unsigned copy=0;copy<2;copy++){unsigned count=counts[ci];reset(status,mode,count,copy);assert(opencfw_em9305_radio_callback_333268(status)==(copy?456:123));assert(*(uint16_t *)0x805d24==(uint16_t)(count+1));char want[32]="";if(status==0){if(mode==0)strcat(want,"A");if(mode==1)strcat(want,"W");if(mode==2){strcat(want,count==0?"QR":"R");assert(request==1900);}if(mode==3)strcat(want,"QV");}strcat(want,copy?"MC":"B");assert(strcmp(trace,want)==0);if(copy){assert(*(uint32_t *)0x805d2c==0&&*(uint32_t *)0x840000==0x12345678);}cases++;}
reset(0,2,55,0);mutate=1;*(uint32_t *)0x805d0c=0x830000;*(uint32_t *)(0x830000+4)=44;*(uint32_t *)(0x831000+8)=55;*(uint8_t *)(0x832000+1)=3;assert(opencfw_em9305_radio_callback_333268(0)==123&&strcmp(trace,"STFXQRB")==0&&request==777);cases++;
reset(0,3,0,0);*(uint32_t *)0x805d0c=0x830000;*(uint8_t *)(0x830000+1)=3;assert(opencfw_em9305_radio_callback_333268(0)==123&&strcmp(trace,"FQVB")==0&&*(uint32_t *)0x805d18==1050);cases++;printf("PASS %u\n",cases);}
