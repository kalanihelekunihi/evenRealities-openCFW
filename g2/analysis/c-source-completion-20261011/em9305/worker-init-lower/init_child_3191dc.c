#include <stdint.h>
#include <stddef.h>

/* Native 0x3191dc..0x319204. Product table 0x334d0c has 43 typed
 * handler identities; interior basic blocks remain genuine source contracts.
 * No numeric stock code address is installed as a callback. */
typedef uint32_t (*em_handler_t)(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t output, uintptr_t input);
extern uint32_t opencfw_em9305_packet_entry_3191ac(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3191c4(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319204(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319208(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319234(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319268(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319298(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3192c0(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3192e8(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319310(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319338(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_31935c(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_31936c(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3193d8(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319400(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319414(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319420(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319438(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319450(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_31948c(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3194ac(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3194cc(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3194f4(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319518(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_31953c(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319564(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319574(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3195a0(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3195cc(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3195f4(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319620(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319644(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319698(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_3196ec(uint32_t context, uint32_t payload, uint32_t mode);
extern uint32_t opencfw_em9305_packet_entry_319700(uint32_t context, uint32_t payload, uint32_t mode);

static const em_handler_t em_packet_handlers[43] = {
    opencfw_em9305_packet_entry_31936c, /* opcode  0, native 0x31936c */
    opencfw_em9305_packet_entry_319268, /* opcode  1, native 0x319268 */
    opencfw_em9305_packet_entry_3196ec, /* opcode  2, native 0x3196ec */
    opencfw_em9305_packet_entry_319204, /* opcode  3, native 0x319204 */
    opencfw_em9305_packet_entry_319204, /* opcode  4, native 0x319204 */
    opencfw_em9305_packet_entry_319204, /* opcode  5, native 0x319204 */
    opencfw_em9305_packet_entry_319204, /* opcode  6, native 0x319204 */
    opencfw_em9305_packet_entry_319700, /* opcode  7, native 0x319700 */
    opencfw_em9305_packet_entry_319414, /* opcode  8, native 0x319414 */
    opencfw_em9305_packet_entry_319420, /* opcode  9, native 0x319420 */
    opencfw_em9305_packet_entry_319204, /* opcode 10, native 0x319204 */
    opencfw_em9305_packet_entry_319204, /* opcode 11, native 0x319204 */
    opencfw_em9305_packet_entry_3191c4, /* opcode 12, native 0x3191c4 */
    opencfw_em9305_packet_entry_3191ac, /* opcode 13, native 0x3191ac */
    opencfw_em9305_packet_entry_3194cc, /* opcode 14, native 0x3194cc */
    opencfw_em9305_packet_entry_319338, /* opcode 15, native 0x319338 */
    opencfw_em9305_packet_entry_31935c, /* opcode 16, native 0x31935c */
    opencfw_em9305_packet_entry_319620, /* opcode 17, native 0x319620 */
    opencfw_em9305_packet_entry_319204, /* opcode 18, native 0x319204 */
    opencfw_em9305_packet_entry_319204, /* opcode 19, native 0x319204 */
    opencfw_em9305_packet_entry_319438, /* opcode 20, native 0x319438 */
    opencfw_em9305_packet_entry_319438, /* opcode 21, native 0x319438 */
    opencfw_em9305_packet_entry_31953c, /* opcode 22, native 0x31953c */
    opencfw_em9305_packet_entry_319564, /* opcode 23, native 0x319564 */
    opencfw_em9305_packet_entry_319574, /* opcode 24, native 0x319574 */
    opencfw_em9305_packet_entry_319450, /* opcode 25, native 0x319450 */
    opencfw_em9305_packet_entry_3193d8, /* opcode 26, native 0x3193d8 */
    opencfw_em9305_packet_entry_319400, /* opcode 27, native 0x319400 */
    opencfw_em9305_packet_entry_3194f4, /* opcode 28, native 0x3194f4 */
    opencfw_em9305_packet_entry_31948c, /* opcode 29, native 0x31948c */
    opencfw_em9305_packet_entry_3194ac, /* opcode 30, native 0x3194ac */
    opencfw_em9305_packet_entry_3192c0, /* opcode 31, native 0x3192c0 */
    opencfw_em9305_packet_entry_3192e8, /* opcode 32, native 0x3192e8 */
    opencfw_em9305_packet_entry_319298, /* opcode 33, native 0x319298 */
    opencfw_em9305_packet_entry_319310, /* opcode 34, native 0x319310 */
    opencfw_em9305_packet_entry_3195cc, /* opcode 35, native 0x3195cc */
    opencfw_em9305_packet_entry_3195f4, /* opcode 36, native 0x3195f4 */
    opencfw_em9305_packet_entry_3195a0, /* opcode 37, native 0x3195a0 */
    opencfw_em9305_packet_entry_319698, /* opcode 38, native 0x319698 */
    opencfw_em9305_packet_entry_319644, /* opcode 39, native 0x319644 */
    opencfw_em9305_packet_entry_319208, /* opcode 40, native 0x319208 */
    opencfw_em9305_packet_entry_319234, /* opcode 41, native 0x319234 */
    opencfw_em9305_packet_entry_319518, /* opcode 42, native 0x319518 */
};

uint32_t opencfw_em9305_child_3191dc(uint32_t context, uint32_t packet, uint32_t mode)
{
    uint32_t header_size = opencfw_em9305_short_header_decode_32dedc(context, packet);
    uint32_t payload = packet + header_size;
    uint32_t opcode = *(volatile const uint8_t *)(uintptr_t)payload;
    *(volatile uint8_t *)(uintptr_t)(context + 8u) = (uint8_t)opcode;
    /* Native 0x3191f2 branch delay executes this store even for invalid
     * opcodes before returning status 25. */
    if (opcode >= 43u) return 25u;
    return em_packet_handlers[opcode](context, payload, mode);
}
