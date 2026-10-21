#include <stdint.h>
typedef void (*transition_fn)(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t callback_select(uint32_t next,uint32_t old,uint8_t *index);
static void call_transition(uint8_t index,uint32_t a,uint32_t old_a,uint32_t b,uint32_t old_b) {
    uintptr_t target=((volatile uint32_t *)(uintptr_t)0x200002a8)[index];
    ((transition_fn)target)(a,old_a,b,old_b);
}
extern void callback_voltage(uint32_t b,uint32_t a);
void audio_platform_step(uint32_t a,uint32_t old_a,uint32_t b,uint32_t old_b) {
    uint8_t index=26;
    if(old_a<a) {
        for(uint32_t cursor=old_a;cursor<a;cursor++)
            if(!callback_select(cursor+1,cursor,&index)) call_transition(index,a,old_a,b,old_b);
    } else {
        for(uint32_t cursor=old_a;cursor>a;cursor--)
            if(!callback_select(cursor-1,cursor,&index)) call_transition(index,a,old_a,b,old_b);
    }
}
void audio_platform_apply(uint32_t a,uint32_t old_a,uint32_t b,uint32_t old_b) {
    if(a==old_a) { if(b!=old_b) callback_voltage(b,a); return; }
    if((a>>2)==(old_a>>2)) { audio_platform_step(a,old_a,b,old_b); return; }
    if((a&3)!=(old_a&3)) {
        uint32_t middle=(old_a&~3u)|(a&3u);
        audio_platform_step(middle,old_a,b,old_b);old_a=middle;
    }
    uint8_t index=26;
    if(!callback_select(a,old_a,&index)) call_transition(index,a,old_a,b,old_b);
}
