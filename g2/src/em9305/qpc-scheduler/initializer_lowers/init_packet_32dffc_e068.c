#include <stdint.h>

/* Native 0x32dffc/0x32e068 share a 0x23-byte prefix.  ARC LP_COUNT=0x12
 * executes 18 byte-copy iterations.  XBFU immediate 0x4 extracts bit 4:
 * GCC ARC extzvsi encodes ((width-1)<<5)|position. */
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t address);
static uint8_t rd(uintptr_t p, unsigned n)
{ return *(volatile const uint8_t *)(p + n); }
static void w8(uintptr_t p, unsigned n, uint8_t v)
{ *(volatile uint8_t *)(p + n) = v; }
static void w16(uintptr_t p, unsigned n, uint16_t v)
{ *(volatile uint16_t *)(p + n) = v; }
static void w32(uintptr_t p, unsigned n, uint32_t v)
{ *(volatile uint32_t *)(p + n) = v; }

static void common_prefix(uintptr_t fields, uintptr_t payload)
{
    uint8_t high=rd(payload,2u),low=rd(payload,1u);
    w16(fields,0u,(uint16_t)((uint16_t)low|((uint16_t)high<<8)));
    for(unsigned i=0;i<18u;++i)
        w8(fields,2u+i,rd(payload,3u+i));
    high=rd(payload,22u); low=rd(payload,21u);
    w16(fields,20u,(uint16_t)((uint16_t)low|((uint16_t)high<<8)));
    high=rd(payload,24u); low=rd(payload,23u);
    w16(fields,22u,(uint16_t)((uint16_t)low|((uint16_t)high<<8)));
    uint8_t split=rd(payload,25u);
    w8(fields,26u,(uint8_t)(split>>5));
    w8(fields,24u,(uint8_t)(split&15u));
    w8(fields,25u,(uint8_t)((split>>4)&1u));
    w8(fields,27u,rd(payload,26u));
    uint64_t address=opencfw_em9305_controller_pack_address(payload+27u);
    w32(fields,32u,(uint32_t)(address>>32u));
    w32(fields,28u,(uint32_t)address);
    high=rd(payload,34u); low=rd(payload,33u);
    w16(fields,36u,(uint16_t)((uint16_t)low|((uint16_t)high<<8)));
}

uint32_t opencfw_em9305_packet_child_32dffc(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    common_prefix((uintptr_t)fields_word,payload);
    return 35u;
}

uint32_t opencfw_em9305_packet_child_32e068(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields=(uintptr_t)fields_word;
    common_prefix(fields,payload);
    uint8_t b36=rd(payload,36u),b37=rd(payload,37u);
    uint8_t b35=rd(payload,35u),b38=rd(payload,38u);
    w32(fields,40u,(uint32_t)b35|((uint32_t)b36<<8)|
                   ((uint32_t)b37<<16)|((uint32_t)b38<<24));
    w8(fields,44u,rd(payload,39u));
    w8(fields,45u,rd(payload,40u));
    w8(fields,46u,rd(payload,41u));
    w8(fields,47u,rd(payload,42u));
    return 43u;
}
