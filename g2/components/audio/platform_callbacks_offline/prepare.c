#include <stdint.h>
struct power_request { uint32_t masks[4]; uint8_t range,state,request; };
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
uint32_t audio_platform_auxiliary_active(void) {
    if(!B(0x20074f7a)) return 0;
    uint32_t value=W(0x40008800);
    return (value&15u)!=0 && !(value&0xc0000000u);
}
void audio_platform_prepare_state(struct power_request *request) {
    unsigned active=request->range==3 || (request->masks[0]&0x3fffffffu)!=0 || (request->masks[1]&0x4c4u)!=0;
    if(!active) active=(W(0x400204d8)&(1u<<29))!=0;
    if(!active && audio_platform_auxiliary_active()) {
        uint32_t mode=W(0x40008800)&15u; active=mode>=1 && mode<3;
    }
    for(unsigned i=0;!active && i<16;i++) {
        uint32_t config=W(0x40008200u+32u*i);
        if((config&1u) && (W(0x40008010)&(1u<<i))) {
            uint32_t id=(config>>8)&0x1ffu;
            active=id<6 || (id>=19 && id<25) || (id>=256 && id<480);
        }
    }
    B(0x20074f7b)=active;
}
