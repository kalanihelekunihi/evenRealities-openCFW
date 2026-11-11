#include <stdint.h>

/* Native 0x322630..0x322752: apply a completed PHY update. The current TX
 * (+76) and RX (+77) PHYs become the requested ones (+722/+723, mapped
 * through the PHY mode table at 0x33448f; 1 when out of range) unless the
 * request is empty or already in effect (PHY 2..4 compare as masks 2, 4,
 * 8, others as 1), setting flag bit 21 of +636. A new TX PHY reloads the
 * TX power (+66) from the per-PHY table at +332 (coded PHY indexed by the
 * S2/S8 choice +78); the unset marker 0x7e is replaced by the default
 * power (config byte 40), which is reported to the power hook at
 * *0x8052c8 when enabled (+548 bit 2). Finally recompute both radio
 * limits (+592, +590, mirrored into +0x1c) and mark +628. */
extern const uint8_t opencfw_em9305_phy_mode_table_33448f[];
extern uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t,uintptr_t);

static uint32_t phy_mask_322630(uint32_t phy)
{
    uint32_t index=phy-2u;
    if(index>=3u) return 1u;
    return (uint8_t)(0x80402u>>((index&0xffu)*8u));
}

void opencfw_em9305_child_322630(uintptr_t record)
{
    volatile uint8_t *rec=(volatile uint8_t *)record;
    uint32_t tx_mask=phy_mask_322630(rec[76]);
    uint32_t rx_mask=phy_mask_322630(rec[77]);
    uint32_t requested=rec[722];
    if(requested!=0u&&requested!=tx_mask) {
        uint32_t phy=1u,coded=0u;
        if(requested-2u<7u) {
            phy=opencfw_em9305_phy_mode_table_33448f[(int8_t)(requested-2u)];
            coded=((requested-2u)&0x7fu)==2u;
        }
        rec[76]=(uint8_t)phy;
        uint32_t adjust=coded?(rec[78]!=1u):1u;
        int32_t power=(int8_t)rec[332u+phy-adjust];
        *(volatile uint32_t *)(record+636u)|=1u<<21;
        rec[66]=(uint8_t)power;
        if(power==0x7e) {
            uint32_t power_default=*(volatile uint8_t *)(*(volatile uint32_t *)(uintptr_t)0x805cacu+40u);
            rec[66]=(uint8_t)power_default;
            rec[331u+phy]=(uint8_t)power_default;
            if(coded)
                rec[335]=*(volatile uint8_t *)(*(volatile uint32_t *)(uintptr_t)0x805cacu+40u);
            if(rec[548]&4u) {
                uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x8052c8u;
                if(hook!=0u)
                    ((void (*)(uintptr_t,uint32_t,uint32_t,int32_t,uint32_t))hook)(record,phy,0u,
                        *(volatile int8_t *)(*(volatile uint32_t *)(uintptr_t)0x805cacu+40u),1u);
            }
        }
    }
    requested=rec[723];
    if(requested!=0u&&requested!=(uint8_t)rx_mask) {
        uint32_t phy=1u;
        if(requested-2u<7u)
            phy=opencfw_em9305_phy_mode_table_33448f[(int8_t)(requested-2u)];
        rec[77]=(uint8_t)phy;
        *(volatile uint32_t *)(record+636u)|=1u<<21;
    }
    rec[628]=1u;
    uint32_t tx_limit=opencfw_em9305_radio_limit_317b10(record,record+574u);
    *(volatile uint16_t *)(record+592u)=(uint16_t)tx_limit;
    uint32_t rx_limit=opencfw_em9305_radio_limit_317b10(record,record+566u);
    uint32_t mirrored=*(volatile uint16_t *)(record+592u);
    *(volatile uint16_t *)(record+590u)=(uint16_t)rx_limit;
    *(volatile uint32_t *)(record+0x1cu)=mirrored;
}
