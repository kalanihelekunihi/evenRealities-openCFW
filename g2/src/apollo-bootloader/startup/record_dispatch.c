/* SPDX-License-Identifier: MIT
 * Stock 0x43299c is a scatter-initialization record walker, not a conventional
 * constructor array. Callbacks return the next record; each callback offset
 * is relative to its own slot. Fixed table bounds belong to this locked image.
 */
#include <stdint.h>
extern const uint32_t opencfw_boot_init_records[18];
void opencfw_boot_init_records_run(void) {
    const uint32_t *cursor=opencfw_boot_init_records;
    const uint32_t *end=opencfw_boot_init_records+18;
    while(cursor!=end) {
        uintptr_t callback=(uintptr_t)cursor+*cursor;
        cursor=((const uint32_t *(*)(const uint32_t *))callback)(cursor+1);
    }
}
uint32_t opencfw_boot_vector_base_init(void) {
    *(volatile uint32_t *)(uintptr_t)0xe000ed08=0x410000;
    return 1;
}
