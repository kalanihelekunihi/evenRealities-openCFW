#include <stdint.h>

/* Native 0x30e858..0x30e878. The 12-byte frame retains the native ambient
 * bytes at sp+11; a C automatic would not preserve the same stack source. */
extern uint32_t opencfw_em9305_associated_cycle_event_30e858(
    uint32_t first,uint32_t second,uint32_t third);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

__asm__(
 ".text\n.align 2\n"
 ".global opencfw_em9305_associated_cycle_event_30e858\n"
 ".type opencfw_em9305_associated_cycle_event_30e858,@function\n"
 "opencfw_em9305_associated_cycle_event_30e858:\n"
 "st.aw blink,[sp,-12]\n"
 "stb_s r0,[sp,8]\n"
 "mov_s r0,0x35\n"
 "asl_s r0,r0,0x10\n"
 "st_s r0,[sp,4]\n"
 "add_s r0,sp,4\n"
 "stb r2,[sp,10]\n"
 "bl.d opencfw_em9305_ll_event_callback_30e79c\n"
 "stb r1,[sp,9]\n"
 "ld.ab blink,[sp,12]\n"
 "j_s [blink]\n"
 ".size opencfw_em9305_associated_cycle_event_30e858,.-opencfw_em9305_associated_cycle_event_30e858\n");
