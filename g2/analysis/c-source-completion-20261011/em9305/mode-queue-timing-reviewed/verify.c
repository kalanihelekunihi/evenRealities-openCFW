#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_325a68(uintptr_t,uintptr_t);
static uint32_t slot,first,result;static unsigned calls;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){assert(n==8);return slot;}
uint32_t opencfw_em9305_phy_queue_count_314114(uintptr_t q){assert(q==0x810168);return 2;}
uint32_t opencfw_em9305_test_mpywhul(uint32_t a,uint32_t b){assert(a==2&&b==3);return 6;}
uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t c){assert(c==0x810000);return 10;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t a,uint32_t b){assert(a==6&&b==10);*(uint16_t*)0x810106=999;return calls++?result:first;}
uint32_t opencfw_em9305_test_mpyw(uint32_t a,uint32_t b){assert(a==7);return a*b+123;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x820000);return 0x456;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805cac=0x830000;*(uint16_t*)0x830026=3;*(uint16_t*)0x81034e=7;for(unsigned n=0;n<256;n++)for(unsigned route=0;route<3;route++){calls=0;slot=route==2?0:0x820000;first=route?8:4;result=2;*(uint16_t*)0x810106=17;*(uint16_t*)0x810104=n;for(unsigned j=0;j<5;j++)*(uint8_t*)(uintptr_t)(0x8102c4+j)=n+j;assert(opencfw_em9305_mode_callback_325a68(0x810000,0)==(slot?0x456:0));if(slot){unsigned t=route?2:6;unsigned v=7*(n+1)*t+123+17;assert(calls==(route?2:1)&&*(uint16_t*)0x8102cc==(uint16_t)v);assert(*(uint8_t*)0x820000==1);for(unsigned j=0;j<5;j++)assert(*(uint8_t*)(uintptr_t)(0x820001+j)==(uint8_t)(n+j));assert(*(uint16_t*)0x820006==(uint16_t)v);}else assert(!calls);}puts("PASS768 queue/timing paths with host arithmetic models");}
