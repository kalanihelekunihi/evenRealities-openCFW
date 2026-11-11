#include <stdint.h>

/* Native 0x321490..0x321608: start periodic-advertising sync on the sync
 * context (*0x8051b8) from a SyncInfo (third argument): load and transform
 * the channel map (+644), derive the CRC seed (+692) and first channel
 * (+97, plus the receiver's byte +177 at +98 when flag 0x40 of +154 is
 * set), the PHY (+108/+109 from the sync request byte +6), the anchor
 * (offset in 30/300 us units plus 0x258000 per wrap bit, + reference
 * time) and the widened receive window. When the anchor is at least 300
 * us away, schedule it, advancing event by event (new channel, interval
 * +252 times the skip count) until the scheduler accepts, and mark the
 * sync pending (0x8051a5). */
extern uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_pal_elapsed_raw(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_init_secondary_compare_3249e8(uintptr_t,uintptr_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

void opencfw_em9305_child_321490(uintptr_t receiver,uintptr_t request,uintptr_t info,
                                 uint32_t reference)
{
    uintptr_t sync=r32(0x8051b8u);
    w32(sync+644u,r32(info+8u));
    w32(sync+648u,r32(info+0xcu));
    w8(sync+690u,1u);
    (void)opencfw_em9305_radio_channel_transform_30e3fc(sync+644u);
    uint32_t access=r32(info+0x14u);
    uint32_t counter=r16(sync+248u);
    w16(sync+692u,access^(access>>16));
    uint32_t channel=opencfw_em9305_associated_channel_seed_324c98(sync+644u,counter);
    uint32_t flags=r8(receiver+154u);
    w8(sync+97u,channel);
    if(flags&0x40u) w8(sync+98u,r8(receiver+177u));
    uint32_t phy_code=r8(request+6u);
    uint32_t large=r8(info+2u);
    uint32_t wraps=r8(info+3u);
    uint32_t offset=r16(info);
    uint32_t phy=(phy_code==2u)?3u:(phy_code==1u)+1u;
    uint32_t unit=(large==0u)?30u:300u;
    offset=wraps*0x258000u+unit*offset;
    w32(sync+272u,offset+reference);
    w32(sync+0x64u,r32(info+0x14u));
    w32(sync+0x68u,r32(info+0x18u));
    w16(sync+276u,r16(sync+248u));
    w8(sync+109u,phy);
    w8(sync+108u,phy);
    uint32_t accuracy=opencfw_em9305_mode_callback_child_317ea4(r8(info+0x10u));
    unit=(r8(info+2u)==0u)?30u:300u;
    uint32_t widening=opencfw_em9305_init_secondary_time_317ebc(unit+offset,accuracy);
    uint32_t elapsed=opencfw_em9305_pal_elapsed_raw(offset,widening);
    unit=(r8(info+2u)==0u)?30u:300u;
    uint32_t window=unit+(widening<<1);
    w32(sync+268u,window);
    w32(sync+204u,window);
    if(elapsed<300u) return;
    w32(sync+0x38u,elapsed+reference);
    uint32_t piece=opencfw_em9305_radio_duration_piece_312b88(r8(sync+109u),0u,1u);
    uint32_t interval=r32(sync+252u);
    w32(sync+264u,piece);
    w32(sync+0x3cu,piece);
    w32(sync+0x44u,interval);
    uintptr_t compare=(uintptr_t)opencfw_em9305_init_secondary_compare_3249e8;
    uint32_t busy=opencfw_em9305_associated_schedule_insert_312da4(sync+0x30u,compare);
    for(uint32_t skip=1u;busy==0u;++skip) {
        uint32_t next=r16(sync+248u)+1u;
        w16(sync+248u,next);
        channel=opencfw_em9305_associated_channel_seed_324c98(sync+644u,(uint16_t)next);
        interval=r32(sync+252u);
        w8(sync+97u,channel);
        uint32_t advance=interval*(skip&0xffffu);
        uint32_t drift=opencfw_em9305_init_secondary_time_317ebc(advance,accuracy);
        uint32_t anchor=r32(sync+272u)+(advance-drift);
        uint32_t duration=r32(sync+264u)+drift;
        window=r32(sync+268u)+(drift<<1);
        w32(sync+0x38u,anchor);
        w32(sync+0x3cu,duration);
        w32(sync+204u,window);
        busy=opencfw_em9305_associated_schedule_insert_312da4(sync+0x30u,compare);
    }
    w8(0x8051a5u,1u);
}
