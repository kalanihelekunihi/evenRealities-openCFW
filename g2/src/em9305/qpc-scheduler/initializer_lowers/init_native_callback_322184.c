#include <stdint.h>

/* Native 0x322184..0x32233c: start PAwR sync (subevent-aware variant of
 * 321490) on the sync context (*0x8051b8) from a SyncInfo: load and
 * transform the channel map (+644), CRC seed (+692), first channel seeded
 * by event counter (+248) xor the subevent counter of the PAwR block
 * (+780 -> byte +18), PHY, anchor and receive window (+168 from +508).
 * When the anchor is at least 300 us away, schedule it, stepping one
 * subevent at a time (wrapping to the next event after +512 subevents;
 * offset = interval +252 * event + subevent * spacing +513 * 1.25 ms)
 * until the scheduler accepts, and mark the sync pending (0x8051a5). */
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

void opencfw_em9305_callback_322184(uintptr_t receiver,uintptr_t request,uintptr_t info,
                                    uint32_t reference)
{
    uintptr_t sync=r32(0x8051b8u);
    w32(sync+644u,r32(info+8u));
    w32(sync+648u,r32(info+0xcu));
    w8(sync+690u,1u);
    (void)opencfw_em9305_radio_channel_transform_30e3fc(sync+644u);
    uintptr_t pawr=r32(sync+780u);
    uint32_t access=r32(info+0x14u);
    uint32_t counter=r16(sync+248u);
    uint32_t subevent=r8(pawr+0x12u);
    w16(sync+692u,access^(access>>16));
    uint32_t channel=opencfw_em9305_associated_channel_seed_324c98(sync+644u,subevent^counter);
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
    pawr=r32(sync+780u);
    w32(sync+272u,offset+reference);
    w32(sync+0x64u,r32(info+0x14u));
    w32(sync+168u,r32(sync+508u));
    w32(sync+0x68u,r32(info+0x18u));
    w16(sync+276u,r16(sync+248u));
    w8(sync+109u,phy);
    w8(sync+108u,phy);
    w16(pawr+364u,r8(pawr+0x12u));
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
    w32(sync+68u,interval);
    uintptr_t compare=(uintptr_t)opencfw_em9305_init_secondary_compare_3249e8;
    while(opencfw_em9305_associated_schedule_insert_312da4(sync+0x30u,compare)==0u) {
        pawr=r32(sync+780u);
        uint32_t next=r8(pawr+0x12u)+1u;
        w8(pawr+0x12u,next);
        uint32_t limit=r8(sync+512u);
        counter=r16(sync+248u);
        if((next&0x7fu)==limit) {
            next=0u;
            counter+=1u;
            w8(pawr+18u,0u);
            w16(sync+248u,counter);
        }
        channel=opencfw_em9305_associated_channel_seed_324c98(sync+644u,
            (uint16_t)(counter^(uint8_t)next));
        pawr=r32(sync+780u);
        uint32_t spacing=r8(sync+513u);
        uint32_t event=r16(sync+248u);
        interval=r32(sync+252u);
        subevent=r8(pawr+0x12u);
        w8(sync+97u,channel);
        uint32_t advance=interval*event+(uint16_t)spacing*(uint16_t)subevent*1250u;
        uint32_t drift=opencfw_em9305_init_secondary_time_317ebc(advance,accuracy);
        uint32_t anchor=advance-drift+r32(sync+272u);
        uint32_t duration=r32(sync+264u)+drift;
        window=r32(sync+268u)+(drift<<1);
        w32(sync+0x38u,anchor);
        w32(sync+0x3cu,duration);
        w32(sync+204u,window);
    }
    w8(0x8051a5u,1u);
}
