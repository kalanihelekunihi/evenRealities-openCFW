#include <stdint.h>

/* Native 0x312918..0x312b86: compute the air-time reservation of an
 * associated scheduling object (descriptor at +44, result stored at +12)
 * from the descriptor kind (+0): 2 legacy advertising, 3 legacy events
 * on the enabled channels (+127), 6 extended/auxiliary events (with the
 * 0x4290 offset at +16 for coded PHY), 7 data with `length` (or 244)
 * bytes split into PDUs of the connection's maximum, 8/9 periodic events
 * through 312be4. Packet times come from 312b88 (PHY +12, options
 * +14/+15, lengths +124/+149/+100) plus fixed IFS/turnaround constants.
 * Other kinds reserve 0. */
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy, uint32_t coded, uint32_t length);
extern uint32_t opencfw_em9305_auxiliary_guard_interval(void);
extern uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t window);
extern uint32_t opencfw_em9305_radio_duration_312be4(uint32_t,uint32_t,uint32_t,uint32_t,
                                                     uint32_t,uint32_t,uint32_t,uint32_t);

static uint32_t opencfw_em9305_phy_tail_312918(uint32_t phy)
{
    if(phy==2u)return 1214u;
    if(phy==3u)return 0x4326u;
    return 2270u;
}

void opencfw_em9305_associated_object_init_312918(uintptr_t object, uint32_t length)
{
    uintptr_t d=*(volatile uint32_t *)(object+44u);
    volatile uint8_t *d8=(volatile uint8_t *)d;
    uint32_t total=0u;
    switch(d8[0]){
    case 2u:{
        uint32_t phy=d8[13];
        total=phy==3u?0xc10u:376u;
        if(*(volatile uint32_t *)(d+104u)==0u)break;
        total+=opencfw_em9305_radio_duration_piece_312b88(d8[12],0u,d8[149])+150u;
        if(*(volatile uint32_t *)(d+108u)==0u)break;
        total+=phy!=3u?526u:3238u;
        break;
    }
    case 3u:{
        uint32_t packet=opencfw_em9305_radio_duration_piece_312b88(d8[12],d8[14],d8[124]);
        uint32_t channels=d8[127];
        uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
        uint32_t spacing=opencfw_em9305_channel_timing_adjust_312c5c(guard+packet);
        uint32_t count=(channels&1u)+((channels>>1)&1u)+((channels>>2)&1u);
        total=(count-1u)*spacing+packet;
        if(*(volatile uint32_t *)(d+104u)==0u)break;
        uint32_t base=d8[13]==3u?0xc10u:376u;
        uint32_t turnaround=count*150u;
        total+=turnaround+base*count;
        if(*(volatile uint32_t *)(d+108u)==0u)break;
        uint32_t response=opencfw_em9305_radio_duration_piece_312b88(d8[12],0u,d8[149]);
        total+=turnaround+(uint32_t)((int32_t)response*(int16_t)count);
        break;
    }
    case 6u:{
        uint32_t extended=d8[132];
        uint32_t phy=d8[13];
        if(extended!=0u){
            if(phy==3u){
                total=720u;
                *(volatile uint32_t *)(object+16u)=0x4290u;
            }else{
                total=phy==2u?0x2cu:0x50u;
            }
            if(*(volatile uint32_t *)(d+100u)==0u)break;
            uint32_t coded=d8[15];
            uint32_t packet=opencfw_em9305_radio_duration_piece_312b88(d8[12],coded==0u?2u:coded,0x24u);
            total+=phy==3u?1916u:(phy==2u?400u:492u);
            total+=packet;
        }else{
            if(phy==3u){
                total=0xed0u;
                *(volatile uint32_t *)(object+16u)=0x4290u;
            }else{
                total=phy==2u?0xecu:464u;
            }
            if(*(volatile uint32_t *)(d+100u)==0u)break;
            uint32_t coded=d8[15];
            total+=opencfw_em9305_radio_duration_piece_312b88(d8[12],coded==0u?2u:coded,d8[124]);
            total+=150u+opencfw_em9305_phy_tail_312918(phy);
        }
        break;
    }
    case 7u:{
        uint32_t limit=length,unit=length;
        if(length==0u){
            limit=244u;
            unit=241u;
        }
        if(*(volatile uint32_t *)(d+116u)!=0u){
            total=opencfw_em9305_radio_duration_piece_312b88(d8[12],d8[14],0xdu);
            total+=opencfw_em9305_phy_tail_312918(d8[13])+150u;
        }
        uintptr_t pending=*(volatile uint32_t *)(object+40u);
        uint32_t bytes=pending!=0u?*(volatile uint16_t *)pending:0u;
        uint32_t options=d8[14];
        uint32_t phy=d8[12];
        if(limit>=bytes){
            int32_t minimum=*(volatile uint16_t *)(d+100u);
            if(minimum<0xd)minimum=0xd;
            total+=opencfw_em9305_radio_duration_piece_312b88(phy,options,(uint16_t)(bytes+(uint32_t)minimum));
            break;
        }
        uint32_t full=opencfw_em9305_radio_duration_piece_312b88(phy,options,unit+16u);
        uint32_t packets=bytes/unit;
        uint32_t covered=(uint32_t)((int32_t)(int16_t)unit*(int16_t)packets);
        uint32_t rest=bytes-covered;
        total+=(full+300u)*packets;
        if((uint16_t)rest==0u)break;
        total+=opencfw_em9305_radio_duration_piece_312b88(phy,options,(uint16_t)(rest+13u));
        break;
    }
    case 8u:{
        uintptr_t pending=*(volatile uint32_t *)(object+40u);
        int32_t bytes=64;
        if(pending!=0u){
            bytes=*(volatile uint16_t *)pending;
            if(bytes<64)bytes=64;
        }
        total=opencfw_em9305_radio_duration_312be4(d8[12],0u,0u,0u,(uint32_t)bytes,0u,d8[14],0u);
        break;
    }
    case 9u:
        total=opencfw_em9305_radio_duration_312be4(d8[12],0u,0u,0u,0u,0u,d8[14],0u);
        break;
    default:
        break;
    }
    *(volatile uint32_t *)(object+12u)=total;
}
