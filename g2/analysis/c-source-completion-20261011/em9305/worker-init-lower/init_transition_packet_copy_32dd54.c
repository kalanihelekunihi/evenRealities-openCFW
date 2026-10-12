#include <stdint.h>

extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t);
static uint8_t rd8(uintptr_t p) { return *(volatile uint8_t *)p; }
static void wr8(uintptr_t p,uint32_t v) { *(volatile uint8_t *)p=(uint8_t)v; }
static void wr16(uintptr_t p,uint32_t v) { *(volatile uint16_t *)p=(uint16_t)v; }
static void wr32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }

/* Full native 0x32dd54..0x32de04, using selected 0x304624 address packer.
 * The two packer calls and destination writes retain native order. */
uint32_t opencfw_em9305_init_transition_packet_copy_32dd54(
    uintptr_t out,uintptr_t source)
{
    uint64_t first=opencfw_em9305_controller_pack_address(source);
    wr32(out,(uint32_t)first);
    wr32(out+4u,(uint32_t)(first>>32u)); /* Second BL delay slot. */
    uint64_t second=opencfw_em9305_controller_pack_address(source+6u);
    wr32(out+12u,(uint32_t)(second>>32u));
    wr32(out+8u,(uint32_t)second);

    uint32_t b13=rd8(source+13u),b14=rd8(source+14u);
    uint32_t b12=rd8(source+12u),b15=rd8(source+15u);
    wr32(out+16u,b12|(b13<<8u)|(b14<<16u)|(b15<<24u));
    uint32_t b17=rd8(source+17u),b18=rd8(source+18u),b16=rd8(source+16u);
    wr32(out+20u,b16|(b17<<8u)|(b18<<16u));
    uint32_t b19=rd8(source+19u);
#ifdef __arc__
    /* Native 32dd96 clears the high accumulator before writing byte38. */
    __asm__ volatile("mov r59,0" : : : "r59","memory");
#endif
    wr8(out+38u,b19);
    uint32_t b21=rd8(source+21u),b20=rd8(source+20u);
    wr16(out+40u,b20|(b21<<8u));
    uint32_t b23=rd8(source+23u),b22=rd8(source+22u);
    wr16(out+32u,b22|(b23<<8u));
    uint32_t b25=rd8(source+25u),b24=rd8(source+24u);
    wr16(out+34u,b24|(b25<<8u));
    uint32_t b27=rd8(source+27u),b26=rd8(source+26u);
    wr16(out+36u,b26|(b27<<8u));
    uint32_t b28=rd8(source+28u);
#ifdef __arc__
    __asm__ volatile("mov r58,%0" : : "r"(b28) : "r58","memory");
#endif
    uint32_t b29=rd8(source+29u);
    uint32_t b30=rd8(source+30u);
#ifdef __arc__
    /* MACU writes its register operand.  Use a separate read/write scratch
     * so subsequent byte packing still consumes the original b29. */
    uint32_t macu_scratch=b29;
    __asm__ volatile("macu %0,%0,256" : "+r"(macu_scratch) : : "r58","r59","memory");
#endif
    uint32_t b31=rd8(source+31u);
#ifdef __arc__
    uint32_t macdu_scratch=b30;
    __asm__ volatile("macdu 0,%0,0x10000" : "+r"(macdu_scratch) : : "r58","r59","memory");
#endif
    uint32_t b32=rd8(source+32u);
    wr32(out+24u,b28|(b29<<8u)|(b30<<16u)|(b31<<24u));
    wr32(out+28u,b32);
    uint32_t flags=rd8(source+33u);
    wr8(out+42u,flags&31u);
    wr8(out+43u,flags>>5u);
    return 34u;
}
