/* Apollo terminal-data session-list synchronization, native 0x5977ce. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];

static uint16_t load_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_u32(uint8_t *p,uint32_t value) {
    for(uint32_t i=0;i<4u;++i) p[i]=(uint8_t)(value>>(8u*i));
}

/* Stock 0x5977CE (td_state_sync) */
uint32_t audio_td_state_sync(const void *payload) {
    if(payload==0) return UINT32_MAX;
    const uint8_t *p=payload;
    uint8_t *state=audio_td_state;
    for(uint32_t i=0;i<0x63cu;++i) state[0x9b9cu+i]=state[0x9560u+i];
    uint32_t old_count=load_u32(state+0x9ba4u);
    if(old_count>10u) old_count=10u;
    put_u32(state+0x9560u,load_u32(p));
    put_u32(state+0x9564u,load_u32(p+4u));
    uint32_t count=load_u16(p+8u);
    if(count>10u) count=10u;
    put_u32(state+0x9568u,count);
    state[0xa1d9u]=1u;
    for(uint32_t i=0;i<count;++i) {
        uint8_t *row=state+0x95fcu+i*0x90u;
        const uint8_t *incoming=p+0xcu+i*0x88u;
        const uint8_t *old=0;
        for(uint32_t j=0;j<old_count;++j) {
            const uint8_t *candidate=state+0x9b9cu+j*0x90u+0x9cu;
            if(load_u32(candidate)==load_u32(incoming)) {
                old=candidate;
                break;
            }
        }
        for(uint32_t k=0;k<0x88u;++k) row[k]=incoming[k];
        if(old==0) {
            put_u32(row+0x88u,0u);
            row[0x8cu]=0u;
        } else {
            uint8_t status=row[0x86u];
            put_u32(row+0x88u,(status==1u || status==2u)?load_u32(old+0x88u):0u);
            row[0x8cu]=status==2u?old[0x8cu]:0u;
        }
    }
    return 0u;
}
