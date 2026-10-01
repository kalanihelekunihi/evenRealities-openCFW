/* Observed G2 s200_v2.2.6.10 input interfaces; not original firmware source.
 * Pure helpers for app/simulator tooling. These are internal events, not BLE
 * packets. Application side effects remain dependent on page and input state. */
#ifndef OPENCFW_RING_ACTIONS_H
#define OPENCFW_RING_ACTIONS_H
#include <stdbool.h>
#include <stdint.h>
enum g2_input_event { G2_SINGLE_CLICK=0,G2_DOUBLE_CLICK=1,G2_LONG_PRESS=3,
 G2_UPROLL=4,G2_DOWNROLL=5,G2_PRESS=13,G2_RELEASE=14 };
enum {G2_INPUT_SOURCE_RING=4};
static inline bool g2_ring_type_to_input(uint8_t type,uint32_t *event) {
 switch(type) {
 case 0:*event=G2_LONG_PRESS;return true;
 case 1:*event=G2_SINGLE_CLICK;return true;
 case 2:*event=G2_DOUBLE_CLICK;return true;
 case 4:*event=G2_DOWNROLL;return true;
 case 5:*event=G2_UPROLL;return true;
 case 8:*event=G2_RELEASE;return true;
 default:return false;
 }
}
/* Original helper 0x004C5886: first byte occupies bits 16..23, second 0..7. */
static inline uint32_t g2_input_extra(uint8_t first,uint8_t second) {
 return ((uint32_t)first<<16)|second;
}
/* 12-byte application/sync body built by 0x00465748 (not a BLE wire packet). */
static inline void g2_app_input_body(uint8_t out[12],uint16_t source,
                                     uint32_t event,uint8_t first,uint8_t second) {
 uint32_t extra=g2_input_extra(first,second);
 out[0]=3;out[1]=7;out[2]=(uint8_t)source;out[3]=(uint8_t)(source>>8);
 for(unsigned i=0;i<4;i++) {out[4+i]=(uint8_t)(event>>(8*i));out[8+i]=(uint8_t)(extra>>(8*i));}
}
#endif
