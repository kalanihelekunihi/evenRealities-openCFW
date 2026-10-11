/* Native Cordio ATT callbacks 0x4b4de0, 0x4b4e08, 0x4b4e50. */
#include <stdint.h>

extern uint8_t audio_ble_att_runtime[]; /* native live 0x200610ac */
extern uint8_t *audio_ble_att_ccb_by_conn_id(uint8_t); /* 0x4b4eee */
extern void g2_wsf_candidate_buffer_free_word(uint32_t); /* 0x5304d4 */

static uint32_t word(const uint8_t *p) {
    uint32_t v; __builtin_memcpy(&v,p,4); return v;
}
static void put_half(uint8_t *p,uint16_t v) { __builtin_memcpy(p,&v,2); }
static void put_word(uint8_t *p,uint32_t v) { __builtin_memcpy(p,&v,4); }
static uint8_t *table(uint32_t offset) {
    return (uint8_t *)(uintptr_t)word(audio_ble_att_runtime+offset);
}

void audio_ble_att_l2c_data_callback_4b4de0(uint16_t a,uint16_t b,uint8_t *packet) {
    uint8_t *v=table((packet[8]&1u)?0x3cu:0x40u);
    ((void (*)(uint16_t,uint16_t))(uintptr_t)word(v))(a,b);
}

void audio_ble_att_l2c_control_callback_4b4e08(uint8_t *event) {
    uint8_t *ccb=audio_ble_att_ccb_by_conn_id(event[0]);
    if(ccb[0xeu]==0u)return;
    if(event[2]==1u)ccb[2]|=2u;
    else {
        ccb[2]&=(uint8_t)~2u;
        uint8_t *v=table(0x40u);
        ((void (*)(uint8_t *))(uintptr_t)word(v+4u))(event);
        if((ccb[2]&2u)==0u) {
            v=table(0x3cu);
            ((void (*)(uint8_t *))(uintptr_t)word(v+4u))(event);
        }
    }
}

void audio_ble_att_dm_conn_callback_4b4e50(uint8_t *event) {
    uint8_t *ccb=audio_ble_att_ccb_by_conn_id(event[0]);
    if(event[2]==0x27u) {
        __builtin_memcpy(ccb+0xcu,event+6u,2u);
        ccb[0xeu]=event[0];
        for(uint32_t i=0;i<3u;i++) {
            put_half(ccb+i*4u,0xf7u);
            ccb[i*4u+2u]=0u;
        }
        put_word(ccb+0x10u,0u);
    }
    if(ccb[0xeu]!=0u) {
        uint8_t *v=table(0x40u);
        ((void (*)(uint8_t *,uint8_t *))(uintptr_t)word(v+0xcu))(ccb,event);
        v=table(0x3cu);
        ((void (*)(uint8_t *,uint8_t *))(uintptr_t)word(v+0xcu))(ccb,event);
        if(event[2]==0x28u) {
            ccb[0xeu]=0u;
            uint32_t buffer=word(ccb+0x10u);
            if(buffer)g2_wsf_candidate_buffer_free_word(buffer);
        }
    }
    uint32_t cb=word(audio_ble_att_runtime+0x50u);
    if(cb)((void (*)(uint8_t *))(uintptr_t)cb)(event);
    cb=word(audio_ble_att_runtime+0x5cu);
    if(cb)((void (*)(uint8_t *))(uintptr_t)cb)(event);
}
