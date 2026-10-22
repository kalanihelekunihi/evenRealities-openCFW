/* Loaded image B native 0x10003128..0x1000313f.
 * Stock clears aligned words from 0x20017090 to 0x2002d79c; a relocated
 * source image must provide these bounds as linker symbols.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_bss_start[];
extern uint32_t gx8002_image_b_bss_end[];

/* Stock 0x10003144 (gx8002_backup_bss_bounds) */
void gx8002_image_b_clear_bss_10003128(void)
{
    volatile uint32_t *cursor = gx8002_image_b_bss_start;
    volatile uint32_t *end = gx8002_image_b_bss_end;
    while ((uintptr_t)cursor < (uintptr_t)end)
        *cursor++ = 0u;
}
