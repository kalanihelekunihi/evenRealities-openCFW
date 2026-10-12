#include <stdint.h>

/* Native 0x31e4a0..0x31e5ea. R0=context, R1=event; R2 is not read.
 * The state/event branches share the L/M release path and the common event
 * dispatcher epilogue. All called native bodies remain typed real contracts. */
extern uint32_t opencfw_em9305_mode_event_32279c(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_322b70(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_32c978(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t context,
                                                   uint32_t event);
/* Native 0x323028 uses R0..R7 and six stack words. */
extern uint32_t opencfw_em9305_mode_event_323028(
    uint32_t index, uint32_t zero, uintptr_t config_plus4,
    uint32_t config_byte52, uint32_t config_word60,
    uint32_t config_word64, uint32_t config_word68,
    uint32_t config_word72, uint32_t config_word76,
    uint32_t config_word80, uint32_t zero_stack,
    uint32_t context_byte321, uint32_t context_byte890,
    uint32_t context_halfword892);
extern uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_3212f0(uintptr_t context,
                                                   uint32_t event);
extern uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t context);
extern uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t id);
extern uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t context);
extern uint32_t opencfw_em9305_mode_event_318edc(uintptr_t context,
                                                   uint32_t event);

static uint8_t r8(uintptr_t p){return *(volatile const uint8_t *)p;}
static uint16_t r16(uintptr_t p){return *(volatile const uint16_t *)p;}
static uint32_t r32(uintptr_t p){return *(volatile const uint32_t *)p;}
static void w8(uintptr_t p,uint8_t v){*(volatile uint8_t *)p=v;}
static void w32(uintptr_t p,uint32_t v){*(volatile uint32_t *)p=v;}

static uint32_t native_index(uintptr_t context)
{
    uint32_t base=r32(0x805c70u);
    int32_t delta=(int32_t)((uint32_t)context-base);
    return (uint8_t)(delta/912);
}

uint32_t opencfw_em9305_child_31e4a0(uint32_t context_word,
                                       uint32_t event)
{
    uintptr_t context=(uintptr_t)context_word;
    uintptr_t mode_record=context+570u;
    uint8_t state=r8(context+1u);
    if(state==0u) {
        if(event==0x3fu) {
            (void)opencfw_em9305_mode_event_322b70(context);
            (void)opencfw_em9305_mode_event_32c978(context);
            uint32_t flags=r32(context+4u);
            if((flags&1u)!=0u) {
                (void)opencfw_em9305_mode_event_31bd78(context,0x66u);
                flags=r32(context+4u);
            }
            if((flags&(1u<<8u))!=0u) {
                (void)opencfw_em9305_mode_event_31bd78(context,0x67u);
                flags=r32(context+4u);
            }
            if((flags&(1u<<6u))!=0u) {
                uint16_t first=r16(mode_record);
                if(first>=28u || r16(mode_record+2u)>=329u)
                    (void)opencfw_em9305_mode_event_31bd78(context,0x68u);
            }
            uintptr_t config=(uintptr_t)r32(0x805c6cu);
            uint32_t context_half892=r16(context+892u);
            uint32_t base=r32(0x805c70u);
            uint32_t context_byte321=r8(context+321u);
            uint32_t context_byte890=r8(context+890u);
            uint32_t word68=r32(config+68u);
            uint32_t word64=r32(config+64u);
            uint32_t word60=r32(config+60u);
            uint32_t config_byte52=r8(config+52u);
            uint32_t word72=r32(config+72u);
            uint32_t word76=r32(config+76u);
            uint32_t word80=r32(config+80u);
            uint32_t index=(uint8_t)(((int32_t)((uint32_t)context-base))/912);
            (void)opencfw_em9305_mode_event_323028(
                index,0u,config+4u,config_byte52,
                word60,word64,word68,word72,word76,word80,
                0u,context_byte321,context_byte890,context_half892);
            w8(context+1u,2u);
            return opencfw_em9305_mode_event_318edc(context,event);
        }
        if(event==0x4cu) goto event_l;
        if(event==0x4du) goto event_m;
        return opencfw_em9305_mode_event_318edc(context,event);
    }
    if(state==3u) {
        if(event==0x4cu) goto event_l;
        if(event==0x4du) goto event_m;
        if(event==0x51u) {
            uint32_t word=r32(context+636u);
            w32(context+640u,0u);
            w32(context+636u,word&~1u);
            (void)opencfw_em9305_mode_event_32cadc(context);
            w8(mode_record+50u,0u);
        }
        return opencfw_em9305_mode_event_318edc(context,event);
    }
    if(state==2u) {
        /* BC after CMP(event-71,2) is unsigned LO: 71/72 go directly
         * to the common event dispatcher. */
        if((uint32_t)(event-71u)<2u || event==0x3fu)
            return opencfw_em9305_mode_event_318edc(context,event);
        if(event==0x3du) {
            (void)opencfw_em9305_mode_event_32279c(context);
            return opencfw_em9305_mode_event_318edc(context,event);
        }
        (void)opencfw_em9305_mode_event_3212f0(context,event);
    }
    if(event==0x4cu) goto event_l;
    if(event==0x4du) goto event_m;
    return opencfw_em9305_mode_event_318edc(context,event);

event_l:
    (void)opencfw_em9305_mode_event_31ac3c(context);
    (void)opencfw_em9305_mode_event_3231c4(context);
event_m: {
    uint32_t index=native_index(context);
    (void)opencfw_em9305_associated_schedule_drop_3136ac(index);
    return opencfw_em9305_init_connection_release_31ad90(context);
}
}
