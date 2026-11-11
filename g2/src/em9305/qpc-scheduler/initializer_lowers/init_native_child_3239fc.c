#include <stdint.h>

/* Native 0x3239fc..0x323ac8: compose an advertising PDU for the set. The
 * advertising type (+0x20, low 3 bits) selects the PDU type and header
 * flags: legacy connectable (0) and scannable (4) types take the
 * address-type bits from +827 and set 0x20 unless channel selection
 * (+0xae2) is off when +369 is enabled; types 1/2 use 9/0x40, 5 uses 0xb/
 * 0x40, 6 uses 0xb/0x48, others 0/0. The 5-byte header buffer starts as
 * {7,0,0,0,0} and is filled by 318440 and 3184f4 before composing. */
extern uint32_t opencfw_em9305_child_318440(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_3184f4(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t,uint32_t,uint32_t,uint32_t,
                                                    uintptr_t,uintptr_t,uintptr_t,uint32_t,
                                                    uint32_t);

uint32_t opencfw_em9305_child_3239fc(uintptr_t set,uintptr_t output,uintptr_t source,
                                     uint32_t count)
{
    uint8_t header[5]={7u,0u,0u,0u,0u};
    uint32_t pdu=9u,flags=0x40u;
    uint32_t mode=0u;
    switch(*(volatile uint16_t *)(set+0x20u)&7u) {
    case 0:
        flags=(*(volatile uint8_t *)(set+827u)&1u)^81u;
        pdu=8u;
        mode=*(volatile uint8_t *)(set+369u);
        break;
    case 1:
    case 2:
        break;
    case 4: {
        uint32_t address=*(volatile uint8_t *)(set+827u);
        mode=*(volatile uint8_t *)(set+369u);
        flags=(address&1u)^81u;
        pdu=(address&2u)^0xau;
        break;
    }
    case 5:
        pdu=0xbu;
        break;
    case 6:
        pdu=0xbu;
        flags=0x48u;
        break;
    default:
        pdu=0u;
        flags=0u;
        break;
    }
    if(mode!=0u&&*(volatile uint8_t *)(set+0xae2u)==0u) flags|=0x20u;
    (void)opencfw_em9305_child_318440((uintptr_t)header,set+0x9d4u,set);
    (void)opencfw_em9305_child_3184f4((uintptr_t)header,set+0x9d4u,set);
    return opencfw_em9305_radio_compose_323dc0(set,pdu,flags,
        *(volatile uint16_t *)(set+0x20u)&3u,(uintptr_t)header,source,output,2u,count);
}
