#include <stdint.h>

/* Native 0x32483c..0x324904: ECU procedure state machine (enabled by bit
 * 6 of 0x805a98). Event 0x70 resumes a deferred procedure (flag bit 29 at
 * +644, clearing +648), event 0x29 starts one, and event 0x0c starts one
 * for a peer request 0x27, or for 0x07/0x11 requests of type 0x26 (0x07
 * also rewrites the request type halfword to 0x1a26). With the procedure
 * idle (+620 == 0) child 3247f8 runs and, if it left work pending (+624),
 * the procedure becomes active in state 29 (+635). An active procedure in
 * state 29 runs 3247f8 again and, when nothing is pending, goes idle and
 * finishes the PHY; in any other state the event is deferred (bit 29).
 * Returns 1 when the event was taken. */
extern void opencfw_em9305_dispatch_child_3247f8(uintptr_t record,uint32_t event);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

uint32_t opencfw_em9305_callback_32483c(uintptr_t record,uint32_t event)
{
    if((r8(0x805a98u)&0x40u)==0u)return 0u;
    uint32_t kind;
    if(event==0x70u){
        uint32_t flags=*(volatile uint32_t *)(record+644u);
        if((flags&0x20000000u)==0u)return 0u;
        *(volatile uint32_t *)(record+648u)=0u;
        *(volatile uint32_t *)(record+644u)=flags&~0x20000000u;
        kind=0u;
    }else if(event==0x29u){
        kind=0u;
    }else if(event==0x0cu){
        uint32_t request=r8(0x802818u);
        if(request==7u){
            if(r8(0x80281cu)!=0x26u)return 0u;
            *(volatile uint16_t *)0x80281cu=0x1a26u;
            kind=2u;
        }else if(request==0x27u){
            kind=1u;
        }else{
            if(request!=0x11u)return 0u;
            if(r8(0x80281cu)!=0x26u)return 0u;
            kind=2u;
        }
    }else return 0u;
    uint32_t active=r8(record+620u);
    if(active==1u){
        if(r8(record+635u)!=29u){
            *(volatile uint32_t *)(record+644u)|=0x20000000u;
            return 1u;
        }
        opencfw_em9305_dispatch_child_3247f8(record,kind);
        if(r8(record+624u)!=0u)return 1u;
        w8(record+620u,0u);
        w8(record+635u,0xffu);
        (void)opencfw_em9305_phy_finish_32c810(record);
        return 1u;
    }
    if(active!=0u)return 1u;
    opencfw_em9305_dispatch_child_3247f8(record,kind);
    if(r8(record+624u)==0u)return 1u;
    w8(record+620u,1u);
    w8(record+635u,29u);
    return 1u;
}
