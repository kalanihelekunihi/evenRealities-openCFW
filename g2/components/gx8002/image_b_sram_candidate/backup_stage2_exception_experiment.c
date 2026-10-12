/* Stock image-B 0x100031f0..0x10003240. These are native fatal exception
 * policies, including the actual register capture and non-return loops.
 * The 0x20017390 scratch region belongs to the BSS attribution frontier;
 * its address is a genuine linker/data contract, not fabricated storage.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_exception_scratch_20017390[];

__attribute__((naked, noreturn, used, section(".text.image_b_exception_report")))
void gx8002_image_b_exception_report_100031f0(void)
{
    __asm__ volatile (
        "mfcr r3, cr<0, 0>\n\t"
        "lsri r3, r3, 16\n\t"
        "sextb r3, r3\n"
        "1: br 1b");
}

__attribute__((naked, noreturn, used, section(".text.image_b_exception_capture")))
void gx8002_image_b_exception_capture_100031fc(void)
{
    __asm__ volatile (
        "psrset ee\n\t"
        "subi r14, r14, 4\n\t"
        "st.w r13, (r14, 0)\n\t"
        "addi r14, r14, 4\n\t"
        "lrw r13, gx8002_image_b_exception_scratch_20017390\n\t"
        "st.w r14, (r13, 0)\n\t"
        "lrw r14, gx8002_image_b_exception_scratch_20017390\n\t"
        "subi r14, r14, 72\n\t"
        "stm r0-r12, (r14)\n\t"
        "lrw r0, gx8002_image_b_exception_scratch_20017390\n\t"
        "ld.w r0, (r0, 0)\n\t"
        "st.w r0, (r14, 0x38)\n\t"
        "subi r0, 4\n\t"
        "ld.w r13, (r0, 0)\n\t"
        "st.w r13, (r14, 0x34)\n\t"
        "st.w r15, (r14, 0x3c)\n\t"
        "mfcr r0, cr<2, 0>\n\t"
        "st.w r0, (r14, 0x40)\n\t"
        "mfcr r0, cr<4, 0>\n\t"
        "st.w r0, (r14, 0x44)\n\t"
        "mov r0, r14\n\t"
        "bsr gx8002_image_b_exception_report_100031f0\n\t"
        "br gx8002_image_b_exception_capture_100031fc");
}

__attribute__((naked, noreturn, used, section(".text.image_b_default_exception")))
void gx8002_image_b_default_exception_10003240(void)
{
    __asm__ volatile ("br gx8002_image_b_exception_capture_100031fc");
}
