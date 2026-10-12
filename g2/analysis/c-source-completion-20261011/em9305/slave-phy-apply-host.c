#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned supported,calls,reason;
uint32_t opencfw_em9305_phy_supported_31b39c(void){return supported;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t e){(void)p;calls++;reason=e;return 77;}
/* Native32cb58..32cbec full slave update validation and instant publish. */
uint32_t opencfw_em9305_slave_phy_apply_32cb58(uintptr_t record)
{
 int32_t first=(int8_t)*(volatile uint8_t *)(uintptr_t)0x80281cu;
 if(first<0)return opencfw_em9305_receive_terminate_325c08(record,74u);
 int32_t second=(int8_t)*(volatile uint8_t *)(uintptr_t)0x80281du;
 if(second<0)return opencfw_em9305_receive_terminate_325c08(record,74u);
 if((first|second)==0)return opencfw_em9305_receive_terminate_325c08(record,110u);
 uint32_t anchor=*(volatile uint16_t *)(record+262u);
 uint32_t instant=*(volatile uint16_t *)(uintptr_t)0x80281eu;
 if((uint16_t)(instant-anchor)>=32767u)return opencfw_em9305_receive_terminate_325c08(record,73u);
 if(first!=0){
  uint32_t supported=opencfw_em9305_phy_supported_31b39c();
  if((supported&(uint32_t)first)==0u)return opencfw_em9305_receive_terminate_325c08(record,74u);
  second=*(volatile uint8_t *)(uintptr_t)0x80281du;
 }
 if((uint8_t)second!=0u){
  uint32_t supported=opencfw_em9305_phy_supported_31b39c();
  if((supported&(uint32_t)second)==0u)return opencfw_em9305_receive_terminate_325c08(record,74u);
 }
 uint32_t value=*(volatile uint8_t *)(uintptr_t)0x80281cu,valid=1u;
 if(value>=5u||((0x17u>>value)&1u)==0u){
  (void)opencfw_em9305_receive_terminate_325c08(record,74u);valid=0u;
 }
 value=*(volatile uint8_t *)(uintptr_t)0x80281du;
 if(value>=5u||value==3u)return opencfw_em9305_receive_terminate_325c08(record,74u);
 if(valid==0u)return 0u;
 uint32_t directions=*(volatile uint16_t *)(uintptr_t)0x80281cu;
 instant=*(volatile uint16_t *)(uintptr_t)0x80281eu;
 *(volatile uint16_t *)(record+722u)=(uint16_t)directions;
 *(volatile uint16_t *)(record+724u)=(uint16_t)instant;
 return instant;
}

int main(void){
 if(mmap((void*)0x802000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[800];unsigned count=0;const unsigned deltas[4]={0,32766,32767,65535};
 for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++)for(unsigned m=0;m<4;m++)for(unsigned k=0;k<4;k++){
 memset(r,0xa5,sizeof r);*(uint16_t*)(r+262)=0x8000;supported=1+(m&1)*2+(m>>1)*4;*(volatile uint8_t*)0x80281c=a;*(volatile uint8_t*)0x80281d=c;uint16_t instant=(uint16_t)(0x8000+deltas[k]);*(volatile uint16_t*)0x80281e=instant;calls=reason=0;
 unsigned expectedcalls=0,expectedreason=0,result=77,success=0;
 if(a>=128||c>=128){expectedcalls=1;expectedreason=74;}
 else if(!(a|c)){expectedcalls=1;expectedreason=110;}
 else if(k>=2){expectedcalls=1;expectedreason=73;}
 else if((a&&!(a&supported))||(c&&!(c&supported))){expectedcalls=1;expectedreason=74;}
 else{
  unsigned firstvalid=a==0||a==1||a==2||a==4,secondvalid=c==0||c==1||c==2||c==4;
  expectedcalls=(!firstvalid)+(!secondvalid);expectedreason=expectedcalls?74:0;
  if(!secondvalid)result=77;else if(!firstvalid)result=0;else{result=instant;success=1;}
 }
 if(opencfw_em9305_slave_phy_apply_32cb58((uintptr_t)r)!=result||calls!=expectedcalls||reason!=expectedreason||*(uint16_t*)(r+722)!=(success?(a|(c<<8)):0xa5a5)||*(uint16_t*)(r+724)!=(success?instant:0xa5a5))abort();
 count++;
 }
 printf("PASS %u slave update validation cases\n",count);return 0;
}
