/* G2 s200_v2.2.6.10 observed ring packet builders and conservative RX helpers.
 * Not original source, not a firmware replacement. See README.md.
 * Caller supplies output storage (at least the documented return length).
 * No transmission, allocation or borrowed-buffer queue is implemented here. */
#ifndef OPENCFW_OBSERVED_RING_PROTOCOL_H
#define OPENCFW_OBSERVED_RING_PROTOCOL_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
static inline size_t g2_ring_heartbeat(uint8_t out[4]) {
    out[0]=0;out[1]=0x1a;out[2]=0x94;out[3]=1;return 4;
}
/* Normal public event path: low-level process helper alone uses opposite order.
 * 'interval' units are not established by this batch. */
static inline size_t g2_ring_report_interval(uint8_t out[6],uint16_t interval) {
    out[0]=0;out[1]=0x1a;out[2]=0x8a;out[3]=1;
    out[4]=(uint8_t)(interval>>8);out[5]=(uint8_t)interval;return 6;
}
static inline size_t g2_ring_touch_enable(uint8_t out[8],bool enable) {
    out[0]=0;out[1]=0x1a;out[2]=0x85;out[3]=1;
    out[4]=enable?0:0xff;out[5]=out[6]=out[7]=0xaa;return 8;
}
static inline size_t g2_ring_glasses_flags(uint8_t out[8],bool bit7,bool bit6) {
    out[0]=0;out[1]=0x1a;out[2]=0x89;out[3]=1;
    out[4]=(uint8_t)((bit7?0x80:0)|(bit6?0x40:0));out[5]=out[6]=out[7]=0;return 8;
}
/* Meaning of this outbound command is not fully established here. */
static inline size_t g2_ring_command_88(uint8_t out[4]) {
    out[0]=0;out[1]=0x35;out[2]=0x88;out[3]=0;return 4;
}
/* Conservative bounds for tooling; intentionally stronger than stock parser.
 * Does not authenticate a packet or validate unknown prefix/status semantics. */
static inline bool g2_ring_rx_has_required_bytes(const uint8_t *p,size_t n) {
    if(!p || n<3)return false;
    switch(p[2]) {
    case 0x61:return n>=7 && (n==7 || n>=11);
    case 0x85:case 0x8c:case 0x94:return n>=5;
    case 0x8b:return n>=6;
    case 0x8a:case 0x96:return true;
    default:return false;
    }
}
static inline uint32_t g2_ring_touch_tick_le(const uint8_t p[11]) {
    return (uint32_t)p[7]|((uint32_t)p[8]<<8)|((uint32_t)p[9]<<16)|((uint32_t)p[10]<<24);
}
#endif
