/* IAR __iar_init_vfp for the Apollo main image, reconstructed from the
 * 2.2.6.10 disassembly (IAR cstartup_M; no source path is retained).
 *
 * Stock range: 0x005e4270..0x005e4291 (0x5e4292 is alignment padding).
 * Called once from iar_program_start_5e4254 (C3-startup/iar_program_start.c)
 * before __cmain. Grants CP10/CP11 full access in CPACR (0xe000ed88 |=
 * 0x00f00000), synchronises with DSB/ISB, then writes FPSCR = 0x02040000
 * (DN = 1, LTPSIZE = 4 i.e. no tail predication, RMode = round to nearest,
 * FZ = 0). The bootloader twin is opencfw_boot_fpu_init
 * (apollo-bootloader/startup/fpu.S, stock 0x432958).
 *
 * The FPSCR write has no C form; it is a single inline vmsr. The `.fpu`
 * directive is needed because profile g2-apollo-main-2 is soft-float.
 * Profile g2-apollo-main-2. */
#include <stdint.h>

#define G2_SCB_CPACR      ((volatile uint32_t *)(uintptr_t)0xe000ed88u)
#define G2_CPACR_CP10_CP11 0x00f00000u
#define G2_FPSCR_STARTUP  0x02040000u

void iar_init_vfp_5e4270(void);

/* Stock 0x005e4270 (__iar_init_vfp) */
void iar_init_vfp_5e4270(void)
{
    *G2_SCB_CPACR |= G2_CPACR_CP10_CP11;
    __asm volatile("dsb sy\n\tisb sy" : : : "memory");
    __asm volatile(".fpu fpv5-d16\n\t"
                   "vmsr fpscr, %0"
                   :
                   : "r"(G2_FPSCR_STARTUP)
                   : "memory");
}
