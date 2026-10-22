/* IAR __iar_program_start for the Apollo main image, reconstructed from the
 * 2.2.6.10 disassembly (IAR cstartup_M, Armv8-M variant; no source path is
 * retained).
 *
 * Stock range: 0x005e4254..0x005e426f (literal 0x5e426c = 0xfef5eda5).
 * Reached from reset_handler_5e4232 (runtime/a-67-iar-startup) after it sets
 * MSPLIM/PSPLIM. It pushes the Armv8-M stack-sealing value 0xfef5eda5 twice,
 * points PSP at that seal, then calls the FPU enable 0x5e4270 (CPACR CP10/CP11
 * full access, DSB/ISB, FPSCR = 0x02040000) and __cmain 0x5e4294, which never
 * returns (__low_level_init 0x5e4228, __iar_data_init3 0x5e42b4, main
 * 0x5ce01e, exit 0x5e42dc). The bootloader twin is opencfw_boot_stack_entry
 * (apollo-bootloader/startup/reset.S, stock 0x43293c).
 *
 * Written as a naked function so the stack is not touched before the seal is
 * pushed. Profile g2-apollo-main-2. */
#include <stdint.h>

/* No definition in g2/src yet: stock 0x5e4270..0x5e4293 (__iar_init_vfp). */
extern void iar_init_vfp_5e4270(void);
/* No definition in g2/src yet: stock 0x5e4294..0x5e42b3 (__cmain). */
extern void iar_cmain_5e4294(void) __attribute__((noreturn));

void iar_program_start_5e4254(void) __attribute__((naked, noreturn));

/* Stock 0x005e4254 (__iar_program_start) */
void iar_program_start_5e4254(void)
{
    __asm volatile(
        "ldr    r0, =0xfef5eda5\n\t"
        "mov    r1, r0\n\t"
        "push   {r0, r1}\n\t"
        "mov    r0, sp\n\t"
        "msr    psp, r0\n\t"
        "nop.w\n\t"
        "bl     iar_init_vfp_5e4270\n\t"
        "bl     iar_cmain_5e4294\n\t"
        ".ltorg\n\t");
}
