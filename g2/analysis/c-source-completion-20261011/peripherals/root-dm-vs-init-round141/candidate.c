/* Native DmDevVsInit4b308c..4b3096. Preserve incoming R7 return and
 * stack writes despite the void caller contract. Named Thumb instructions
 * in C; not portable C, not an opcode array or retained binary body. */
#include <stdint.h>
__attribute__((naked)) void DmDevVsInit(uint32_t handler __attribute__((unused))) {
    __asm__ volatile("push {r7, lr}\n\tuxtb r0, r0\n\tmov r8, r8\n\tmov r8, r8\n\tpop {r0, pc}");
}
