/* Native td_bounded_string_copy 0x59722c and record builder 0x5972ce. */
#include <stdint.h>

extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */

static uint16_t load16(const uint8_t *p) {
    return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
}
static void store16(uint8_t *p, uint16_t v) {
    p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8);
}
static void store32(uint8_t *p, uint32_t v) {
    for (unsigned i=0;i<4u;++i) p[i]=(uint8_t)(v>>(i*8u));
}

uint32_t audio_td_bounded_string_copy(uint8_t *dest, uint32_t capacity,
                                      const uint8_t *source) {
    if (dest==0 || capacity==0u) return 0u;
    dest[0]=0u;
    if (source==0) return 0u;
    uint32_t n=load16(source);
    if (capacity<=n) n=capacity-1u;
    if (n!=0u) (void)audio_queue_copy_bytes(dest,source+2u,n);
    dest[n]=0u;
    return n&0xffffu;
}

uint32_t audio_td_record_build_from_event(uint8_t *row, const uint8_t *event,
                                          uint32_t session, uint32_t passthrough) {
    if (row==0 || event==0) return passthrough;
    uint8_t kind=event[0];
    row[0]=kind;
    row[1]=(kind==2u || kind==4u)?1u:(kind==3u?2u:0u);
    uint32_t n=audio_td_bounded_string_copy(row+2u,0x201u,event+2u);
    store16(row+0x204u,(uint16_t)n);
    store32(row+0x208u,session);
    return passthrough;
}
