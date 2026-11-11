/* SPDX-License-Identifier: MIT
 * Native image-A SRAM trap entry at 0x100235fc. This naked C function keeps
 * the architectural register save and trap-stack switch in explicit C-SKY
 * instructions. A C prologue cannot run until the interrupted frame is saved.
 * The exception vector points to the branch at 0x10023640 inside this body.
 */
#include <stdint.h>

extern void gx8002_resident_trap_c_235f0(uint32_t *regs);

__attribute__((naked, used, aligned(4),
               section(".text.gx8002_resident_exception_entry")))
void gx8002_resident_trap_235fc(void)
{
    __asm__ volatile (
        "psrset ee\n\t"
        "subi r14, r14, 4\n\t"
        "st.w r13, (r14, 0)\n\t"
        "addi r14, r14, 4\n\t"
        "lrw r13, 0x20027310\n\t"
        "st.w r14, (r13, 0)\n\t"
        "lrw r14, 0x20027310\n\t"
        "subi r14, r14, 72\n\t"
        "stm r0-r12, (r14)\n\t"
        "lrw r0, 0x20027310\n\t"
        "ld.w r0, (r0, 0)\n\t"
        "st.w r0, (r14, 0x38)\n\t"
        "subi r0, r0, 4\n\t"
        "ld.w r13, (r0, 0)\n\t"
        "st.w r13, (r14, 0x34)\n\t"
        "st.w r15, (r14, 0x3c)\n\t"
        "mfcr r0, cr<2, 0>\n\t"
        "st.w r0, (r14, 0x40)\n\t"
        "mfcr r0, cr<4, 0>\n\t"
        "st.w r0, (r14, 0x44)\n\t"
        "mov r0, r14\n\t"
        "bsr gx8002_resident_trap_c_235f0\n\t"
        ".global gx8002_resident_exception_bridge_23640\n\t"
        ".type gx8002_resident_exception_bridge_23640, %function\n\t"
        "gx8002_resident_exception_bridge_23640:\n\t"
        "br gx8002_resident_trap_235fc\n\t"
        ".size gx8002_resident_exception_bridge_23640, .-gx8002_resident_exception_bridge_23640\n\t"
    );
}
