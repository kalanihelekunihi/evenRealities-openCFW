#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_schedule_latest_3130d4(
    uintptr_t,uint32_t,uint32_t);
static uint32_t current_calls,guard_calls,transitions,mutate_guard_call;
static uintptr_t mutate_limit_address;
static uint32_t mutate_limit_value;
uint32_t opencfw_em9305_pal_current_time(void)
{++current_calls;return 100u;}
uint32_t opencfw_em9305_auxiliary_guard_interval(void)
{++guard_calls;
 if(guard_calls==mutate_guard_call)
  *(uint32_t *)mutate_limit_address=mutate_limit_value;
 return 2u;}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t a,uint32_t b)
{uint32_t d=a-b;return (d&0x80000000u)?0u:d;}
uint32_t opencfw_em9305_auxiliary_transition_333a60(void)
{++transitions;return 0xfeedu;}
static void reset(void)
{memset((void *)(uintptr_t)0x800000u,0,0x100000u);
 current_calls=guard_calls=transitions=mutate_guard_call=0u;
 mutate_limit_address=0u;mutate_limit_value=0u;}
static uint32_t rd(uintptr_t p){return *(uint32_t *)p;}
static void wr(uintptr_t p,uint32_t v){*(uint32_t *)p=v;}
int main(void)
{
 void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
     PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(p!=(void *)-1);
 const uintptr_t object=0x803000u,node=0x804000u,
     next=0x805000u,third=0x806000u,root=0x805f04u;
 reset();wr(object+8u,200u);
 assert(opencfw_em9305_init_schedule_latest_3130d4(object,5u,30u)==1u);
 assert(rd(object+8u)==230u&&rd(root+16u)==object&&rd(root+20u)==object);
 assert(rd(object)==0u&&rd(object+4u)==0u&&transitions==1u);
 reset();wr(object+8u,50u);
 assert(opencfw_em9305_init_schedule_latest_3130d4(object,5u,30u)==0u);
 assert(rd(object+8u)==50u&&rd(root+16u)==0u&&transitions==0u);
 reset();wr(root+16u,node);wr(root+20u,node);
 wr(node+8u,100u);wr(node+12u,10u);wr(object+8u,200u);
 assert(opencfw_em9305_init_schedule_latest_3130d4(object,5u,30u)==1u);
 assert(rd(object+8u)==230u&&rd(node+4u)==object);
 assert(rd(object)==node&&rd(object+4u)==0u);
 assert(rd(root+16u)==node&&rd(root+20u)==object&&transitions==0u);
 reset();wr(root+16u,node);wr(root+20u,node);wr(root+28u,500u);
 wr(node+8u,200u);wr(node+12u,10u);wr(object+8u,190u);
 wr(object+12u,3u);
 assert(opencfw_em9305_init_schedule_latest_3130d4(object,1u,5u)==1u);
 assert(rd(object+8u)==195u&&rd(node)==object);
 assert(rd(object+4u)==node&&rd(root+16u)==object&&transitions==1u);
 /* Initial BN must step root+20 -> node before inspecting next. The
  * terminal limit comes from next+8, not the root+28 sentinel. */
 reset();wr(root+20u,node);wr(root+16u,next);wr(root+28u,500u);
 wr(node,next);wr(node+8u,300u);wr(node+12u,10u);
 wr(next+8u,140u);wr(object+8u,130u);wr(object+12u,3u);
 assert(opencfw_em9305_init_schedule_latest_3130d4(object,1u,5u)==1u);
 assert(rd(object+8u)==135u&&rd(next)==object&&rd(root+16u)==object);
 assert(rd(object+4u)==next&&transitions==1u);
 /* Rejection at the first traversed node advances once more and inserts
  * after the next link when its displacement and limit permit it. */
 reset();wr(root+20u,node);wr(root+16u,third);
 wr(node,next);wr(node+8u,300u);wr(node+12u,10u);
 wr(next,third);wr(next+8u,180u);wr(third+8u,150u);
 wr(object+8u,130u);wr(object+12u,3u);
 assert(opencfw_em9305_init_schedule_latest_3130d4(object,20u,25u)==1u);
 assert(rd(object+8u)==152u&&rd(next)==object&&rd(object)==third);
 assert(rd(third+4u)==object&&transitions==0u);
 /* Guard mutates the live limit between its first read and the later
  * candidate comparison; the fresh load must reject and advance. */
 reset();wr(root+20u,node);wr(root+16u,next);
 wr(node,next);wr(node+8u,300u);wr(node+12u,10u);
 wr(next+8u,140u);wr(object+8u,130u);wr(object+12u,3u);
 mutate_guard_call=3u;mutate_limit_address=next+8u;mutate_limit_value=130u;
 assert(opencfw_em9305_init_schedule_latest_3130d4(object,1u,5u)==0u);
 assert(rd(object+8u)==130u&&rd(next)==0u);
 return 0;
}
