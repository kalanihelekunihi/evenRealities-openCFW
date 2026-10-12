#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t,uint32_t);
static uint32_t selected,guard_result=1u;
static unsigned guards,timers,completes,finishes,phy_rejects,mode_rejects,mode_done;
static unsigned column_calls[5];
uint32_t opencfw_em9305_mode_selector_31affc(uintptr_t c,uint32_t event)
{assert(c==0x810000u&&event!=0xffu);return selected;}
uint32_t opencfw_em9305_mode_guard_31a988(uintptr_t c,uint32_t s,uint32_t cat)
{assert(c==0x810000u&&s==selected&&cat<8u);++guards;return guard_result;}
uint32_t opencfw_em9305_mode_reject_3233b4(uintptr_t c,uint32_t s)
{assert(c==0x810000u&&s==selected);++mode_rejects;return 17u;}
uint32_t opencfw_em9305_mode_done_3234ec(uintptr_t c,uint32_t s)
{assert(c==0x810000u&&s==selected);++mode_done;return 18u;}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t c,uint32_t why,uint32_t ext)
{assert(c==0x810000u&&why==26u&&ext==0u);++phy_rejects;return 19u;}
uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t c)
{assert(c==0x810000u);++timers;return 20u;}
uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t c)
{assert(c==0x810000u);++finishes;return 21u;}
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t c)
{assert(c==0x810000u);++completes;return 22u;}
#define COLUMN(N) static uint32_t col##N(uintptr_t c,uintptr_t self) \
{assert(c==0x810000u&&self==(uintptr_t)col##N);++column_calls[N];return 30u+N;}
COLUMN(0) COLUMN(1) COLUMN(2) COLUMN(3) COLUMN(4)
int main(void)
{
 assert(mmap((void *)0x330000u,0x10000u,PROT_READ|PROT_WRITE,
             MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
 assert(mmap((void *)0x800000u,0x30000u,PROT_READ|PROT_WRITE,
             MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
 uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(ctx!=(void *)-1);
 uintptr_t callbacks[5]={(uintptr_t)col0,(uintptr_t)col1,(uintptr_t)col2,
                          (uintptr_t)col3,(uintptr_t)col4};
 for(unsigned i=0;i<5u;i++){
  assert(callbacks[i]<=UINT32_MAX);
  *(volatile uint32_t *)(uintptr_t)(0x334ba4u+i*4u)=(uint32_t)callbacks[i];
 }
 assert(opencfw_em9305_mode_event_31bd78((uintptr_t)ctx,0xffu)==0u);
 /* Event102 -> category1. Inactive path calls the second column, starts
  * the timer, and activates mode0. */
 assert(opencfw_em9305_mode_event_31bd78((uintptr_t)ctx,102u)==1u);
 assert(guards==1u&&timers==1u&&column_calls[1]==1u);
 assert(ctx[620]==1u&&ctx[626]==1u&&ctx[635]==0u&&ctx[1]==3u);
 /* Event22 -> active category0; selector0 calls column0, then column1. */
 assert(opencfw_em9305_mode_event_31bd78((uintptr_t)ctx,22u)==1u);
 assert(column_calls[0]==1u&&column_calls[1]==2u);
 assert((*(uint32_t *)(ctx+652u)&1u)!=0u);
 /* Event12 + code1 enters category4 via native 42-entry branch table. */
 *(volatile uint8_t *)(uintptr_t)0x802818u=1u;
 ctx[620]=1u;ctx[635]=19u;
 assert(opencfw_em9305_mode_event_31bd78((uintptr_t)ctx,12u)==1u);
 assert(column_calls[2]==1u);
 /* Event12 + code2 category3, current selector differs: guard, column2,
  * then completed flag. */
 *(volatile uint8_t *)(uintptr_t)0x802818u=2u;
 ctx[635]=1u;
 assert(opencfw_em9305_mode_event_31bd78((uintptr_t)ctx,12u)==1u);
 assert(column_calls[2]==2u);
 /* Guard rejection in the initial category4 route emits the PHY reject. */
 ctx[620]=0u;guard_result=0u;
 assert(opencfw_em9305_mode_event_31bd78((uintptr_t)ctx,13u)==1u);
 assert(phy_rejects==1u);
 return 0;
}
