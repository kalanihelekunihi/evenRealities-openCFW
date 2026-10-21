#include <stdint.h>

extern uint32_t opencfw_em9305_pal_current_time(void);
extern uint32_t opencfw_em9305_auxiliary_guard_interval(void);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_transition_333a60(void);

static uint32_t rd(uintptr_t p){return *(volatile uint32_t *)p;}
static void wr(uintptr_t p,uint32_t v){*(volatile uint32_t *)p=v;}

/* Native 0x3130d4..0x31321e. List links are next@0, prev@4, time@8,
 * duration@12. The arithmetic tests use the native wrapped subtraction N
 * flag, not a C signed overflow expression. */
uint32_t opencfw_em9305_init_schedule_latest_3130d4(
    uintptr_t object,uint32_t minimum,uint32_t maximum)
{
    uintptr_t root=0x805f04u, link=root+20u;
    uint32_t original=rd(object+8u);
    uint32_t candidate=original+maximum;
    uintptr_t tail=rd(link);
    wr(object+8u,candidate); /* Native branch delay store. */
    if(tail==0u)goto empty;
    {
        uint32_t duration=rd(tail+12u);
        uint32_t time=rd(tail+8u);
        uint32_t end=time+duration+
            opencfw_em9305_auxiliary_guard_interval();
        if(((candidate-end)&0x80000000u)!=0u)goto advance;
        uint32_t now=opencfw_em9305_pal_current_time();
        if(opencfw_em9305_auxiliary_elapsed_303f8c(
            rd(object+8u),now+25u)==0u)goto fail;
        uintptr_t previous=rd(root+20u);
        uintptr_t next=rd(previous+4u);
        wr(object+4u,(uint32_t)next);
        wr(previous+4u,(uint32_t)object);
        next=rd(object+4u); /* Native 313128 fresh alias-sensitive read. */
        wr(object,(uint32_t)previous); /* BRNE delay slot. */
        if(next!=0u)wr(next,(uint32_t)object);
        else wr(root+20u,(uint32_t)object);
        goto success;
    }
advance:
    for(;;) {
        link=rd(link); /* Native 3131cc before 313134. */
        if(link==0u)goto fail;
        uintptr_t node=rd(link);
        if(node==0u)break;
        uint32_t time=rd(node+8u);
        uint32_t duration=rd(node+12u);
        uint32_t end=time+duration+
            opencfw_em9305_auxiliary_guard_interval();
        wr(object+8u,end); /* BL current-time delay slot. */
        uint32_t now=opencfw_em9305_pal_current_time();
        if(opencfw_em9305_auxiliary_elapsed_303f8c(
            rd(object+8u),now+25u)==0u)goto fail;
        uint32_t displacement=opencfw_em9305_auxiliary_elapsed_303f8c(
            rd(object+8u),original);
        if(displacement<minimum || maximum<displacement)continue;
        uint32_t object_duration=rd(object+12u);
        candidate=rd(object+8u);
        uint32_t limit=rd(link+8u);
        end=candidate+object_duration+
            opencfw_em9305_auxiliary_guard_interval();
        if(((limit-end)&0x80000000u)!=0u)continue;
        goto insert;
    }
    {
        uint32_t limit=rd(link+8u);
        uint32_t duration=rd(object+12u);
        uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
        uint32_t remaining=opencfw_em9305_auxiliary_elapsed_303f8c(
            limit-(duration+guard),original);
        if(remaining>maximum)remaining=maximum;
        candidate=original+remaining;
        wr(object+8u,candidate); /* BRLO delay slot. */
        if(remaining<minimum)goto advance;
        limit=rd(link+8u); /* Native 3131ae after candidate store. */
        if(((limit-candidate)&0x80000000u)!=0u)goto advance;
        uint32_t now=opencfw_em9305_pal_current_time();
        if(opencfw_em9305_auxiliary_elapsed_303f8c(
            rd(object+8u),now+25u)==0u)goto advance;
        if(*(volatile uint8_t *)root==2u)goto advance;
    }
insert:
    {
        uintptr_t next=rd(link);
        wr(object+4u,(uint32_t)link);
        wr(object,(uint32_t)next);
        wr(link,(uint32_t)object);
        next=rd(object); /* Native 313206 fresh alias-sensitive read. */
        if(next!=0u)wr(next+4u,(uint32_t)object);
        else wr(root+16u,(uint32_t)object);
    }
    goto success;
empty:
    {
        uint32_t now=opencfw_em9305_pal_current_time();
        if(opencfw_em9305_auxiliary_elapsed_303f8c(
            rd(object+8u),now+25u)==0u)goto fail;
        wr(root+20u,(uint32_t)object);
        wr(root+16u,(uint32_t)object);
        wr(object+4u,0u);
        wr(object,0u);
    }
success:
    if(rd(root+16u)==object)
        (void)opencfw_em9305_auxiliary_transition_333a60();
    return 1u;
fail:
    wr(object+8u,original);
    return 0u;
}
