#include <stdint.h>
struct power_request { uint32_t masks[4]; uint8_t range,state,request; };
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
static uint32_t nibble(uint32_t word,unsigned bit,uint32_t value) { return (word&~(15u<<bit))|((value&15u)<<bit); }
uint32_t audio_platform_plan(struct power_request *r,uint32_t *first,uint32_t *second) {
    uint32_t initial=W(0x200742b0),word=initial;
    word=nibble(word,8,r->range);
    unsigned s=r->state==1 ? 1 : r->state==0 ? 0 : (W(0x40021000)&3u)==2;
    unsigned clients=(r->masks[0]&0x3fffffffu)!=0 || (r->masks[1]&0x4c4u)!=0;
    unsigned request=r->request==1||r->request==2;
    word=nibble(word,0,s);word=nibble(word,4,request||clients);
    word=nibble(word,12,r->request==2?2:r->request==1?1:0);
    word=nibble(word,16,clients);
    word=nibble(word,20,request||(r->masks[0]&0xc00000u)!=0);
    uint32_t key=word&0xf00fffu,profile;
    unsigned feature=initial&1u;
    switch(key) {
    case 0x000: profile=feature?7:3; break;
    case 0x001: profile=feature?15:11; break;
    case 0x010: profile=7; break;
    case 0x011: profile=15; break;
    case 0x100: profile=feature?6:2; break;
    case 0x101: profile=feature?14:10; break;
    case 0x110: profile=6; break;
    case 0x111: profile=14; break;
    case 0x200: profile=feature?5:1; break;
    case 0x201: profile=feature?13:9; break;
    case 0x210: profile=5; break;
    case 0x211: profile=13; break;
    case 0x300: profile=feature?4:0; break;
    case 0x301: profile=feature?12:8; break;
    case 0x310: profile=4; break;
    case 0x311: profile=12; break;
    case 0x100010: profile=19; break;
    case 0x100011: profile=15; break;
    case 0x100110: profile=18; break;
    case 0x100111: profile=14; break;
    case 0x100210: profile=17; break;
    case 0x100211: profile=13; break;
    case 0x100310: profile=16; break;
    case 0x100311: profile=12; break;
    default: return 5;
    }
    *first=profile;
    switch(word&0xff00fu) {
    case 0: *second=0; break;
    case 1: *second=feature?7:1; break;
    case 0x1000: case 0x11000: *second=2; break;
    case 0x2000: case 0x12000: *second=3; break;
    case 0x1001: case 0x11001: *second=4; break;
    case 0x2001: case 0x12001: *second=5; break;
    case 0x10000: *second=6; break;
    case 0x10001: *second=7; break;
    default: return 5;
    }
    return 0;
}
void audio_platform_change_state(uint32_t next,uint32_t old) {
    if((uint8_t)old==1 && (uint8_t)next==2) *(volatile uint8_t *)(uintptr_t)0x20074f6b=1;
}
