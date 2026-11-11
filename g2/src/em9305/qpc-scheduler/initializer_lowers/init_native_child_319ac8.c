#include <stdint.h>

/* Native 0x319ac8..0x319de6: finish an extended-initiation connect attempt
 * for connection record conn. When the initiator is no longer active
 * (+0x8d4 == 0) the timer (+808) is stopped, the record released, the
 * failure status (0x43 once the retry limit +825 reaches +824) reported
 * through 30e774 and, with all of event mask bits 0x1d (+0x20), a
 * connection-complete event (323028) sent. Otherwise the received
 * AUX_CONNECT_RSP (+0x970) or, failing that, the stored AUX_CONNECT_REQ
 * (+0xa48) is unpacked; a resolvable TargetA with RxAdd set seeds the
 * local RPA (0x805be4) when it is still empty. A rejected response
 * (303404) sends message 776 for the PDU and releases the record.
 * Otherwise a 0x58-byte enhanced-connection-complete message is filled
 * (PDU copy at +4, peer identity/type +52/+60/+68, PHYs +53/+54, local
 * RPA +76, interval +48, latency +56, SCA +57) and sent to the LL task
 * (0x805b18), and the record is closed (319ea0). */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out,uintptr_t in);
extern uint32_t opencfw_em9305_init_transition_packet_copy_32dd54(uintptr_t out,
                                                                 uintptr_t in);
extern uint32_t opencfw_em9305_radio_packet_check_303404(uintptr_t pdu,
    uintptr_t context,uint32_t flags,uintptr_t target);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t request,uintptr_t context,
                                            uint32_t flags,uintptr_t target);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern void opencfw_em9305_child_319ea0(uintptr_t record);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t resource);
extern uint32_t opencfw_em9305_dispatch_child_30e774(uint32_t handle,
    uint32_t status,uint32_t zero);
extern uint32_t opencfw_em9305_mode_event_323028(uint32_t handle,uint32_t role,
    uint32_t status,uint32_t type,uint32_t low,uint32_t high,uint32_t a6,
    uint32_t a7,uint32_t a8,uint32_t a9,uint32_t a10,uint32_t a11,uint32_t a12,
    uint32_t a13);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task,
                                                     uintptr_t message);

struct opencfw_em9305_request_319ac8 {
    uint32_t adv_low,adv_high,target_low,target_high;
    uint8_t kind,flags,adv_type,target_type;
};

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

/* Seed the local resolvable address (0x805be4/0x805be8) from a TargetA
 * with RxAdd set when it is resolvable and none is stored yet. */
static int rpa_empty(void)
{
    return (r32(0x805be8u)|r32(0x805be4u))==0u;
}

/* Peer identity from the address block at b (+0/+4 peer, +8/+12 identity,
 * +18/+19 types): type +52 (bit 1 when the peer is not its identity),
 * identity +60/+64, and the peer RPA +68/+72 (zero when not distinct). */
static void peer_identity(uintptr_t message,uintptr_t b)
{
    uint32_t type=r8(b+19u);
    w8(message+52u,type);
    uint32_t distinct=r8(b+19u)!=r8(b+18u)||r32(b)!=r32(b+8u)||
                      r32(b+4u)!=r32(b+12u);
    if(distinct)w8(message+52u,type|2u);
    w32(message+72u,0u);
    w32(message+68u,0u);
    w32(message+60u,r32(b+8u));
    w32(message+64u,r32(b+12u));
    if(r8(b+19u)!=r8(b+18u)||r32(b)!=r32(b+8u)||r32(b+4u)!=r32(b+12u)){
        w32(message+68u,r32(b));
        w32(message+72u,r32(b+4u));
    }
}

void opencfw_em9305_child_319ac8(uintptr_t conn)
{
    uint8_t header[5];
    uint32_t packet[11];
    struct opencfw_em9305_request_319ac8 request;
    uintptr_t timer=conn+808u;
    uintptr_t aux=conn+0x908u;
    uintptr_t peer=aux+132u;
    uintptr_t pdu;
    if(r8(conn+0x8d4u)==0u){
        uint32_t status;
        (void)opencfw_em9305_wsf_timer_stop(timer);
        opencfw_em9305_child_319ea0(conn);
        (void)opencfw_em9305_common_release_304588(1u);
        uint32_t limit=r8(timer+16u);
        if(limit!=0u&&r8(timer+17u)>=limit){
            w8(timer+18u,0x43u);
            status=0x43u;
        }else{
            status=r8(timer+18u);
        }
        (void)opencfw_em9305_dispatch_child_30e774(r8(conn+1u),status,0u);
        if((r16(conn+0x20u)&0x1du)!=0x1du)return;
        (void)opencfw_em9305_mode_event_323028(r8(conn+1u),1u,0u,r8(conn+58u),
            r32(conn+48u),r32(conn+52u),0u,0u,0u,0u,0x3cu,0u,0xffu,0xffffu);
        return;
    }
    pdu=r32(aux+104u);
    if(pdu!=0u){
        uint32_t used=opencfw_em9305_child_32db0c((uintptr_t)header,pdu);
        (void)opencfw_em9305_init_transition_packet_copy_32dd54((uintptr_t)packet,
                                                                pdu+used);
        uint32_t accepted=opencfw_em9305_radio_packet_check_303404(pdu,
            conn+0x954u,1u,peer);
        if(header[3]!=0u){
            uint32_t high=packet[3];
            if((high&0xc000u)==0x4000u&&rpa_empty()){
                w32(0x805be8u,high);
                w32(0x805be4u,packet[2]);
            }
        }
        if(accepted==0u)goto reject;
    }else{
        pdu=r32(conn+0xa48u);
        if(pdu!=0u){
            uint32_t used=opencfw_em9305_child_32db0c((uintptr_t)header,pdu);
            (void)opencfw_em9305_init_transition_packet_copy_32dd54(
                (uintptr_t)packet,pdu+used);
            uint32_t target_type=header[3];
            uint32_t high=packet[3];
            uint32_t low=packet[2];
            request.adv_low=packet[0];
            request.adv_high=packet[1];
            request.target_low=low;
            request.target_high=high;
            request.kind=header[0];
            request.flags=3u;
            request.adv_type=header[2];
            request.target_type=(uint8_t)target_type;
            if(target_type!=0u&&(high&0xc000u)==0x4000u&&rpa_empty()){
                w32(0x805be4u,low);
                w32(0x805be8u,high);
            }
            (void)opencfw_em9305_child_30301c((uintptr_t)&request,conn+0x954u,1u,
                                              conn+0xa8cu);
        }
    }
    {
        uintptr_t message=opencfw_em9305_wsf_event_allocate(0x58u);
        if(message==0u)goto reject;
        w8(message+2u,0u);
        w16(message,r8(conn+1u));
        uint32_t used=opencfw_em9305_child_32db0c((uintptr_t)packet,pdu);
        (void)opencfw_em9305_init_transition_packet_copy_32dd54(message+4u,
                                                                pdu+used);
        if(r32(aux+104u)!=0u){
            peer_identity(message,peer);
            w8(message+54u,1u);
        }else{
            peer_identity(message,conn+0xa8cu);
            w8(message+54u,r8(conn+0x9e1u));
        }
        w8(message+55u,1u);
        w16(message+86u,0xffffu);
        w8(message+84u,0xffu);
        w32(message+80u,r32(0x805be8u));
        w32(message+76u,r32(0x805be4u));
        uintptr_t params=conn+0x8d0u;
        w32(message+48u,r32(params));
        w8(message+53u,r8(params+5u));
        w8(message+56u,r8(timer+17u));
        w8(message+57u,r8(params-4u));
        (void)opencfw_em9305_wsf_task_message_send(r8(0x805b18u),message);
        opencfw_em9305_child_319ea0(conn);
        return;
    }
reject:
    w16(pdu-2u,776u);
    w16(pdu-4u,r8(conn+1u));
    (void)opencfw_em9305_wsf_task_message_send(r8(0x805b18u),pdu-4u);
    (void)opencfw_em9305_common_release_304588(1u);
}
