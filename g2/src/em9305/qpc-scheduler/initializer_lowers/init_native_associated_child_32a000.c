#include <stdint.h>

/* Native 0x32a000..0x32a216: slave link-layer control dispatcher for the
 * connection record. In state 0 (+1) a connection-indication (0x0b)
 * finishes setup (329610, 32c978), raises the pending procedures from the
 * link features word (+4: bit 0 -> 0x66, bit 8 -> 0x67, bit 6 with a data
 * length above the defaults (+570 >= 28 or +572 >= 329) -> 0x68), or with
 * bit 9 defers them into +644, enters state 2 (or 1 when deferred) and
 * reports the connection complete event (323028) with the config
 * (*0x805c6c) parameters. In state 1 the procedure-start opcodes set
 * their bit in both +644 and +636 (0x15 bit 17, 0x1b..0x23 bits 2..7,
 * 21), 0x40 terminates (reason 0x70, state 2), 0x3d and 0x47/0x48 are
 * ignored and others go to 32b210. In state 2 every opcode except 0x3d,
 * 0x47 and 0x48 goes to 32b210; state 3 handles 0x51 by clearing bit 0
 * of +636 and +640 and the pending byte +620 (32cadc). Every call ends in
 * mode event 318edc with the opcode. */
extern uint32_t opencfw_em9305_associated_child_329610(uintptr_t link);
extern uint32_t opencfw_em9305_mode_event_32c978(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t context,uint32_t event);
extern uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t context);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t record,
                                                        uint32_t reason);
extern uint32_t opencfw_em9305_child_32b210(uintptr_t record,uint32_t opcode);
extern uint32_t opencfw_em9305_mode_event_318edc(uintptr_t context,uint32_t event);
extern uint32_t opencfw_em9305_mode_event_323028(uint32_t handle,uint32_t role,
    uintptr_t record,uint32_t peer_type,uint32_t peer_low,uint32_t peer_high,
    uint32_t peer_rpa_low,uint32_t peer_rpa_high,uint32_t local_rpa_low,
    uint32_t local_rpa_high,uint32_t status,uint32_t follow_up,
    uint32_t clock_accuracy,uint32_t timeout);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void set_both(uintptr_t record,uint32_t bit)
{
    uint32_t pending=r32(record+644u)|bit;
    uint32_t active=r32(record+636u)|bit;
    *(volatile uint32_t *)(record+644u)=pending;
    *(volatile uint32_t *)(record+636u)=active;
}

static void connection_setup(uintptr_t record)
{
    uintptr_t lengths=record+570u;
    uint32_t state;
    (void)opencfw_em9305_associated_child_329610(record);
    (void)opencfw_em9305_mode_event_32c978(record);
    uint32_t features=r32(record+4u);
    if((features&0x200u)!=0u){
        if((features&1u)!=0u)*(volatile uint32_t *)(record+644u)=r32(record+644u)|8u;
        if((features&0x100u)!=0u)*(volatile uint32_t *)(record+644u)=r32(record+644u)|4u;
        state=1u;
        if((features&0x40u)!=0u&&(r16(lengths)>=0x1cu||r16(lengths+2u)>=329u))
            *(volatile uint32_t *)(record+644u)=r32(record+644u)|0x10u;
    }else{
        if((features&1u)!=0u){
            (void)opencfw_em9305_mode_event_31bd78(record,0x66u);
            features=r32(record+4u);
        }
        if((features&0x100u)!=0u){
            (void)opencfw_em9305_mode_event_31bd78(record,0x67u);
            features=r32(record+4u);
        }
        state=2u;
        if((features&0x40u)!=0u&&(r16(lengths)>=0x1cu||r16(lengths+2u)>=329u))
            (void)opencfw_em9305_mode_event_31bd78(record,0x68u);
    }
    uintptr_t base=r32(0x805c70u);
    uintptr_t config=r32(0x805c6cu);
    int32_t handle=(int32_t)(record-base)/912;
    *(volatile uint8_t *)(record+1u)=(uint8_t)state;
    uint32_t accuracy=r8(record+321u);
    uint32_t timeout=r16(record+892u);
    uint32_t follow=r8(record+890u);
    (void)opencfw_em9305_mode_event_323028((uint8_t)handle,1u,config+4u,
        r8(config+52u),r32(config+60u),r32(config+64u),r32(config+68u),
        r32(config+72u),r32(config+76u),r32(config+80u),0u,accuracy,follow,
        timeout);
}

uint32_t opencfw_em9305_child_32a000(uintptr_t record,uint32_t opcode)
{
    uint32_t state=r8(record+1u);
    if(state==0u){
        if(opcode==0x0bu)connection_setup(record);
    }else if(state==1u){
        uint32_t index=opcode-0x15u;
        if(index<15u){
            static const uint32_t bits[15]={1u<<17,0u,0u,0u,0u,0u,1u<<2,1u<<3,
                                            0u,0u,1u<<4,1u<<21,1u<<5,1u<<6,1u<<7};
            if(bits[index]!=0u)set_both(record,bits[index]);
            else (void)opencfw_em9305_child_32b210(record,opcode);
        }else if(opcode-71u>=2u&&opcode!=0x3du){
            if(opcode==0x40u){
                *(volatile uint8_t *)(record+1u)=2u;
                (void)opencfw_em9305_receive_terminate_325c08(record,0x70u);
            }else{
                (void)opencfw_em9305_child_32b210(record,opcode);
            }
        }
    }else if(state==3u){
        if(opcode==0x51u){
            uint32_t active=r32(record+636u);
            *(volatile uint32_t *)(record+640u)=0u;
            *(volatile uint32_t *)(record+636u)=active&~1u;
            (void)opencfw_em9305_mode_event_32cadc(record);
            *(volatile uint8_t *)(record+620u)=0u;
        }
    }else if(state==2u){
        uint32_t index=opcode-0x3du;
        if(index>=12u||((0xc01u>>index)&1u)==0u)
            (void)opencfw_em9305_child_32b210(record,opcode);
    }
    return opencfw_em9305_mode_event_318edc(record,opcode);
}
