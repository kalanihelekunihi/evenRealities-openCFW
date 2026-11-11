#include <stdint.h>

static uint8_t rd8(uintptr_t p) { return *(volatile uint8_t *)p; }
static void wr8(uintptr_t p,uint32_t v) { *(volatile uint8_t *)p=(uint8_t)v; }
static void wr16(uintptr_t p,uint32_t v) { *(volatile uint16_t *)p=(uint16_t)v; }
static void wr32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }
static uint32_t bitfield_0e(uint32_t value)
{
    return (value>>14u)&1u; /* XBFU 0xe */
}
static uint32_t bitfield_0d(uint32_t value)
{
    return (value>>13u)&1u; /* XBFU 0xd */
}

/* Full native 0x32e164..0x32e1f0. Stock also assembles bytes 4..6 in the
 * DSP accumulator (MOV r58 / MACU / MACDU); nothing reads that value, the
 * stored word is built from the same bytes below. */
uintptr_t opencfw_em9305_radio_secondary_encode_32e164(
    uintptr_t out,uintptr_t source)
{
    uint32_t b1=rd8(source+1u),b0=rd8(source);
    uint32_t first=(b1<<8u)|b0;
    wr16(out,first&0x1fffu);
    wr8(out+3u,bitfield_0e(first));
    wr8(out+2u,bitfield_0d(first));
    uint32_t b3=rd8(source+3u),b2=rd8(source+2u);
    wr16(out+4u,(b3<<8u)|b2);
    uint32_t b4=rd8(source+4u);
    uint32_t b5=rd8(source+5u);
    uint32_t b6=rd8(source+6u);
    uint32_t b7=rd8(source+7u);
    uint32_t b8=rd8(source+8u);
    wr32(out+8u,b4|(b5<<8u)|(b6<<16u)|(b7<<24u));
    wr32(out+12u,b8&31u);
    wr8(out+16u,b8>>5u);
    uint32_t b10=rd8(source+10u),b11=rd8(source+11u);
    uint32_t b9=rd8(source+9u),b12=rd8(source+12u);
    wr32(out+20u,b9|(b10<<8u)|(b11<<16u)|(b12<<24u));
    uint32_t b14=rd8(source+14u),b15=rd8(source+15u);
    uint32_t b13=rd8(source+13u);
    wr32(out+24u,b13|(b14<<8u)|(b15<<16u));
    uint32_t b17=rd8(source+17u),b16=rd8(source+16u);
    wr16(out+28u,b16|(b17<<8u));
    return out;
}
