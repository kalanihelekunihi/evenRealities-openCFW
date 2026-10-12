#include <stdint.h>

/* Native common body 0x325d74..0x325dea, entered by the two table
 * callbacks at 0x325dec and 0x325df4. Packet stores retain native order. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_mode_callback_common_325d74(uintptr_t context,
                                                       uint32_t type)
{
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(9u);
    if (packet==0u) return 0u;
    *(volatile uint8_t *)packet=(uint8_t)type;
    uint8_t enabled=*(volatile uint8_t *)(context+534u);
    uint32_t upper=*(volatile uint16_t *)(context+572u);
    uint32_t lower=*(volatile uint16_t *)(context+568u);
    if (enabled!=0u) {
        uint8_t flags=*(volatile uint8_t *)(context+545u);
        if ((flags&8u)!=0u) {
            uint8_t lower_mode=*(volatile uint8_t *)(context+77u);
            uint8_t upper_mode=*(volatile uint8_t *)(context+76u);
            uint32_t floor=0xa90u;
            if (upper_mode==3u&&upper<floor) upper=floor;
            if (lower_mode==3u&&lower<floor) lower=floor;
        } else {
            uint32_t ceiling=0x848u;
            if (upper>ceiling) upper=ceiling;
            if (lower>ceiling) lower=ceiling;
        }
    } else {
        uint32_t ceiling=0x848u;
        if (upper>ceiling) upper=ceiling;
        if (lower>ceiling) lower=ceiling;
    }
    uint8_t low0=*(volatile uint8_t *)(context+566u);
    *(volatile uint8_t *)(packet+1u)=low0;
    uint8_t low1=*(volatile uint8_t *)(context+567u);
    *(volatile uint8_t *)(packet+4u)=(uint8_t)(lower>>8);
    *(volatile uint8_t *)(packet+3u)=(uint8_t)lower;
    *(volatile uint8_t *)(packet+2u)=low1;
    uint8_t high0=*(volatile uint8_t *)(context+570u);
    *(volatile uint8_t *)(packet+5u)=high0;
    uint8_t high1=*(volatile uint8_t *)(context+571u);
    *(volatile uint8_t *)(packet+8u)=(uint8_t)(upper>>8);
    *(volatile uint8_t *)(packet+7u)=(uint8_t)upper;
    *(volatile uint8_t *)(packet+6u)=high1;
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
uint32_t opencfw_em9305_mode_callback_325dec(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    return opencfw_em9305_mode_callback_common_325d74(context,0x14u);
}
uint32_t opencfw_em9305_mode_callback_325df4(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    return opencfw_em9305_mode_callback_common_325d74(context,0x15u);
}
