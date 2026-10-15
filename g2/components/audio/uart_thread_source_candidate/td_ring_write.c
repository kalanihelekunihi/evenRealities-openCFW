/* Apollo td_ring_write, native 0x5976d8. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM 0x2010fd20 */

static uint16_t load_u16(const volatile uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static void put_u16(volatile uint8_t *p,uint16_t value) {
    p[0]=(uint8_t)value;
    p[1]=(uint8_t)(value>>8);
}

uint32_t audio_td_ring_write(const void *payload) {
    if(payload==0) return UINT32_MAX;
    const uint8_t *packet=payload;
    volatile uint8_t *ring=audio_td_state;
    uint16_t published=load_u16(ring+0x800u);
    uint16_t cached=load_u16(ring+0x802u);
    uint16_t end=published<cached?published:cached;
    if(end>0x7ffu) end=0x7ffu;
    uint16_t length=(uint16_t)((uint16_t)packet[0]|((uint16_t)packet[1]<<8));
    uint8_t sentence_final=packet[0x202u];
    uint8_t all_final=packet[0x203u];
    if(all_final!=0u && length==0u) {
        if(cached>0x7ffu) cached=0x7ffu;
        put_u16(ring+0x802u,cached);
        ring[cached]=0;
        if(sentence_final!=0u) put_u16(ring+0x800u,cached);
        ring[0x804u]=(uint8_t)(sentence_final!=0u);
        ring[0x805u]=1u;
        return 0;
    }
    uint16_t copy=length;
    if(copy>0x7ffu-end) copy=(uint16_t)(0x7ffu-end);
    for(uint16_t i=0;i<copy;++i) ring[end+i]=packet[2u+i];
    cached=(uint16_t)(end+copy);
    put_u16(ring+0x802u,cached);
    ring[cached]=0;
    if(sentence_final!=0u) put_u16(ring+0x800u,cached);
    if(cached<load_u16(ring+0x800u)) put_u16(ring+0x800u,cached);
    ring[0x804u]=(uint8_t)(sentence_final!=0u);
    ring[0x805u]=(uint8_t)(all_final!=0u);
    return 0;
}
