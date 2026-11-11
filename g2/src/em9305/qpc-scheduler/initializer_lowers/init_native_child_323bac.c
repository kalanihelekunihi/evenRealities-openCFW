#include <stdint.h>

/* Native 0x323bac..0x323c0a: encode a 3-byte sync-offset field. Offsets
 * below 0x3bfc4 us use 30 us units (byte0 bit 7 clear), larger ones 300 us
 * units (bit 7 set); the stock divisions are reciprocal multiplies. byte0
 * also carries (secondary current < 0x33) << 6 and the caller's flag bits;
 * bytes 1..2 hold the 13-bit offset and the PHY code (1M 0, 2M 1, coded 2)
 * from the object's byte 63 in bits 13..14. Returns that PHY field
 * (code << 13), which 32c650 passes on. */
extern uint32_t opencfw_em9305_init_secondary_current_303f5c(void);

static uint32_t mulhi_323bac(uint32_t a,uint32_t b)
{
    return (uint32_t)(((uint64_t)a*b)>>32);
}

uint32_t opencfw_em9305_child_323bac(uintptr_t object,uint32_t offset,uint32_t flags,
                                 uintptr_t out)
{
    uint32_t current=opencfw_em9305_init_secondary_current_303f5c();
    uint32_t units,large;
    if(offset<0x3bfc4u) {
        units=mulhi_323bac(offset,0x11111112u)>>1;
        large=0u;
    } else {
        units=(offset*3u+mulhi_323bac(offset,0x69d0369eu))>>10;
        large=0x80u;
    }
    volatile uint8_t *field=(volatile uint8_t *)out;
    field[0]=(uint8_t)(((current<0x33u)?1u<<6:0u)|flags|large);
    uint32_t phy=*(volatile uint8_t *)(object+63u);
    field[1]=(uint8_t)units;
    uint32_t code=(phy==2u)?1u:((phy==3u)?2u:0u);
    field[2]=(uint8_t)((units|(code<<13))>>8);
    return code<<13;
}
