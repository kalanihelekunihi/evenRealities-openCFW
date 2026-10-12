#include <stdint.h>

/* Alternative canonical entry for native 0x312918. Select only in place of
 * the existing 312918 C definition, with the typed shared body in
 * init_associated_object_r2_312918.c. R2 arrives from the caller and is
 * returned as the path-specific live registers. The 32-byte frame keeps
 * saved blink at sp+0 and the R2-R7 frame at sp+4..sp+27. */
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t,
                                                               uint32_t);
extern uint32_t opencfw_em9305_associated_object_init_with_regs_312918(
    uintptr_t,uint32_t,void *);

__asm__(
    ".text\n.balign 4\n"
    ".global opencfw_em9305_associated_object_init_312918\n"
    ".type opencfw_em9305_associated_object_init_312918,@function\n"
    "opencfw_em9305_associated_object_init_312918:\n"
    "st.aw blink,[sp,-32]\n"
    "st r2,[sp,4]\n"
    "st r3,[sp,8]\n"
    "st r4,[sp,12]\n"
    "st r5,[sp,16]\n"
    "st r6,[sp,20]\n"
    "st r7,[sp,24]\n"
    "add r2,sp,4\n"
    "bl opencfw_em9305_associated_object_init_with_regs_312918\n"
    "ld r2,[sp,4]\n"
    "ld r3,[sp,8]\n"
    "ld r4,[sp,12]\n"
    "ld r5,[sp,16]\n"
    "ld r6,[sp,20]\n"
    "ld r7,[sp,24]\n"
    "ld.ab blink,[sp,32]\n"
    "j_s [blink]\n"
    ".size opencfw_em9305_associated_object_init_312918,.-opencfw_em9305_associated_object_init_312918\n");
