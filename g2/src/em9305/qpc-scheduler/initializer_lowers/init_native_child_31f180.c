#include <stdint.h>

/* Native 0x31f180..0x31f296: parse the extended header of a received
 * advertising PDU into the scan report state at 0x803b68 (skipped while
 * busy +1). A continuation (+9) only advances the data pointer (+4) and
 * recomputes the RSSI-adjusted byte (+8); otherwise the header (+0xc) and
 * extended fields (+0xa) are decoded first. For ADV_EXT_IND (type 7) the
 * field flags are masked by the scanner's filter (+701, +153) into +154.
 * With an AuxPtr present, decode it (from the scanner's +184) and, for a
 * supported secondary PHY, return the aux offset in us minus the
 * secondary time and store the window end (+128 of the object's +44),
 * otherwise return 0. */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t,uintptr_t,uintptr_t);
extern void opencfw_em9305_child_32db74(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_phy_supported_31b39c(void);
extern uint32_t opencfw_em9305_init_secondary_current_303f5c(void);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);

struct init_aux_pointer_31f180 {
    uint8_t channel;
    uint8_t clock_accuracy;
    uint8_t units;
    uint8_t reserved;
    uint16_t offset;
    uint8_t phy;
    uint8_t reserved1;
};

uint32_t opencfw_em9305_child_31f180(uintptr_t object,uintptr_t data)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x803b68u;
    if(data==0u||state[1]!=0u) return 0u;
    uintptr_t scanner=*(volatile uint32_t *)(object+0x24u);
    uintptr_t window=*(volatile uint32_t *)(object+44u);
    uint32_t rssi;
    if(state[9]!=0u) {
        uint32_t skip=state[0xb];
        rssi=~(uint32_t)*(volatile uint8_t *)(scanner+152u);
        uint32_t base=state[0x10];
        state[9]=0u;
        rssi+=base;
        *(volatile uint32_t *)(state+4)=data+skip+2u;
    } else {
        uintptr_t cursor=data+opencfw_em9305_child_32db0c((uintptr_t)(state+0xc),data);
        uint32_t used=opencfw_em9305_dispatch_child_32df24(scanner+152u,(uintptr_t)(state+0xa),
                                                          cursor);
        uint32_t level=*(volatile uint8_t *)(scanner+152u);
        uint32_t base=state[0x10];
        *(volatile uint32_t *)(state+4)=used+cursor;
        rssi=~level+base;
    }
    state[8]=(uint8_t)rssi;
    if(state[0xc]!=7u) return 0u;
    uint32_t fields=state[0xa];
    if(*(volatile uint8_t *)(scanner+701u)!=0u) {
        uint32_t filter=*(volatile uint8_t *)(scanner+154u);
        fields&=~0x26u;
        state[0xa]=(uint8_t)fields;
        *(volatile uint8_t *)(scanner+154u)=(uint8_t)(filter&~0x26u);
    } else if(*(volatile uint8_t *)(scanner+153u)!=0u) {
        uint32_t filter=*(volatile uint8_t *)(scanner+154u);
        fields&=~0x34u;
        state[0xa]=(uint8_t)fields;
        *(volatile uint8_t *)(scanner+154u)=(uint8_t)(filter&~0x34u);
    }
    if((fields&0x10u)==0u) return 0u;
    struct init_aux_pointer_31f180 aux;
    opencfw_em9305_child_32db74((uintptr_t)&aux,*(volatile uint32_t *)(scanner+184u));
    uint32_t phy=aux.phy;
    if(phy>=3u) return 0u;
    if(((opencfw_em9305_phy_supported_31b39c()>>(phy&31u))&1u)==0u) return 0u;
    uint32_t unit=(aux.units==0u)?30u:300u;
    uint32_t offset=aux.offset*unit;
    *(volatile uint8_t *)(window+1u)=aux.channel;
    uint32_t current=opencfw_em9305_init_secondary_current_303f5c();
    uint32_t margin=(aux.clock_accuracy==1u)?50u:500u;
    uint32_t time=opencfw_em9305_init_secondary_time_317ebc(unit+offset,current+margin);
    *(volatile uint32_t *)(window+128u)=unit+(time<<1);
    return offset-time;
}
