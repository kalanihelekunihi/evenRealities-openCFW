#include <stdint.h>

/* Native 0x31b9ac..0x31ba22: pack an ISO data header. Bytes 0..1: the
 * 12-bit handle (+0) with PB flags (+2, 2 bits) and TS flag (+3); for PB
 * 0 or 2 (first fragment) append the optional 4-byte timestamp (+8, when
 * TS is set), then the sequence number (+0xc) and the 14-bit SDU length
 * (+0xe) with packet status (+0x10). Bytes 2..3: the data length (+4)
 * plus the header bytes added. Returns the header length. */
uint32_t opencfw_em9305_dispatch_child_31b9ac(uintptr_t out,uintptr_t in)
{
    volatile uint8_t *o=(volatile uint8_t *)out;
    uint32_t flags=*(volatile uint8_t *)(in+2u);
    uint32_t handle=*(volatile uint16_t *)in;
    uint32_t stamp=*(volatile uint8_t *)(in+3u);
    o[0]=(uint8_t)handle;
    o[1]=(uint8_t)((((flags&3u)<<12)+(handle&0xf00u)+(stamp<<14))>>8);
    uint32_t added=0u;
    if((*(volatile uint8_t *)(in+2u)|2u)==2u) {
        volatile uint8_t *field;
        if(*(volatile uint8_t *)(in+3u)!=0u) {
            o[4]=(uint8_t)*(volatile uint32_t *)(in+8u);
            o[5]=(uint8_t)(*(volatile uint32_t *)(in+8u)>>8);
            o[6]=(uint8_t)*(volatile uint16_t *)(in+0xau);
            o[7]=*(volatile uint8_t *)(in+0xbu);
            field=o+8;
            added=8u;
        } else {
            field=o+4;
            added=4u;
        }
        field[0]=*(volatile uint8_t *)(in+0xcu);
        field[1]=*(volatile uint8_t *)(in+0xdu);
        uint32_t length=*(volatile uint16_t *)(in+0xeu);
        uint32_t status=*(volatile uint8_t *)(in+0x10u);
        field[2]=(uint8_t)length;
        field[3]=(uint8_t)(((status<<14)+(length&0xf00u))>>8);
    }
    o[2]=(uint8_t)(*(volatile uint8_t *)(in+4u)+added);
    o[3]=(uint8_t)((*(volatile uint16_t *)(in+4u)+added)>>8);
    return added+4u;
}
