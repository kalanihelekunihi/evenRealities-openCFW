/* Native td_session_ring_append 0x5979ce. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dcu]; /* RAM base 0x2010fd20 */
extern void audio_td_session_ring_reset(void);
extern uint32_t audio_td_ring_index_wrap(uint8_t *, uint16_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

static uint16_t load16(const uint8_t *p) {
    return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
}
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
           (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}
static void store16(uint8_t *p, uint16_t v) {
    p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8);
}
static void store32(uint8_t *p, uint32_t v) {
    for (unsigned i=0;i<4u;++i) p[i]=(uint8_t)(v>>(i*8u));
}

uint8_t *audio_td_session_ring_append(uint8_t continue_last, uint8_t *kind) {
    uint8_t *ring=audio_td_state+0x1054u; /* native RAM 0x20110d74 */
    if (load32(ring+0x8504u)==0u) audio_td_session_ring_reset();
    uint16_t count=load16(ring+0x8500u);
    uint16_t physical;
    uint8_t resulting_kind;
    if (continue_last==0u || count==0u) {
        if (count<64u) {
            physical=(uint16_t)audio_td_ring_index_wrap(ring,count);
            store16(ring+0x8500u,(uint16_t)(count+1u));
        } else {
            physical=load16(ring+0x8502u);
            store16(ring+0x8502u,(uint16_t)((physical+1u)&63u));
        }
        resulting_kind=2u;
        continue_last=0u;
    } else {
        physical=(uint16_t)audio_td_ring_index_wrap(ring,(uint16_t)(count-1u));
        resulting_kind=3u;
    }
    uint8_t *row=ring+(uint32_t)physical*0x214u;
    audio_uart_buffer_zero(row,0x214u,0u);
    store32(row+0x20cu,load32(ring+0x8504u));
    uint32_t next=load32(ring+0x8508u);
    if (continue_last==0u) {
        store32(ring+0x8508u,next+1u);
        store32(row+0x210u,next);
    } else {
        store32(row+0x210u,next==0u?0u:next-1u);
    }
    if (kind!=0) *kind=resulting_kind;
    return row;
}
