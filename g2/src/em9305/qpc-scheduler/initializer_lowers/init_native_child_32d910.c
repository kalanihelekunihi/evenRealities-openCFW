#include <stdint.h>

/* Native 0x32d910..0x32da74: decode the 0x2c (BIGInfo) AD payload into
 * the receive record: little-endian bit fields of words 0..2, the 32-bit
 * field at +13, the 20/12-bit pair at +17, the 16-bit field at +21, the
 * two 40-bit fields at +23 and +28 (split around bits 32..39) and, for an
 * encrypted payload (length >= 35), the 8-byte GIV and 16-byte GSKD.
 * Returns the decoded length (0x38 encrypted, 0x20 otherwise). */
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t length);

static uint32_t opencfw_em9305_le32_32d910(volatile const uint8_t *in)
{
    uint32_t value=((uint32_t)in[1]<<8)+in[0];
    value+=(uint32_t)in[2]<<16;
    return value+((uint32_t)in[3]<<24);
}

uint32_t opencfw_em9305_child_32d910(uintptr_t out, uintptr_t in, uint32_t length)
{
    volatile const uint8_t *i=(volatile const uint8_t *)in;
    volatile uint8_t *o=(volatile uint8_t *)out;
    uint32_t word=opencfw_em9305_le32_32d910(i);
    o[16]=(uint8_t)(word>>27);
    *(volatile uint16_t *)(out+10u)=(uint16_t)(word&0x3fffu);
    *(volatile uint16_t *)(out+14u)=(uint16_t)((word>>15)&0xfffu);
    o[12]=(uint8_t)((word>>14)&1u);
    word=opencfw_em9305_le32_32d910(i+4);
    o[24]=(uint8_t)(word>>28);
    o[17]=(uint8_t)(word&31u);
    *(volatile uint32_t *)(out+20u)=(word>>8)&0xfffffu;
    o[18]=(uint8_t)((word&224u)>>5);
    word=opencfw_em9305_le32_32d910(i+8);
    *(volatile uint16_t *)(out+34u)=(uint16_t)(word>>24);
    *(volatile uint32_t *)(out+28u)=word&0xfffffu;
    o[32]=(uint8_t)((word>>20)&15u);
    *(volatile uint32_t *)(out+36u)=opencfw_em9305_le32_32d910(i+13);
    word=opencfw_em9305_le32_32d910(i+17);
    *(volatile uint16_t *)(out+44u)=(uint16_t)(word>>20);
    *(volatile uint32_t *)(out+40u)=word&0xfffffu;
    *(volatile uint16_t *)(out+46u)=(uint16_t)(((uint32_t)i[22]<<8)+i[21]);
    uint32_t low=i[23]+((uint32_t)i[24]<<8)+((uint32_t)i[25]<<16)+((uint32_t)i[26]<<24);
    uint32_t high=i[27];
    *(volatile uint32_t *)(out+48u)=low;
    o[56]=(uint8_t)(high>>5);
    *(volatile uint32_t *)(out+52u)=high&31u;
    uint32_t next=(high>>5)+1u;
    low=i[28]+((uint32_t)i[29]<<8)+((uint32_t)i[30]<<16)+((uint32_t)i[31]<<24);
    high=i[32];
    *(volatile uint32_t *)(out+60u)=low;
    o[56]=(uint8_t)next;
    *(volatile uint32_t *)(out+64u)=high&127u;
    o[68]=(uint8_t)(high>>7);
    if(length<0x23u){
        o[69]=0u;
        return 0x20u;
    }
    o[69]=1u;
    (void)opencfw_em9305_memcpy((void *)(out+70u),(const void *)(in+33u),8u);
    (void)opencfw_em9305_memcpy((void *)(out+78u),(const void *)(in+41u),16u);
    return 0x38u;
}
