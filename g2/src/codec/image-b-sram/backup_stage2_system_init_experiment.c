/* Image-B native system init 0x1000314c..0x100031e3, represented in a C
 * translation unit with C-SKY ISA for its exact CR/PSR and MMIO sequence.
 * Pinned NationalChip arch/soc/grus/system.c corroborates high-level order;
 * native instructions determine this product's exact branches and values.
 * Child 0x3ffc is already selected as preserve_memory; clock init 0x3294 and board init 0x34d4
 * remain real source obligations.
 */
#include <stdint.h>

extern void gx8002_image_b_clear_bss_10003128(void);
extern void gx8002_image_b_clock_init_10003294(void);
extern uint32_t gx8002_image_b_preserve_memory_10003ffc(void);
extern void gx8002_image_b_system_board_child_100034d4(void);

__attribute__((naked, used, section(".text.image_b_system_init")))
void gx8002_image_b_system_init_1000314c(void)
{
    __asm__ volatile (
        "push r15\n\t"
        "mfcr r2, cr<19, 0>\n\t"
        "mfcr r3, cr<20, 0>\n\t"
        "mfcr r1, cr<21, 0>\n\t"
        "movi r0, 0\n\t"
        "ins r3, r0, 31, 12\n\t"
        "ins r1, r0, 2, 0\n\t"
        "mtcr r1, cr<21, 0>\n\t"
        "movi r1, 31\n\t"
        "andi r3, r3, 4095\n\t"
        "ins r3, r1, 5, 1\n\t"
        "lrw r1, 0xfefffcfe\n\t"
        "and r2, r1\n\t"
        "ori r2, r2, 768\n\t"
        "mtcr r2, cr<19, 0>\n\t"
        "movi r2, 1\n\t"
        "ins r3, r2, 0, 0\n\t"
        "mtcr r3, cr<20, 0>\n\t"
        "mfcr r3, cr<18, 0>\n\t"
        "ori r3, r3, 3\n\t"
        "mtcr r3, cr<18, 0>\n\t"
        "bsr gx8002_image_b_clock_init_10003294\n\t"
        "bsr gx8002_image_b_preserve_memory_10003ffc\n\t"
        "bez r0, 1f\n"
        "2: bsr gx8002_image_b_system_board_child_100034d4\n\t"
        "lrw r3, gx8002_image_b_vectors_10003000\n\t"
        "mtcr r3, cr<1, 0>\n\t"
        "lrw r3, 0xe000e100\n\t"
        "movi r1, 0\n\t"
        "movi r2, 255\n\t"
        "st.w r2, (r3, 0xb10)\n\t"
        "mov r2, r1\n\t"
        "subi r2, 1\n\t"
        "st.w r1, (r3, 0x200)\n\t"
        "st.w r2, (r3, 0x180)\n\t"
        "st.w r1, (r3, 0x204)\n\t"
        "st.w r2, (r3, 0x184)\n\t"
        "st.w r1, (r3, 0x208)\n\t"
        "st.w r2, (r3, 0x188)\n\t"
        "st.w r1, (r3, 0x20c)\n\t"
        "st.w r2, (r3, 0x18c)\n\t"
        "psrset ee, ie\n\t"
        "pop r15\n"
        "1: bsr gx8002_image_b_clear_bss_10003128\n\t"
        "br 2b");
}
