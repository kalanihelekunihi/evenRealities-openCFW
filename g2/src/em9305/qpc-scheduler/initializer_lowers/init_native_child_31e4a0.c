#include <stdint.h>

/* Native 0x31e4a0..0x31e5ec: connection state machine event (state +1).
 * State 0 (initiating): connect-complete 0x3f runs the setup children,
 * raises the feature/PHY events (0x66/0x67/0x68, from flags +4 and the
 * data length +570/+572) and reports the new connection through 323028
 * with the pending connect command (*0x805c6c), moving to state 2. State 2
 * forwards events other than 0x3d/0x3f/0x47/0x48 to 3212f0 (0x3d goes to
 * 32279c). State 3 handles 0x51 (clear pending procedure +640/+636 bit 0,
 * 32cadc, clear +620). In every state 0x4c tears down via 31ac3c/3231c4
 * and 0x4d (and 0x4c) drop the schedule entry and release the connection;
 * everything else ends in 318edc. */
extern uint32_t opencfw_em9305_mode_event_32279c(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_322b70(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32c978(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_event_323028(uint32_t,uint32_t,uintptr_t,uint32_t,uint32_t,
                                                 uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,
                                                 uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_3212f0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t);
extern uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t);
extern uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_318edc(uintptr_t,uint32_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}

static uint32_t index_31e4a0(uintptr_t record)
{
    uint32_t base=r32(0x805c70u);
    return (uint8_t)((int32_t)((uint32_t)record-base)/912);
}

static void connect_complete_31e4a0(uintptr_t record)
{
    (void)opencfw_em9305_mode_event_322b70(record);
    (void)opencfw_em9305_mode_event_32c978(record);
    uint32_t features=r32(record+4u);
    if(features&1u) {
        (void)opencfw_em9305_mode_event_31bd78(record,0x66u);
        features=r32(record+4u);
    }
    if(features&0x100u) {
        (void)opencfw_em9305_mode_event_31bd78(record,0x67u);
        features=r32(record+4u);
    }
    if((features&0x40u)&&(r16(record+570u)>=0x1cu||r16(record+572u)>=329u))
        (void)opencfw_em9305_mode_event_31bd78(record,0x68u);
    uintptr_t command=r32(0x805c6cu);
    uint32_t value892=r16(record+892u);
    uint32_t value321=r8(record+321u);
    uint32_t value890=r8(record+890u);
    (void)opencfw_em9305_mode_event_323028(index_31e4a0(record),0u,command+4u,
        r8(command+52u),r32(command+60u),r32(command+64u),r32(command+68u),
        r32(command+72u),r32(command+0x4cu),r32(command+0x50u),0u,value321,value890,value892);
    *(volatile uint8_t *)(record+1u)=2u;
}

uint32_t opencfw_em9305_child_31e4a0(uintptr_t record,uint32_t event)
{
    uint32_t state=r8(record+1u);
    uint32_t teardown=0u,release=0u;
    if(state==0u) {
        if(event==0x4du) release=1u;
        else if(event==0x4cu) teardown=1u;
        else if(event==0x3fu) connect_complete_31e4a0(record);
    } else if(state==3u) {
        if(event==0x4cu) teardown=1u;
        else if(event==0x4du) release=1u;
        else if(event==0x51u) {
            uint32_t pending=r32(record+636u);
            *(volatile uint32_t *)(record+640u)=0u;
            *(volatile uint32_t *)(record+636u)=pending&~1u;
            (void)opencfw_em9305_mode_event_32cadc(record);
            *(volatile uint8_t *)(record+620u)=0u;
        }
    } else {
        uint32_t forward=1u;
        if(state==2u) {
            if(event-71u<2u||event==0x3fu) {
                forward=0u;
            } else if(event==0x3du) {
                (void)opencfw_em9305_mode_event_32279c(record);
                forward=0u;
            } else {
                (void)opencfw_em9305_mode_event_3212f0(record,event);
            }
        }
        if(forward) {
            if(event==0x4du) release=1u;
            else if(event==0x4cu) teardown=1u;
        }
    }
    if(teardown) {
        (void)opencfw_em9305_mode_event_31ac3c(record);
        (void)opencfw_em9305_mode_event_3231c4(record);
        release=1u;
    }
    if(release) {
        (void)opencfw_em9305_associated_schedule_drop_3136ac(index_31e4a0(record));
        return opencfw_em9305_init_connection_release_31ad90(record);
    }
    return opencfw_em9305_mode_event_318edc(record,event);
}
