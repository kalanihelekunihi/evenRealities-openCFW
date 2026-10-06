/* SPDX-License-Identifier: MIT
 * Stock 0x43299c is a scatter-initialization record walker, not a conventional
 * constructor array. Callbacks return the next record; each callback offset
 * is relative to its own slot. Fixed table bounds belong to this locked image.
 */
#include <stdint.h>
void opencfw_boot_init_records_run(void) {
    uint32_t *cursor=(uint32_t *)(uintptr_t)0x4330d8;
    uint32_t *end=(uint32_t *)(uintptr_t)0x433120;
    while(cursor<end) {
        uintptr_t callback=(uintptr_t)cursor+*cursor;
        cursor=((uint32_t *(*)(uint32_t *))callback)(cursor+1);
    }
}
uint32_t opencfw_boot_vector_base_init(void) {
    *(volatile uint32_t *)(uintptr_t)0xe000ed08=0x410000;
    return 1;
}
