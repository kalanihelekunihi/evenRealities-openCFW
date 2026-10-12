#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_child_31e4a0(uint32_t,uint32_t);
static char trace[32];
static unsigned trace_n;
static uint32_t notice[3],notice_n;
static uint32_t args[14];
static unsigned mutation_mode;
static void mark(char c){assert(trace_n<sizeof trace-1u);trace[trace_n++]=c;trace[trace_n]=0;}
uint32_t opencfw_em9305_mode_event_32279c(uintptr_t c){(void)c;mark('E');return 1u;}
uint32_t opencfw_em9305_mode_event_322b70(uintptr_t c){(void)c;mark('A');return 2u;}
uint32_t opencfw_em9305_mode_event_32c978(uintptr_t c){(void)c;mark('B');return 3u;}
uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t c,uint32_t e)
{
 notice[notice_n++]=e;mark('C');
 if(mutation_mode!=0u&&e==0x66u) *(volatile uint32_t *)(c+4u)=1u<<8u;
 if(mutation_mode!=0u&&e==0x67u) *(volatile uint32_t *)(c+4u)=1u<<6u;
 return 4u;
}
uint32_t opencfw_em9305_mode_event_323028(uint32_t a0,uint32_t a1,uintptr_t a2,
  uint32_t a3,uint32_t a4,uint32_t a5,uint32_t a6,uint32_t a7,uint32_t a8,
  uint32_t a9,uint32_t a10,uint32_t a11,uint32_t a12,uint32_t a13)
{uint32_t v[]={a0,a1,(uint32_t)a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13};
 memcpy(args,v,sizeof args);mark('P');return 5u;}
uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t c){(void)c;mark('Q');return 6u;}
uint32_t opencfw_em9305_mode_event_3212f0(uintptr_t c,uint32_t e)
{(void)c;(void)e;mark('T');return 7u;}
uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t c){(void)c;mark('L');return 8u;}
uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t c){(void)c;mark('N');return 9u;}
uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t id)
{assert(id==1u);mark('S');return 10u;}
uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t c)
{(void)c;mark('R');return 0xa5u;}
uint32_t opencfw_em9305_mode_event_318edc(uintptr_t c,uint32_t e)
{(void)c;mark('D');return 0xd000u+e;}

static void fixture(uint8_t state,uint32_t event,const char *expected)
{
    uintptr_t c=0x800390u,config=0x830000u;
    memset((void *)0x800000u,0,0x100000u);
    *(volatile uint32_t *)0x805c70u=0x800000u;
    *(volatile uint32_t *)0x805c6cu=(uint32_t)config;
    *(volatile uint8_t *)(c+1u)=state;
    *(volatile uint32_t *)(c+4u)=mutation_mode!=0u?1u:0x141u;
    *(volatile uint16_t *)(c+570u)=28u;
    *(volatile uint8_t *)(c+321u)=0x31u;
    *(volatile uint8_t *)(c+890u)=0x8au;
    *(volatile uint16_t *)(c+892u)=0x892u;
    *(volatile uint8_t *)(c+620u)=0xffu;
    *(volatile uint32_t *)(c+636u)=0x13u;
    *(volatile uint32_t *)(c+640u)=0x23u;
    *(volatile uint8_t *)(config+52u)=0x52u;
    for(unsigned i=0;i<6;++i) *(volatile uint32_t *)(config+60u+4u*i)=0x6000u+i;
    trace_n=notice_n=0u;trace[0]=0;
    uint32_t result=opencfw_em9305_child_31e4a0((uint32_t)c,event);
    assert(strcmp(trace,expected)==0);
    assert(result==(strchr(expected,'R')!=0?0xa5u:0xd000u+event));
    if(strchr(expected,'P')!=0) {
        assert(args[0]==1u&&args[1]==0u&&args[2]==config+4u&&args[3]==0x52u);
        for(unsigned i=0;i<6;++i) assert(args[4+i]==0x6000u+i);
        assert(args[10]==0u&&args[11]==0x31u&&args[12]==0x8au&&args[13]==0x892u);
        assert(*(volatile uint8_t *)(c+1u)==2u);
        assert(notice_n==3u&&notice[0]==0x66u&&notice[1]==0x67u&&notice[2]==0x68u);
    }
    if(strchr(expected,'Q')!=0) {
        assert(*(volatile uint32_t *)(c+636u)==0x12u);
        assert(*(volatile uint32_t *)(c+640u)==0u);
        assert(*(volatile uint8_t *)(c+620u)==0u);
    }
}

int main(void)
{
    assert(mmap((void *)0x800000u,0x100000u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
    fixture(0u,0x3fu,"ABCCCPD");
    mutation_mode=1u;
    fixture(0u,0x3fu,"ABCCCPD");
    mutation_mode=0u;
    fixture(0u,0x4cu,"LNSR");
    fixture(0u,0x4du,"SR");
    fixture(3u,0x51u,"QD");
    fixture(3u,0x4cu,"LNSR");
    fixture(2u,0x3du,"ED");
    fixture(2u,0x4cu,"TLNSR");
    fixture(2u,0x47u,"D");
    fixture(2u,0x48u,"D");
    fixture(1u,0x4du,"SR");
    fixture(1u,0x52u,"D");
    puts("PASS 31e4a0 connected 12 native-path host fixtures");
    return 0;
}
