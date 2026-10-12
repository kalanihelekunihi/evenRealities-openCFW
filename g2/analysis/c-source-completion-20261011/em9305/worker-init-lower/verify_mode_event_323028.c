#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_323028(
 uint32_t,uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,
 uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
static uint8_t captured[2][48];
static unsigned calls;
void *opencfw_em9305_memset(void *p,uint32_t value,uint32_t n)
{ return memset(p,(int)value,n); }
uintptr_t opencfw_em9305_radio_address_write_3045e8(
 uintptr_t output,uint32_t low,uint32_t high)
{
 volatile uint8_t *p=(volatile uint8_t *)output;
 for(unsigned i=0;i<4u;i++) p[i]=(uint8_t)(low>>(i*8u));
 p[4]=(uint8_t)high;p[5]=(uint8_t)(high>>8u);
 return output;
}
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{
 volatile uint8_t *p=(volatile uint8_t *)event;
 unsigned n=calls==0u?48u:8u;
 for(unsigned i=0;i<n;i++) captured[calls][i]=p[i];
 return ++calls+0x100u;
}
static uint16_t h(const uint8_t *p,unsigned at)
{ return (uint16_t)(p[at]|((uint16_t)p[at+1u]<<8u)); }
static uint32_t w(const uint8_t *p,unsigned at)
{ return (uint32_t)p[at]|((uint32_t)p[at+1u]<<8u)|((uint32_t)p[at+2u]<<16u)|((uint32_t)p[at+3u]<<24u); }
int main(void)
{
 uint8_t *cfg=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                   MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(cfg!=(void *)-1);
 *(volatile uint32_t *)(cfg+32u)=0x44556677u;
 *(volatile uint16_t *)(cfg+36u)=0x8899u;
 cfg[43]=0xaau;
 assert(mmap((void *)0x804000u,0x4000u,PROT_READ|PROT_WRITE,
             MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
 *(volatile uint8_t *)(uintptr_t)0x805a95u=0x40u;
 uint32_t result=opencfw_em9305_mode_event_323028(
   0x1234u,0u,(uintptr_t)cfg,0x55u,0x10203040u,0x50607080u,
   0x11121314u,0x15161718u,0x21222324u,0x25262728u,
   0u,0x91u,0x92u,0x9394u);
 assert(result==0x102u && calls==2u);
 assert(h(captured[0],0u)==0x1234u && captured[0][2]==5u);
 assert(captured[0][3]==0u && captured[0][4]==0u);
 assert(h(captured[0],6u)==0x1234u && captured[0][8]==0u);
 assert(captured[0][9]==0x55u && w(captured[0],10u)==0x10203040u);
 assert(h(captured[0],14u)==0x7080u && w(captured[0],16u)==0x44556677u);
 assert(h(captured[0],20u)==0x8899u && captured[0][22]==0xaau);
 assert(w(captured[0],23u)==0x21222324u && h(captured[0],27u)==0x2728u);
 assert(w(captured[0],29u)==0x11121314u && h(captured[0],33u)==0x1718u);
 assert(captured[0][35]==0x92u && h(captured[0],36u)==0x9394u);
 assert(h(captured[1],0u)==0x1234u && h(captured[1],2u)==33u);
 assert(h(captured[1],4u)==0x1234u && captured[1][6]==0x91u);
 calls=0u;
 result=opencfw_em9305_mode_event_323028(1u,0u,0u,1u,0u,0u,0u,0u,0u,0u,
                                             1u,0u,0u,0u);
 assert(result==0x101u && calls==1u);
 return 0;
}
