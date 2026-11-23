#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31ff68..0x32003a: extended-initiator message handler. The
 * event (+3) goes to the initiator state machine (32003c) of the record
 * addressed by the handle (+0) if it is pending in ((uintptr_t)&em9305_ram_802a2c + 0x32u), or to every
 * pending record when the handle is 255, the event is 1 or 2, or byte +2
 * is 255. For event 1 (create), each pending record creates its
 * connection (31a5bc) from the create parameters (*((uintptr_t)&em9305_ram_805c5c + 0x1cu): peer type +6,
 * address +8/+12, role +4, PHY +5), stopping at the first failure; when
 * all succeed the peer is stored at ((uintptr_t)&em9305_ram_802a2c + 0x28u)..((uintptr_t)&em9305_ram_802a2c + 0x30u), the done mask
 * ((uintptr_t)&em9305_ram_802a2c + 0x31u) is cleared and each pending record transfers its connection
 * (31dd88 into its +88 connection) and starts (3202e0). */
extern uint8_t *const opencfw_em9305_ext_init_records_3357a8[3];
extern uint32_t opencfw_em9305_child_32003c(uintptr_t machine,uint32_t event);
extern uint32_t opencfw_em9305_child_31a5bc(uintptr_t link,uint32_t peer_type,
    uint32_t peer_low,uint32_t peer_high,uint32_t role,uint32_t phy);
extern uint32_t opencfw_em9305_radio_transfer_31dd88(uintptr_t slot,
    uintptr_t input,uintptr_t source);
extern uint32_t opencfw_em9305_child_3202e0(uintptr_t record);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
#define RECORD(i) ((uintptr_t)opencfw_em9305_ext_init_records_3357a8[(i)])

void opencfw_em9305_callback_31ff68(uintptr_t message)
{
    uint32_t handle=*(volatile uint16_t *)message;
    uint32_t event=r8(message+3u);
    uint32_t pending=r8(((uintptr_t)&em9305_ram_802a2c + 0x32u));
    if(handle!=255u&&event-1u>=2u&&r8(message+2u)!=255u){
        if(((pending>>(handle&31u))&1u)!=0u)
            (void)opencfw_em9305_child_32003c(RECORD(handle),event);
    }else{
        for(uint32_t index=0u;index<3u;++index){
            if(((pending>>index)&1u)==0u)continue;
            (void)opencfw_em9305_child_32003c(RECORD(index),event);
            pending=r8(((uintptr_t)&em9305_ram_802a2c + 0x32u));
        }
    }
    if(r8(message+3u)!=1u)return;
    pending=r8(((uintptr_t)&em9305_ram_802a2c + 0x32u));
    uintptr_t create=r32(((uintptr_t)&em9305_ram_805c5c + 0x1cu));
    for(uint32_t index=0u;index<3u;++index){
        if(((pending>>index)&1u)==0u)continue;
        if(opencfw_em9305_child_31a5bc(RECORD(index),r8(create+6u),r32(create+8u),
                                       r32(create+12u),r8(create+4u),
                                       r8(create+5u))!=0u)return;
        pending=r8(((uintptr_t)&em9305_ram_802a2c + 0x32u));
    }
    uint32_t high=r32(create+12u),low=r32(create+8u);
    uint32_t type=r8(create+6u);
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_802a2c + 0x31u)=0u;
    *(volatile uint32_t *)((uintptr_t)&em9305_ram_802a2c + 0x2cu)=high;
    *(volatile uint32_t *)((uintptr_t)&em9305_ram_802a2c + 0x28u)=low;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_802a2c + 0x30u)=(uint8_t)type;
    for(uint32_t index=0u;index<3u;++index){
        if(((pending>>index)&1u)==0u)continue;
        uintptr_t record=RECORD(index);
        uintptr_t connection=r32(((uintptr_t)&em9305_ram_805c5c + 0x14u))
                             +*(volatile uint16_t *)(record+88u)*912u;
        (void)opencfw_em9305_radio_transfer_31dd88(connection,record+36u,0u);
        (void)opencfw_em9305_child_3202e0(record);
        pending=r8(((uintptr_t)&em9305_ram_802a2c + 0x32u));
    }
}
