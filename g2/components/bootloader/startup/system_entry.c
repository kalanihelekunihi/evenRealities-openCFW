/* SPDX-License-Identifier: MIT
 * Stock 0x43297c call chain; reset, FPU and stack setup precede this entry.
 * These two platform providers remain explicitly unresolved here.
 */
#include <stdint.h>
extern uint32_t opencfw_boot_vector_base_init(void);
extern void opencfw_boot_init_records_run(void);
extern void opencfw_boot_platform_system_init(uint32_t argument);
extern void opencfw_boot_platform_terminal(void) __attribute__((noreturn));
void opencfw_boot_system_entry(void) {
    if(opencfw_boot_vector_base_init()!=0u)
        opencfw_boot_init_records_run();
    opencfw_boot_platform_system_init(0);
    opencfw_boot_platform_terminal();
}
