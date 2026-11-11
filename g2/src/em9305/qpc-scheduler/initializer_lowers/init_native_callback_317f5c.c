#include <stdint.h>

/* Native 0x317f5c..0x31807a: PHY-update procedure state machine. Event
 * 0x70 resumes a deferred procedure (bit 29 of +644) or a parked peer
 * request (bit 30: the saved 10-byte request at +866 is restored to
 * 0x80281c), event 0x29 starts a local procedure and event 0x0c a peer
 * request of type 0x26; +648 is cleared on resume. With the procedure
 * idle (+620 == 0) the request is run by 317f2c and, if work is pending
 * (+624), the procedure becomes active in state 29 (+635) - unless another
 * procedure owns the link (bit 6 of 0x805a98 with bit 2 of 0x805a87 and
 * +534 clear), in which case the local procedure is deferred (bit 29) or
 * the peer request parked (bit 30, saved to +866) and mode event 0x67 is
 * raised. An active procedure in state 29 runs 317f2c and, when nothing
 * is pending, goes idle and finishes the PHY; otherwise the event is
 * deferred. Returns 1 when the event was taken. */
extern void opencfw_em9305_child_317f2c(uintptr_t record,uint32_t selector);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t context,uint32_t event);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_callback_317f5c(uintptr_t record,uint32_t event)
{
    uint32_t selector,local;
    if(event==0x70u){
        uint32_t flags=r32(record+644u);
        if((flags&0x20000000u)!=0u){
            w32(record+648u,0u);
            local=1u;
            selector=0u;
            w32(record+644u,flags&~0x20000000u);
        }else{
            if((flags&0x40000000u)==0u)return 0u;
            w32(record+648u,0u);
            w32(record+644u,flags&~0x40000000u);
            (void)opencfw_em9305_memcpy((void *)0x80281cu,(const void *)(record+866u),10u);
            local=0u;
            selector=1u;
        }
    }else if(event==0x29u){
        local=1u;
        selector=0u;
    }else{
        if(event!=0x0cu)return 0u;
        if(r8(0x802818u)!=0x26u)return 0u;
        local=0u;
        selector=1u;
    }
    uint32_t active=r8(record+620u);
    if(active==1u){
        if(r8(record+635u)!=29u){
            w32(record+644u,r32(record+644u)|0x20000000u);
            return 1u;
        }
        opencfw_em9305_child_317f2c(record,selector);
        if(r8(record+624u)!=0u)return 1u;
        w8(record+620u,0u);
        w8(record+635u,0xffu);
        (void)opencfw_em9305_phy_finish_32c810(record);
        return 1u;
    }
    if(active!=0u)return 1u;
    if((r8(0x805a87u)&4u)==0u&&r8(record+534u)==0u
       &&(r8(0x805a98u)&0x40u)!=0u){
        uint32_t pending=r32(record+648u);
        uint32_t flags=r32(record+644u);
        if(local!=0u){
            w32(record+648u,pending);
            w32(record+644u,flags|0x20000000u);
        }else{
            w32(record+648u,pending);
            w32(record+644u,flags|0x40000000u);
            (void)opencfw_em9305_memcpy((void *)(record+866u),(const void *)0x80281cu,10u);
        }
        (void)opencfw_em9305_mode_event_31bd78(record,0x67u);
        return 1u;
    }
    opencfw_em9305_child_317f2c(record,selector);
    if(r8(record+624u)==0u)return 1u;
    w8(record+620u,1u);
    w8(record+635u,29u);
    return 1u;
}
