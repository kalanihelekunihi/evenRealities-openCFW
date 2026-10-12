#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned deadline_result,callbacks,expected_code,expected_encoded,owner_mode;static char trace[32];static unsigned n;
static void mark(char c){trace[n++]=c;}
static uint32_t callback_second(uint32_t code,uint32_t context,uint32_t zero,uint32_t timestamp,uint32_t encoded){assert(code==1&&context==77&&zero==0&&timestamp==1000&&encoded==expected_encoded);callbacks++;mark('C');return 0x82;}
static uint32_t callback_first(uint32_t code,uint32_t context,uint32_t zero,uint32_t timestamp,uint32_t encoded){assert(code==expected_code&&context==77&&zero==0&&timestamp==1000&&encoded==expected_encoded);callbacks++;mark('B');*(uint32_t *)0x805cf8=(uint32_t)(uintptr_t)callback_second;return 0x81;}
uint32_t opencfw_em9305_radio_deadline_333450(uint32_t deadline){assert(deadline==2512&&*(uint32_t *)0x805e88==deadline);mark('D');return deadline_result;}
uint32_t opencfw_em9305_radio_receive_trigger_312360(void){assert(*(uint32_t *)0xf04420==320&&*(uint8_t *)0xf04405==1);mark('R');return 0;}
uint32_t opencfw_em9305_radio_configure_3104d8(uint32_t first,uint32_t second){assert(first==4&&second==9);mark('Q');return 0;}
uint32_t opencfw_em9305_radio_finish_310454(uint32_t selector){assert(selector==(owner_mode==2?3:1));mark('F');if(owner_mode==2)*(uint32_t *)0x805d0c=0x833000;else *(uint32_t *)0x805d18=900;return 0;}
uint32_t opencfw_em9305_radio_setup_310450(uint32_t value){assert(value==44);mark('S');*(uint32_t *)0x805d0c=0x831000;return 0;}
uint32_t opencfw_em9305_radio_timestamp_310474(uint32_t value){assert(value==55);mark('T');*(uint32_t *)0x805d0c=0x832000;return 0;}
uint32_t opencfw_em9305_radio_transform_33322c(uintptr_t p){assert(p==0x833014);mark('X');return 0;}
uint32_t opencfw_em9305_common_activate_310580(uint32_t value){assert(value==0);mark('A');return 0;}
/* Authenticated receive command predicate31b7c8..31b7d4 and radio
 * completion3330d8..33322c, with complete scheduler leaf children. */
uint32_t opencfw_em9305_receive_command_31b7c8(uintptr_t source)
{ return *(volatile uint8_t *)(source+621u)==3u; }
uint32_t opencfw_em9305_radio_window_3122fc(uint32_t value,uint32_t mode)
{
 *(volatile uint32_t *)(uintptr_t)0xf04420u=value;
 *(volatile uint8_t *)(uintptr_t)0xf04405u=(uint8_t)mode;
 return value;
}
uint32_t opencfw_em9305_radio_window_start_3103e0(uint32_t offset,uint32_t size)
{
 uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805e84u;
 uint32_t deadline=offset+base-85u;
 *(volatile uint32_t *)(uintptr_t)0x805e88u=deadline;
 uint32_t result=opencfw_em9305_radio_deadline_333450(deadline);
 uint32_t state=1u;
 if(result!=0u){
  uint32_t extra=*(volatile uint16_t *)(uintptr_t)0x805e9cu;
  (void)opencfw_em9305_radio_window_3122fc(20u+((size+extra)<<2),1u);
  (void)opencfw_em9305_radio_receive_trigger_312360();
  state=3u;
 }
 *(volatile uint8_t *)(uintptr_t)0x805e78u=(uint8_t)state;
 return result;
}
uint32_t opencfw_em9305_radio_window_resume_310430(uint32_t unused,uint32_t size)
{
 (void)unused;
 uint32_t extra=*(volatile uint16_t *)(uintptr_t)0x805e9cu;
 uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805e8cu;
 *(volatile uint32_t *)(uintptr_t)0x805e84u=base;
 uint32_t result=opencfw_em9305_radio_window_3122fc(20u+((size+extra)<<2),1u);
 *(volatile uint8_t *)(uintptr_t)0x805e78u=3u;
 return result;
}
uint32_t opencfw_em9305_radio_window_base_310654(uint32_t unused)
{
 (void)unused;
 uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805e8cu;
 *(volatile uint8_t *)(uintptr_t)0x805e78u=2u;
 *(volatile uint32_t *)(uintptr_t)0x805e84u=base;
 return base;
}
/* Exact five non-executable status bytes at native3344c0..3344c5. */
const uint8_t opencfw_em9305_radio_status_3344c0[5]={0u,1u,3u,4u,6u};
uint32_t opencfw_em9305_radio_callback_3330d8(uint32_t status,uint32_t timestamp,uint32_t selector,uint32_t context)
{
 uintptr_t source=0x805d18u,root=0x805cf4u;
 uint32_t count=*(volatile uint16_t *)(source+12u);
 *(volatile uint16_t *)(source+12u)=(uint16_t)(count+1u);
 uint32_t active=1u,code=1u;
 if(status<=4u&&((0x19u>>status)&1u)!=0u){
  uintptr_t packet=*(volatile uint32_t *)(source+28u);
  uint32_t length=*(volatile uint8_t *)packet;
  uint32_t limit=*(volatile uint16_t *)(source+32u);
  uint32_t span=length+2u>limit?limit+6u:length+9u;
  if(*(volatile uint8_t *)(uintptr_t)0x805d3au!=0u)span+=4u;
  if(selector==1u)span=8u+(span<<2);
  else if(selector==3u)span=(span<<4)+80u;
  else if(selector==4u)span=(span<<6)+80u;
  else span=8u+(span<<3);
  uint32_t finish;
  if(*(volatile uint8_t *)(source+10u)!=0u){
   uint32_t base=*(volatile uint32_t *)(root+8u);
   finish=span+timestamp-base;
  }else{
   uint32_t base=*(volatile uint32_t *)source;
   finish=base+span;
  }
  uint32_t mode=*(volatile uint8_t *)(root+16u);
  *(volatile uint32_t *)(root+36u)=finish;
  if(mode==1u){
   uint32_t first=*(volatile uint8_t *)(source+14u);
   uint32_t other=*(volatile uint8_t *)(source+15u);
   *(volatile uint32_t *)source=finish+150u;
   if(first!=other){
    uint32_t second=*(volatile uint8_t *)(source+25u);
    (void)opencfw_em9305_radio_configure_3104d8(first,second);
   }
   (void)opencfw_em9305_radio_window_base_310654(150u);
  }else if(mode==3u){
   uintptr_t owner=*(volatile uint32_t *)(root+24u);
   if(owner!=0u){
    (void)opencfw_em9305_radio_finish_310454(*(volatile uint8_t *)(owner+1u));
    finish=*(volatile uint32_t *)(root+36u);
   }
   uint32_t extra=*(volatile uint16_t *)(root+40u);
   uint32_t base=*(volatile uint32_t *)(root+12u);
   finish+=150u;
   *(volatile uint32_t *)(root+36u)=finish;
   (void)opencfw_em9305_radio_window_resume_310430(147u,extra+base);
  }else if(mode==2u){
   uintptr_t owner=*(volatile uint32_t *)(root+24u);
   if(owner!=0u){
    (void)opencfw_em9305_radio_setup_310450(*(volatile uint32_t *)(owner+4u));
    owner=*(volatile uint32_t *)(root+24u);
    (void)opencfw_em9305_radio_timestamp_310474(*(volatile uint32_t *)(owner+8u));
    owner=*(volatile uint32_t *)(root+24u);
    (void)opencfw_em9305_radio_finish_310454(*(volatile uint8_t *)(owner+1u));
    owner=*(volatile uint32_t *)(root+24u);
    (void)opencfw_em9305_radio_transform_33322c(owner+20u);
   }
   uint32_t base=*(volatile uint32_t *)(root+8u);
   uint32_t time=*(volatile uint32_t *)(root+20u);
   uint32_t extra=*(volatile uint16_t *)(root+40u);
   uint32_t delta=time-base;
   *(volatile uint32_t *)(root+36u)=delta;
   active=opencfw_em9305_radio_window_start_3103e0(delta-3u,extra+6u);
  }else (void)opencfw_em9305_common_activate_310580(mode);
 }
 uint32_t encoded=selector==3u?1u:selector==4u?2u:0u;
 if(status<5u)code=opencfw_em9305_radio_status_3344c0[status];
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805cf8u;
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)(code,context,0u,timestamp,encoded);
 if(active==0u){
  callback=*(volatile uint32_t *)(uintptr_t)0x805cf8u;
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)(1u,context,0u,timestamp,encoded);
 }
 return result;
}


static void reset(unsigned status,unsigned mode,unsigned selector,unsigned extended,unsigned shortlimit){memset((void *)0x800000,0,0x100000);memset((void *)0xf00000,0,0x10000);memset(trace,0,sizeof(trace));n=callbacks=owner_mode=0;*(uint32_t *)0x805d18=500;*(uint32_t *)0x805d34=0x820000;*(uint8_t *)0x820000=12;*(uint16_t *)0x805d38=shortlimit?5:20;*(uint8_t *)0x805d3a=extended;*(uint8_t *)0x805d22=extended;*(uint16_t *)0x805d24=65535;*(uint8_t *)0x805d26=4;*(uint8_t *)0x805d27=5;*(uint8_t *)0x805d31=9;*(uint32_t *)0x805cfc=100;*(uint32_t *)0x805d00=30;*(uint32_t *)0x805d08=2000;*(uint16_t *)0x805d1c=60;*(uint8_t *)0x805d04=mode;*(uint32_t *)0x805e84=700;*(uint32_t *)0x805e8c=800;*(uint16_t *)0x805e9c=9;*(uint32_t *)0x805cf8=(uint32_t)(uintptr_t)callback_first;expected_code=status<5?opencfw_em9305_radio_status_3344c0[status]:1;expected_encoded=selector==3?1:selector==4?2:0;deadline_result=(status+selector)&1;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);assert(mmap((void *)0xf00000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0xf00000);unsigned cases=0;for(unsigned status=0;status<8;status++)for(unsigned mode=0;mode<4;mode++)for(unsigned selector=0;selector<5;selector++)for(unsigned extended=0;extended<2;extended++)for(unsigned shortlimit=0;shortlimit<2;shortlimit++){reset(status,mode,selector,extended,shortlimit);unsigned allowed=status<=4&&((0x19>>status)&1);unsigned result=opencfw_em9305_radio_callback_3330d8(status,1000,selector,77);assert(*(uint16_t *)0x805d24==0);assert(callbacks==(allowed&&mode==2&&!deadline_result?2:1)&&result==(callbacks==2?0x82:0x81));unsigned span=(shortlimit?11:21)+(extended?4:0);span=selector==1?8+(span<<2):selector==3?(span<<4)+80:selector==4?(span<<6)+80:8+(span<<3);unsigned finish=extended?span+900:500+span;if(!allowed){assert(strcmp(trace,"B")==0&&*(uint32_t *)0x805d18==500);}else if(mode==0){assert(strcmp(trace,"AB")==0&&*(uint32_t *)0x805d18==finish);}else if(mode==1){assert(strcmp(trace,"QB")==0&&*(uint32_t *)0x805d18==finish+150&&*(uint8_t *)0x805e78==2&&*(uint32_t *)0x805e84==800);}else if(mode==2){assert(strcmp(trace,deadline_result?"DRB":"DBC")==0&&*(uint32_t *)0x805d18==1900&&*(uint8_t *)0x805e78==(deadline_result?3:1));}else assert(strcmp(trace,"B")==0&&*(uint32_t *)0x805d18==finish+150&&*(uint32_t *)0xf04420==416&&*(uint32_t *)0x805e84==800);cases++;}
reset(0,2,1,0,0);owner_mode=2;deadline_result=1;*(uint32_t *)0x805d0c=0x830000;*(uint32_t *)(0x830000+4)=44;*(uint32_t *)(0x831000+8)=55;*(uint8_t *)(0x832000+1)=3;assert(opencfw_em9305_radio_callback_3330d8(0,1000,1,77)==0x81&&strcmp(trace,"STFXDRB")==0);cases++;
reset(0,3,1,0,0);owner_mode=3;*(uint32_t *)0x805d0c=0x830000;*(uint8_t *)(0x830000+1)=1;assert(opencfw_em9305_radio_callback_3330d8(0,1000,1,77)==0x81&&strcmp(trace,"FB")==0&&*(uint32_t *)0x805d18==1050);cases++;
for(unsigned value=0;value<256;value++){*(uint8_t *)(0x840000+621)=value;assert(opencfw_em9305_receive_command_31b7c8(0x840000)==(value==3));cases++;}printf("PASS %u\n",cases);}
