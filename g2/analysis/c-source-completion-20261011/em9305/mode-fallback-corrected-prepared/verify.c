#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_mode_event_31c420(uintptr_t,uint32_t);
static unsigned calls;
uint32_t opencfw_em9305_init_response_packet_326a84(uintptr_t c){assert(c==0x810000);return 0x91;}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t c,uint32_t r,uint32_t e){assert(c==0x810000&&r==30&&e==0);return 0x92;}
uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t p){assert(p==0x810010);assert(*(volatile uint8_t *)0x810001==3&&*(volatile uint8_t *)0x81026c==0);calls++;return 0x93;}
uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t c){*(volatile uint8_t *)(c+12)=34;return c;}
int main(void){assert(mmap((void *)0x810000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x810000);unsigned ev[]={0x49,0x4a,0x51,0x73},code[]={40,30,34,48};for(unsigned prior=0;prior<256;prior++)for(unsigned i=0;i<4;i++){*(volatile uint8_t *)0x810001=prior;*(volatile uint8_t *)0x81026c=255;unsigned old=calls;assert(opencfw_em9305_mode_event_31c420(0x810000,ev[i])==(prior==2?0x93:prior));assert(*(volatile uint8_t *)0x810001==3&&*(volatile uint8_t *)0x81026c==0&&*(volatile uint8_t *)0x81000c==code[i]);assert(calls==old+(prior==2));}assert(opencfw_em9305_mode_event_31c420(0x810000,13)==0x91);assert(opencfw_em9305_mode_event_31c420(0x810000,14)==0x92);assert(opencfw_em9305_mode_event_31c420(0x810000,0x99)==0x810000);puts("PASS1024 transition states plus response/reject/default routes");}
