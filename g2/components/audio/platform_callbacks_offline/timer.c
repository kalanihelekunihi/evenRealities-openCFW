#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t spot_timer_clock_request(uint32_t group,uint32_t user);
void audio_spot_timer_initialize(void) {
    W(0x400083e0)&=~1u;W(0x400083e0)=0x110;
    W(0x400083f0)=0x100;W(0x400083e8)=0xffffffffu;W(0x400083ec)=0xffffffffu;
    W(0x40008068)=0xc0000000u;W(0x40008060)|=0x40000000u;
}
void audio_spot_timer_start(uint32_t microseconds) {
    (void)spot_timer_clock_request(4,49);
    W(0x400083e8)=microseconds*6u;
    W(0x40008010)|=0x8000u;
    W(0x400083e0)|=2u;W(0x400083e0)&=~2u;
    W(0xe000e108)=0x40000u;
    W(0x400083e0)|=1u;
}
void audio_spot_timer_restart(uint32_t microseconds) {
    W(0x400083e0)&=~1u;
    W(0x400083e0)|=2u;W(0x400083e0)&=~2u;
    W(0x400083e8)=microseconds*6u;
    W(0x40008068)=0xc0000000u;W(0xe000e288)=0x40000u;
    W(0x400083e0)|=1u;
}
