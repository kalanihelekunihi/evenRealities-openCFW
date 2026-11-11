#include <stdint.h>

/* Native 0x316298..0x31634c: accept a pending connection-update request
 * (0x80281c: interval min, +2 max, +4 latency, +6 timeout) when the
 * latency and intervals are below 500, (latency+1) * interval is at most
 * 500, the timeout (x10) lies in 10..3200 and exceeds twice the scaled
 * interval budget of the record (+266 * 1.25, rounded up). An accepted
 * request is stored at +846, +260 and +382 and flag bit 29 is set at +636;
 * otherwise the link is terminated (0x73) when option bit 5 of 0x805a86 is
 * set. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,
                                                        uint32_t reason);

static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}

void opencfw_em9305_ecu_callback_316298(uintptr_t record)
{
    uint32_t latency=r16(0x802822u);
    uint32_t maximum=r16(0x802820u);
    uint32_t minimum=r16(0x80281cu);
    uint32_t timeout=r16(0x802824u);
    uint32_t ranges_ok;
    if(latency>=500u)ranges_ok=0u;
    else ranges_ok=((uint16_t)(minimum-1u)<500u)&(maximum<500u);
    uint32_t span=(maximum+1u)*minimum;
    uint32_t scaled_timeout=timeout*10u;
    uint32_t accept;
    if((int32_t)span>=501)accept=0u;
    else accept=(latency<minimum)
                &(0xf388u<(uint16_t)(timeout+0xfffff37fu))&ranges_ok;
    uint32_t budget=r16(record+266u);
    budget=budget+(budget>>2)+((budget&3u)!=0u?1u:0u);
    budget=budget*span*2u;
    if(scaled_timeout>=budget&&accept!=0u){
        uint32_t flags=*(volatile uint32_t *)(record+636u);
        uint32_t preferred=r16(0x80281eu);
        uintptr_t update=record+846u;
        w16(record+260u,maximum);
        w16(record+382u,scaled_timeout);
        w16(update,minimum);
        w16(update+4u,latency);
        w16(update+6u,timeout);
        w16(update+2u,preferred);
        *(volatile uint32_t *)(record+636u)=flags|0x20000000u;
        return;
    }
    if((*(volatile uint8_t *)0x805a86u&0x20u)==0u)return;
    (void)opencfw_em9305_receive_terminate_325c08(record,0x73u);
}
