#include <stdint.h>

extern uint32_t opencfw_em9305_radio_peer_pair_303a40(
    uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_identity_pair_303a60(
    uint32_t,uint32_t,uint32_t,uintptr_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t,uint32_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(
    uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_transition_random_317afc(void);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(
    uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(
    uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_schedule_latest_3130d4(
    uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_post(uint32_t,uint32_t);

static uint32_t rd(uintptr_t p){return *(volatile uint32_t *)p;}
static uint16_t rh(uintptr_t p){return *(volatile uint16_t *)p;}
static uint8_t rb(uintptr_t p){return *(volatile uint8_t *)p;}
static void wr(uintptr_t p,uint32_t v){*(volatile uint32_t *)p=v;}
static void wh(uintptr_t p,uint16_t v){*(volatile uint16_t *)p=v;}
static void wb(uintptr_t p,uint8_t v){*(volatile uint8_t *)p=v;}
static uint32_t mpywhl_327de8(uint32_t a,uint32_t b)
{
#ifdef __arc__
    uint32_t result;
    __asm__ volatile("mpywhl %0,%1,%2":"=r"(result):"r"(a),"r"(b):
        "r58","r59","memory");
    return result;
#else
    return a*(uint32_t)(int32_t)(int16_t)b;
#endif
}

/* Native 0x327de8..0x327fe0. The stock frame contains one 8-byte
 * temporary identity pair. The mode-one and modes-two-to-four loops are
 * retained as loops; scheduler children may mutate the observed fields. */
uint32_t opencfw_em9305_init_transition_process_327de8(uintptr_t owner)
{
    uint8_t flag0=rb(0x8052fcu),flag1=rb(0x8052fdu);
    if((flag0|flag1)!=0u)goto command_event;

    uintptr_t mode_state=0x805a70u,extended=0x805be1u;
    uint8_t pending=rb(mode_state+15u);
    uintptr_t object=rd(owner+44u);
    uint8_t current=rb(extended+1u);
    uint32_t pair[2];
    uint32_t lower=0u,upper=0u;
    uint32_t found=0u;
    if(pending!=0u && current==1u) {
        upper=rd(mode_state+32u);
        lower=rd(mode_state+28u);
        wb(mode_state+15u,0u);
        found=1u;
    } else if((current&2u)!=0u) {
        uint32_t upper_arg=rd(0x805b98u);
        uint32_t lower_arg=rd(0x805b94u);
        uint32_t kind=rb(0x805b92u);
        found=opencfw_em9305_radio_peer_pair_303a40(
            kind,lower_arg,upper_arg,(uintptr_t)pair);
        if(found!=0u){upper=pair[1];lower=pair[0];}
    }
    if(found!=0u) {
        uintptr_t address=0x8052d6u;
        (void)opencfw_em9305_radio_address_write_3045e8(
            address,lower,upper);
        uint16_t first=rh(address),second=rh(address+2u),third=rh(address+4u);
        wh(address+252u,first);
        wh(address+254u,second);
        wh(address+256u,third); /* STH.AS [r13,128]. */
        wr(object+88u,upper);
        wr(object+84u,lower);
    }

    uintptr_t config=0x805b84u;
    uint8_t mode=rb(config+12u);
    if(mode==1u || mode==4u) {
        uint32_t flags=rd(object+80u)&68u;
        if(flags==68u) {
            uint32_t high=rd(config+20u);
            uint32_t low=rd(config+16u);
            uint32_t kind=rb(config+14u);
            if(opencfw_em9305_radio_identity_pair_303a60(
                kind,low,high,(uintptr_t)pair)!=0u)
                (void)opencfw_em9305_radio_address_write_3045e8(
                    0x8052dcu,pair[0],pair[1]);
            mode=rb(config+12u); /* Only path through native 327eae. */
        }
    }
    if(mode!=1u && mode!=4u && rb(0x805bc0u)!=0u) {
        uintptr_t source=config+28u;
        uint8_t count=rb(source+31u);
        wb(source+32u,0u);
        wb(object+124u,(uint8_t)(count+8u));
        wb(0x8052d5u,(uint8_t)(count+6u)); /* BL delay slot. */
        (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x8052dcu,
            (const void *)source,count);
    }
    if(rb(extended)!=0u) {
        uintptr_t source=0x805bc1u;
        uint8_t count=rb(source+31u);
        wb(source+32u,0u);
        wb(object+125u,(uint8_t)(count+8u));
        wb(0x8053d1u,(uint8_t)(count+6u)); /* STB.AB old base. */
        (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x8053d8u,
            (const void *)source,count);
    }
    (void)opencfw_em9305_associated_object_init_312918(owner,0u);
    mode=rb(config+12u);
    if(mode<=4u && mode!=1u) {
        for(;;) {
            if((rb(mode_state+27u)&2u)!=0u) {
                uint32_t draw=opencfw_em9305_init_transition_random_317afc();
                uint32_t old_time=rd(owner+8u); /* Native before MPYWHL. */
                uint32_t adjustment=mpywhl_327de8(draw,625u);
                wr(owner+8u,old_time+adjustment);
            }
            uint32_t upper_bound=rd(config+8u);
            uint32_t lower_bound=rd(config+4u);
            if(lower_bound==upper_bound) {
                wr(owner+8u,rd(owner+8u)+lower_bound);
                if(opencfw_em9305_associated_schedule_insert_312da4(owner,0u)!=0u)
                    break;
            } else {
                if(opencfw_em9305_init_schedule_adjust_312f88(
                    owner,lower_bound,upper_bound)!=0u)break;
                uint32_t increment=rd(config+8u);
                uint32_t old_time=rd(owner+8u);
                wr(owner+8u,old_time+increment);
            }
        }
        if(rb(extended+14u)!=0u) {
            uint32_t handler=rb(0x805b18u);
            return opencfw_em9305_wsf_event_post(handler,1u<<14u);
        }
        return 0u;
    }
    if(mode!=1u)return mode;

    uint32_t initial_remaining=rd(config),captured=rd(owner+8u);
    uint32_t remaining=initial_remaining,continue_bit=1u;
    while(remaining!=0u && (continue_bit&1u)!=0u) {
        uint32_t maximum=rd(config+8u);
        uint32_t minimum=rd(config+4u);
        uint32_t success=opencfw_em9305_init_schedule_latest_3130d4(
            owner,minimum,maximum);
        uint32_t scheduled_time=rd(owner+8u); /* BRNE.D capture. */
        if(success==0u) {
            uint32_t increment=rd(config+8u);
            scheduled_time+=increment;
            wr(owner+8u,scheduled_time);
        }
        uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(
            scheduled_time,captured);
        uint32_t increment=rd(config+8u);
        uint32_t next=initial_remaining-elapsed;
        if((elapsed+increment)>=initial_remaining)next=0u; /* MOV.NC. */
        wr(config,next);
        remaining=next;
        continue_bit=success^1u; /* Native BXOR bit 0. */
    }
    uint32_t result=(~continue_bit)|(remaining!=0u);
    if((result&1u)!=0u)return result;
command_event:
    {
        uintptr_t event=opencfw_em9305_wsf_event_allocate(4u);
        if(event==0u)return 0u;
        wh(event+2u,1028u);
        uint32_t handler=rb(0x805b18u);
        return opencfw_em9305_wsf_task_message_send(handler,event);
    }
}
