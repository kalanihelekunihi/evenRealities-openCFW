#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_318edc(uintptr_t,uint32_t);
static char trace[8];static unsigned n;
static void mark(char c){trace[n++]=c;trace[n]=0;}
uint32_t opencfw_em9305_mode_event_32cf78(uintptr_t c){(void)c;mark('A');return 1u;}
uint32_t opencfw_em9305_mode_event_32cb40(uintptr_t c){(void)c;mark('B');return 2u;}
uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t c){(void)c;mark('C');return 3u;}
uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t c){(void)c;mark('D');return 4u;}
uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t c)
{(void)c;mark('E');return 0xabcdef01u;}
uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t c)
{assert(c==0x800010u);mark('F');return 0x12345678u;}

int main(void)
{
    assert(mmap((void *)0x800000u,0x100000u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
    const uint32_t events[]={0u,0x47u,0x48u,0x4cu,0x52u};
    unsigned cases=0;
    for(unsigned ei=0;ei<5;++ei)
    for(unsigned prior=0;prior<4;++prior) {
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x800001u=(uint8_t)prior;
        *(volatile uint8_t *)0x80026cu=0xffu;
        n=0;trace[0]=0;
        uint32_t result=opencfw_em9305_mode_event_318edc(0x800000u,events[ei]);
        if(events[ei]==0x4cu) {
            assert(strcmp(trace,"CDE")==0&&result==0xabcdef01u);
            assert(*(volatile uint8_t *)0x800001u==prior);
        } else if(events[ei]==0x52u) {
            assert(trace[0]==0&&result==0x800000u);
            assert(*(volatile uint8_t *)0x800001u==prior);
        } else {
            assert(strcmp(trace,events[ei]==0u?(prior==2u?"AF":"A"):
                        events[ei]==0x48u?(prior==2u?"BF":"B"):
                        prior==2u?"F":"")==0);
            assert(result==(prior==2u?0x12345678u:prior));
            assert(*(volatile uint8_t *)0x800001u==3u);
            assert(*(volatile uint8_t *)0x80026cu==0u);
        }
        ++cases;
    }
    printf("PASS mode/event 318edc %u source/contract fixtures\n",cases);
    return 0;
}
