/* SPDX-License-Identifier: MIT
 * Loaded image B native 0x10003128..0x1000313f.
 * Stock clears aligned words from 0x20017090 to 0x2002d79c.
 *
 * Wave 6: stock span is authoritative. Named symbols are exported for the
 * final linker script (PROVIDE) so a relocated image can override.
 */
#include <stdint.h>

#ifndef G2_IMAGE_B_BSS_START
#define G2_IMAGE_B_BSS_START UINT32_C(0x20017090)
#endif
#ifndef G2_IMAGE_B_BSS_END
#define G2_IMAGE_B_BSS_END   UINT32_C(0x2002d79c)
#endif

__attribute__((section(".opencfw.abs.bss_start"), used))
char gx8002_image_b_bss_start[1];
__attribute__((section(".opencfw.abs.bss_end"), used))
char gx8002_image_b_bss_end[1];

/* Stock 0x10003128 (gx8002_backup_clear_bss) */
void gx8002_image_b_clear_bss_10003128(void)
{
    for (uintptr_t address = (uintptr_t)G2_IMAGE_B_BSS_START;
         address < (uintptr_t)G2_IMAGE_B_BSS_END;
         address += sizeof(uint32_t))
        *(volatile uint32_t *)address = 0u;
    (void)gx8002_image_b_bss_start;
    (void)gx8002_image_b_bss_end;
}
