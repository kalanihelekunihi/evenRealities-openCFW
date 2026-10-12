#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned gate=1,ready=1,calls;
uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
uint32_t opencfw_em9305_command_apply_307fcc(uint32_t a,uint32_t b,uint32_t c){assert(a==0xffffffff&&b==55&&c==66);calls++;return 100;}
uint32_t opencfw_em9305_command_apply_30805c(uint32_t a,uint32_t b,uint32_t c){assert(a==0xffffffff&&b==55&&c==66);calls++;return 101;}
uint32_t opencfw_em9305_command_ready_3213d0(uint32_t a){assert(a<0xf00);return ready;}
uint32_t opencfw_em9305_command_apply_307d0c(uint32_t a,uint32_t b){assert(a==1&&b<=7);calls++;return 999;}
uint32_t opencfw_em9305_command_apply_309874(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){assert(a==0xffffffff&&b<=3&&c==499&&(d&65535)>=10&&(d&65535)<=0x4000&&e==0x12345678);calls++;return 102;}
/* Authenticated five command providers30c5c0/30c5e0/30dbd4/30dc70/30d48c.
 * Stream gate ignores incoming id; all children retain original full inputs. */
extern uint32_t opencfw_em9305_command_apply_307fcc(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_apply_30805c(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_apply_307d0c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_ready_3213d0(uint32_t);
extern uint32_t opencfw_em9305_command_apply_309874(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_command_30c5c0(uint32_t id,uint32_t first,uint32_t second)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 return opencfw_em9305_command_apply_307fcc(id,first,second);
}
uint32_t opencfw_em9305_command_30c5e0(uint32_t id,uint32_t first,uint32_t second)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 return opencfw_em9305_command_apply_30805c(id,first,second);
}
uint32_t opencfw_em9305_command_30dbd4(uint32_t id,uint32_t mode)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(id>=0xf00u)return 18u;
 if(opencfw_em9305_command_ready_3213d0(id)==0u)return 66u;
 if((mode&3u)==3u&&(*(volatile uint32_t *)(uintptr_t)0x805b34u&16u)==0u)return 17u;
 (void)opencfw_em9305_command_apply_307d0c(id,mode);
 return 0u;
}
uint32_t opencfw_em9305_command_30dc70(uint32_t id,uint32_t mode,uint32_t first,uint32_t second,uint32_t last)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(mode>3u)return 18u;
 if(mode==3u&&(*(volatile uint32_t *)(uintptr_t)0x805b34u&16u)==0u)return 17u;
 if(first>499u)return 18u;
 if((uint16_t)(second-0x4001u)<0xc009u)return 18u;
 return opencfw_em9305_command_apply_309874(id,mode,first,second,last);
}
uint32_t opencfw_em9305_command_30d48c(uint32_t id,uint32_t first,uint32_t second,uint32_t unused)
{
 (void)unused;
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(id>3u)return 18u;
 if(id==3u&&(*(volatile uint32_t *)(uintptr_t)0x805b34u&16u)==0u)return 17u;
 if(first>499u)return 18u;
 if((uint16_t)(second-0x4001u)<0xc009u)return 18u;
 *(volatile uint16_t *)(uintptr_t)0x805aceu=(uint16_t)second;
 *(volatile uint16_t *)(uintptr_t)0x805accu=(uint16_t)first;
 *(volatile uint8_t *)(uintptr_t)0x805acbu=(uint8_t)id;
 return 0u;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(gate=0;gate<2;gate++){calls=0;assert(opencfw_em9305_command_30c5c0(0xffffffff,55,66)==(gate?100:12)&&calls==gate);calls=0;assert(opencfw_em9305_command_30c5e0(0xffffffff,55,66)==(gate?101:12)&&calls==gate);cases+=2;}gate=1;for(unsigned cap=0;cap<2;cap++)for(unsigned mode=0;mode<5;mode++)for(unsigned first=499;first<=500;first++)for(unsigned second=0;second<65536;second++){*(uint32_t *)0x805b34=cap?16:0;calls=0;unsigned expected=mode>3?18:mode==3&&!cap?17:first>499||second<10||second>0x4000?18:0;unsigned r=opencfw_em9305_command_30dc70(0xffffffff,mode,first,second|0x10000,0x12345678);assert(r==(expected?expected:102)&&calls==!expected);r=opencfw_em9305_command_30d48c(mode,first,second|0x10000,99);assert(r==expected);if(!expected)assert(*(uint16_t *)0x805ace==second&&*(uint16_t *)0x805acc==first&&*(uint8_t *)0x805acb==mode);cases+=2;}
for(unsigned cap=0;cap<2;cap++)for(ready=0;ready<2;ready++)for(unsigned mode=0;mode<8;mode++){*(uint32_t *)0x805b34=cap?16:0;calls=0;unsigned r=opencfw_em9305_command_30dbd4(1,mode),expected=!ready?66:(mode&3)==3&&!cap?17:0;assert(r==expected&&calls==!expected);cases++;}
gate=0;assert(opencfw_em9305_command_30dbd4(0xffffffff,0)==12&&opencfw_em9305_command_30dc70(0,0,0,0,0)==12&&opencfw_em9305_command_30d48c(0,0,0,0)==12);cases+=3;gate=ready=1;assert(opencfw_em9305_command_30dbd4(0xf00,0)==18);cases++;printf("PASS %u\n",cases);}
