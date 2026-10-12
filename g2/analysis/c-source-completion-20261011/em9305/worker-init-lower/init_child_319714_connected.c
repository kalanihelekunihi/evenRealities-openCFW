#include <stdint.h>

/* Native 0x319714..0x3197c6. R0=context, R1=packet, R2=mode.
 * The BIH table at 0x319736 has 17 rows for opcodes 3..19. Its targets
 * are interior basic blocks sharing a single return; source keeps them in
 * one connected dispatcher rather than inventing handler functions. */
extern uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t context,
                                                             uintptr_t packet);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);

static uint8_t read8(uintptr_t p)
{ return *(volatile const uint8_t *)p; }
static void write8(uintptr_t p,uint8_t v)
{ *(volatile uint8_t *)p=v; }

uint32_t opencfw_em9305_child_319714(uint32_t context_word,
                                      uint32_t packet_word,
                                      uint32_t mode)
{
    uintptr_t context=(uintptr_t)context_word;
    uintptr_t packet=(uintptr_t)packet_word;
    uint32_t header=opencfw_em9305_short_header_decode_32dedc(context,packet);
    uintptr_t opcode_pointer=packet+header;
    uint8_t opcode=read8(opcode_pointer);
    uintptr_t payload=opcode_pointer+1u; /* native LDB.AB [r15,1] */
    write8(context+8u,opcode);           /* branch delay slot, even invalid */
    if(opcode<3u || opcode>19u) return 25u;
    switch(opcode) {
    case 3u: {
        if(mode==0u) return 25u;
        (void)opencfw_em9305_memcpy((void *)(context+12u),
                                    (const void *)payload,8u);
        uint8_t high=read8(payload+9u),low=read8(payload+8u);
        *(volatile uint16_t *)(context+20u)=
            (uint16_t)((uint16_t)low|((uint16_t)high<<8));
        (void)opencfw_em9305_memcpy((void *)(context+22u),
                                    (const void *)(payload+10u),8u);
        (void)opencfw_em9305_memcpy((void *)(context+30u),
                                    (const void *)(payload+18u),4u);
        return read8(context+5u)==23u?0u:25u;
    }
    case 4u:
        if(mode==1u) return 25u;
        (void)opencfw_em9305_memcpy((void *)(context+12u),
                                    (const void *)payload,12u);
        return read8(context+5u)==13u?0u:25u;
    case 5u:
        if(mode==1u) return 25u;
        return read8(context+5u)==1u?0u:25u;
    case 6u: case 11u:
        return read8(context+5u)==1u?0u:25u;
    case 10u:
        if(mode==0u) return 25u;
        return read8(context+5u)==1u?0u:25u;
    case 18u: case 19u:
        if((read8(0x805a94u)&16u)==0u) return 25u;
        return read8(context+5u)==1u?0u:25u;
    default:
        return 25u; /* table rows 7..9 and 12..17 */
    }
}
