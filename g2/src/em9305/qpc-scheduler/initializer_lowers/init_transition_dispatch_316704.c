#include <stdint.h>

extern uint32_t opencfw_em9305_radio_packet_check_303404(
    uint32_t,uintptr_t,uint32_t,uintptr_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_init_transition_packet_copy_32dd54(
    uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_transition_packet_check_32e278(uintptr_t);
extern uint32_t opencfw_em9305_ll_stream_address_busy_318200(
    uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_init_transition_gate_3168e4(void);
extern uintptr_t opencfw_em9305_init_transition_refresh_327dbc(void);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

static uint8_t rd8(uintptr_t p) { return *(volatile uint8_t *)p; }
static uint32_t rd32(uintptr_t p) { return *(volatile uint32_t *)p; }
static void wr8(uintptr_t p,uint32_t v) { *(volatile uint8_t *)p=(uint8_t)v; }
static void wr16(uintptr_t p,uint32_t v) { *(volatile uint16_t *)p=(uint16_t)v; }
static void wr32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }

/* Prepared complete 0x316704..0x316892, with native 40-byte frame supplied
 * by the ARC entry below.  Every child remains a genuine source identity. */
uint32_t opencfw_em9305_init_transition_dispatch_316704_body(uint8_t *frame)
{
    if(rd8(0x805a71u)==0u) return 0u;
    uint8_t state=rd8(0x8052fcu);
    const uintptr_t config=0x805b84u;
    if(state==0u) {
        (void)opencfw_em9305_init_transition_refresh_327dbc();
        if(rd8(config+12u)==1u) {
            (void)opencfw_em9305_memset(frame,0u,36u);
            uint8_t option=rd8(config+14u);
            uint32_t high=rd32(config+20u);
            uint32_t low=rd32(config+16u);
            frame[4]=60u;
            frame[2]=5u;frame[3]=60u;
            frame[9]=option;
            frame[8]=1u;
            frame[36]=0xffu;frame[37]=0xffu;
            frame[35]=0xffu;
            (void)opencfw_em9305_radio_address_write_3045e8(
                (uintptr_t)(frame+10u),low,high);
            (void)opencfw_em9305_ll_event_callback_30e79c((uintptr_t)frame);
        }
        (void)opencfw_em9305_common_release_304588(1u);
        return opencfw_em9305_init_transition_gate_3168e4();
    }

    /* LD.AB at 31672e advances R15 from 0x805398 to 0x8053b4. */
    const uintptr_t snapshot=0x8053b4u;
    uintptr_t packet=rd32(0x805398u);
    if(packet==0u) return opencfw_em9305_init_transition_gate_3168e4();
    uint32_t check=opencfw_em9305_radio_packet_check_303404(
        (uint32_t)packet,0x80537cu,1u,snapshot);
    uint32_t fail=check^1u; /* Native BXOR bit zero. */
    uintptr_t event=opencfw_em9305_wsf_event_allocate(88u);
    if(event!=0u) {
        /* BL delay captures pre-call R0 (event+4) in R19.  The following
         * child receives that pointer, not the copy child's return value. */
        (void)opencfw_em9305_init_transition_packet_copy_32dd54(
            event+4u,packet+2u);
        if(opencfw_em9305_init_transition_packet_check_32e278(event+4u)==0u)
            fail=1u;
    }
    if(event==0u) {
        if(fail!=0u) goto error_event;
        return opencfw_em9305_init_transition_gate_3168e4();
    }
    if(fail!=0u) goto error_event;

    const uintptr_t advertised=0x8053bcu;
    uint8_t advertised11=rd8(advertised+11u);
    uint32_t first_high=rd32(advertised+16u);
    wr8(event+2u,0u);
    wr8(event+52u,advertised11);
    wr32(event+48u,first_high);
    uint8_t second11=rd8(advertised+11u);
    uint8_t advertised10=rd8(advertised+10u);
    uint32_t flags=advertised11;
    uint32_t high,low;
    if(second11!=advertised10) {
        flags|=2u;
        wr8(event+52u,flags);
        high=rd32(advertised+4u);
        low=rd32(advertised);
        /* Native mismatch arm rereads the two descriptor bytes. */
        advertised10=rd8(advertised+10u);
        second11=rd8(advertised+11u);
    } else {
        uint32_t a=rd32(snapshot+4u),b=rd32(snapshot+12u);
        uint32_t c=rd32(snapshot),d=rd32(snapshot+8u);
        if(((a^b)|(c^d))!=0u) {
            flags|=2u;
            wr8(event+52u,flags);
            high=rd32(advertised+4u);
            low=rd32(advertised);
            advertised10=rd8(advertised+10u);
            second11=rd8(advertised+11u);
        } else {
            high=b;
            low=d;
        }
    }
    wr32(event+72u,0u);
    wr32(event+68u,0u);
    wr32(event+60u,low);
    wr32(event+64u,high);
    uint32_t sampled_high=rd32(snapshot+4u);
    uint32_t sampled_low=rd32(snapshot); /* Native BRNE delay slot. */
    uint32_t different=second11!=advertised10;
    if(!different) {
        uint32_t compare_high=rd32(snapshot+12u);
        uint32_t compare_low=rd32(snapshot+8u);
        different=((compare_high^sampled_high)|
            (compare_low^sampled_low))!=0u;
    }
    if(different) {
        wr32(event+68u,sampled_low);
        wr32(event+72u,sampled_high);
    }
    if(opencfw_em9305_ll_stream_address_busy_318200(flags,low,high)!=0u)
        goto error_event;
    wr16(event+86u,0xffffu);
    wr8(event+84u,0xffu);
    wr8(event+57u,0u);
    wr16(event+54u,1u);
    uint32_t product100=rd32(config+100u);
    uint8_t state2=rd8(0x8052feu);
    wr32(event+80u,product100);
    uint32_t product96=rd32(config+96u);
    uint8_t handler=rd8(0x805b18u);
    wr8(event+53u,state2);
    wr32(event+76u,product96);
    (void)opencfw_em9305_wsf_task_message_send(handler,event);
    return opencfw_em9305_init_transition_gate_3168e4();

error_event:
    if(event!=0u)(void)opencfw_em9305_wsf_event_release(event);
    event=opencfw_em9305_wsf_event_allocate(4u);
    if(event!=0u) {
        wr16(event+2u,772u);
        uint8_t handler=rd8(0x805b18u);
        (void)opencfw_em9305_wsf_task_message_send(handler,event);
    }
    (void)opencfw_em9305_common_release_304588(1u);
    return opencfw_em9305_init_transition_gate_3168e4();
}

#ifdef __arc__
__asm__(
".text\n.balign 4\n.global opencfw_em9305_init_transition_dispatch_316704\n"
".type opencfw_em9305_init_transition_dispatch_316704,@function\n"
"opencfw_em9305_init_transition_dispatch_316704:\n"
"enter_s [r13-r19,fp,blink]\nsub_s sp,sp,0x28\n"
"mov r0,sp\nbl opencfw_em9305_init_transition_dispatch_316704_body\n"
"leave_s [r13-r19,fp,blink,pcl]\n"
".size opencfw_em9305_init_transition_dispatch_316704,. - opencfw_em9305_init_transition_dispatch_316704\n");
#else
uint32_t opencfw_em9305_init_transition_dispatch_316704(void)
{
    uint8_t frame[40] __attribute__((aligned(4)));
    return opencfw_em9305_init_transition_dispatch_316704_body(frame);
}
#endif
