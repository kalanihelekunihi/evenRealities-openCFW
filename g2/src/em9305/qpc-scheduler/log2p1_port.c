/* Experimental hardware operation adapter; no inferred arithmetic equation.
 * Authenticated vendor apexextensions.s declares major7/minor0, no flags,
 * two operands. Stock0x31163e uses R13 output/R0 input. Preserve that encoding
 * through a named assembler extension and the ordinary C return adapter.
 * Compilation/encoding identity is not device execution qualification.
 */
#include <stdint.h>
/* GNU gas spells the vendor FLAGS_NONE class SUFFIX_NONE. */
__asm__(".extInstruction log2p1,7,0,SUFFIX_NONE,SYNTAX_2OP");
uint32_t opencfw_em9305_log2p1(uint16_t ready_set)
{
    register uint32_t argument __asm__("r0") = ready_set;
    register uint32_t result __asm__("r13");
    __asm__ volatile("log2p1 %0, %1" : "=r"(result) : "r"(argument));
    return result;
}
