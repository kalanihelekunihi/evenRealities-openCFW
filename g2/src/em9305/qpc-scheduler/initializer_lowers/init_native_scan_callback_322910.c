#include <stdint.h>

/* Native 0x322910..0x322a30: scan request/response outcome. On a received
 * response from the device being scanned (state 4 at +184 of the scanner
 * +0x2c, address +168/+172 equal to 0x805064) and while the report budget
 * (0x805b01 below config byte 14) allows, complete the pending report
 * (+108: channel, address-changed flag, rssi/phy/type bytes into +100),
 * queue it, signal the task and stage a fresh 45-byte report. Then
 * update the backoff (0x805166): two successes halve the window (min 1),
 * two failures double it (max 256); pick a random count in 1..window. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_post(uint32_t,uint32_t);
extern void opencfw_em9305_scan_counter_up_316968(void);
extern uint32_t opencfw_em9305_scan_random_30c478(void);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

uint32_t opencfw_em9305_scan_callback_322910(uintptr_t object,uint32_t success)
{
    const uintptr_t backoff=(uintptr_t)0x805166u;
    if(success!=0u) {
        uintptr_t scanner=r32(object+0x2cu);
        uintptr_t peer=scanner+152u;
        if(r8(peer+32u)==4u&&
           ((r32(peer+0x10u)^r32(0x805064u))|(r32(0x805068u)^r32(peer+0x14u)))==0u&&
           r8(0x805b01u)<r8(r32(0x805cacu)+0xeu)) {
            uintptr_t fresh=opencfw_em9305_wsf_event_allocate(0x2du);
            if(fresh!=0u) {
                w8(r32(scanner+0x6cu)+39u,r8(peer));
                uint32_t changed=0u;
                if(r8(scanner+187u)!=r8(scanner+186u))
                    changed=((r32(peer+0x1cu)^r32(peer+0x14u))|
                             (r32(peer+0x18u)^r32(peer+0x10u)))!=0u;
                w8(r32(scanner+0x6cu)+40u,changed);
                w8(r32(scanner+0x64u)+41u,r32(peer+4u));
                w8(r32(scanner+0x64u)+42u,r32(peer+4u)>>8);
                w8(r32(scanner+0x64u)+43u,r16(scanner+158u));
                w8(r32(scanner+0x64u)+44u,r8(scanner+159u));
                (void)opencfw_em9305_ll_event_enqueue((uintptr_t)0x805000u,0u,r32(scanner+0x6cu));
                (void)opencfw_em9305_wsf_event_post(r8(0x805b18u),256u);
                opencfw_em9305_scan_counter_up_316968();
                *(volatile uint32_t *)(scanner+108u)=(uint32_t)fresh;
            }
        }
        uint32_t count=r8(backoff+3u)+1u;
        w8(backoff+3u,count);
        if((uint8_t)count>=2u) {
            uint32_t window=r16(backoff);
            w8(backoff+3u,0u);
            window>>=1;
            if(window==0u) window=1u;
            w16(backoff,window);
        }
        w8(backoff+4u,0u);
    } else {
        uint32_t count=r8(backoff+4u)+1u;
        w8(backoff+4u,count);
        if((uint8_t)count>=2u) {
            uint32_t window=r16(backoff);
            w8(backoff+4u,0u);
            window=(uint16_t)(window<<1);
            if(window>256u) window=256u;
            w16(backoff,window);
        }
        w8(backoff+3u,0u);
    }
    uint32_t random=opencfw_em9305_scan_random_30c478();
    w8(backoff+2u,(random&(r16(backoff)-1u))+1u);
    return 0u;
}
