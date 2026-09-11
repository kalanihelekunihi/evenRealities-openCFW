/*
 * SPDX-License-Identifier: MIT
 *
 * Fixed-address initialized data authenticated at G2 bootloader addresses
 * 0x0043292A through 0x0043293C, 0x00432954 through 0x00432958,
 * 0x0043297A through 0x0043297C, and 0x0043299A through 0x0043299C.
 *
 * These four spans are not independent behavior: they are Thumb halfword
 * alignment padding and the PC-relative literal pool that the already
 * reviewed startup services in runtime_startup_services_432910.c and
 * runtime_startup_runtime_43297c.c load with fixed-offset "ldr rX, [pc,
 * #N]" instructions, plus one unreachable "b ." trap consistent with the
 * reviewed CMSIS/startup idiom of parking execution if it ever falls
 * through the constructor loop. Every naked leaf below places ordinary,
 * already-understood 32-bit constants -- register and RAM addresses named
 * by the CMSIS Cortex-M architecture and the process/main stack limit the
 * host test in test_runtime_bootloader_startup_services_432910.py already
 * exercises -- at its own fixed stock address; none of these leaves is
 * itself called, so each is documented individually rather than wrapped in
 * a synthetic accessor.
 *
 * See docs/research/g2-bootloader-startup-literal-pool-431e70-4329c4-closure.md
 * for the disassembly and derivation of every constant reproduced here.
 */

typedef __UINT32_TYPE__ open_cfw_startup_literal_u32;

#if defined(__arm__) || defined(__thumb__)

/*
 * 0x0043292A..0x0043293C (18 bytes): two bytes of alignment padding, then
 * the literal pool shared by open_cfw_bootloader_vector_table_relocate_432910
 * (the SCB->VTOR target 0x00410000, the run base of this image, and the
 * SCB_VTOR register address 0xE000ED08) and
 * open_cfw_bootloader_stack_limits_init_43291a (the process/main stack
 * limit 0x2007D000), an unreachable "b ." trap, and two more bytes of
 * alignment before open_cfw_bootloader_process_stack_init_43293c.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_startup_literal_pool_43292a(void)
{
    __asm volatile(
        ".short 0x0000\n"
        ".word 0x00410000\n"
        ".word 0xE000ED08\n"
        ".word 0x2007D000\n"
        "1: b 1b\n"
        ".short 0x0000\n"
    );
}

/*
 * 0x00432954..0x00432958 (4 bytes): the literal pool word that
 * open_cfw_bootloader_process_stack_init_43293c loads and pushes twice
 * (as both r0 and r1) onto the initial process stack -- the same
 * 0xFEF5EDA5 sentinel already exercised as the "process" argument to
 * open_cfw_bootloader_process_stack_init_43293c_portable in
 * test_runtime_bootloader_startup_services_432910.py.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_startup_literal_pool_432954(void)
{
    __asm volatile(".word 0xFEF5EDA5\n");
}

/*
 * 0x0043297A..0x0043297C (2 bytes): Thumb halfword alignment padding
 * between the end of open_cfw_bootloader_fpu_enable_432958 and the start
 * of open_cfw_bootloader_runtime_start_43297c.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_startup_literal_pool_43297a(void)
{
    __asm volatile(".short 0x0000\n");
}

/*
 * 0x0043299A..0x0043299C (2 bytes): Thumb halfword alignment padding
 * between the end of open_cfw_bootloader_runtime_start_43297c and the
 * start of open_cfw_bootloader_init_array_run_43299c.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_startup_literal_pool_43299a(void)
{
    __asm volatile(".short 0x0000\n");
}

#else

typedef struct open_cfw_startup_literal_pool_43292a {
    open_cfw_startup_literal_u32 vector_table_target;
    open_cfw_startup_literal_u32 scb_vtor_address;
    open_cfw_startup_literal_u32 stack_limit;
} open_cfw_startup_literal_pool_43292a;

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_startup_literal_pool_43292a_portable(
    open_cfw_startup_literal_pool_43292a *pool)
{
    pool->vector_table_target = 0x00410000U;
    pool->scb_vtor_address = 0xE000ED08U;
    pool->stack_limit = 0x2007D000U;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_startup_literal_u32 open_cfw_bootloader_startup_literal_pool_432954_portable(void)
{
    return 0xFEF5EDA5U;
}

#endif
