/* SPDX-License-Identifier: MIT
 * Stock 0x43299c walks four fixed scatter-initialization records. The source
 * build supplies their descriptors directly as C data and calls the same
 * adapters in stock order. This removes the self-relative callback words that
 * previously required init_records.S; no executable stock bytes are involved.
 */
#include <stdint.h>
extern uint32_t *opencfw_boot_zero_adapter(uint32_t *table);
extern uint32_t *opencfw_boot_expand_adapter(uint32_t *record);

/* First record: two zero spans followed by the terminator. */
static const uint32_t zero_record[] = {
    0x26c6cu, 0x2000055cu, 0x74100u, 0x20081000u, 0u,
};
/* The expand adapter recognizes these authenticated output descriptors and
 * installs source-owned ITCM and SRAM data. The input offsets are unused. */
static const uint32_t itcm_record[] = {0u, 22u << 1, 0x40u};
static const uint32_t initialized_sram_record[] = {0u, 625u << 1, 0x20000000u};
static const uint32_t zero_sram_record[] = {0u, 48u << 1, 0x20080000u};

/* Stock 0x43299C (init_array_run_43299c; IAR __iar_data_init3) */
void opencfw_boot_init_records_run(void) {
    /* The adapters predate this C table and accept mutable pointers, but only
     * read the descriptors. Keeping them const makes them available in ROM
     * before the startup routine has initialized writable memory. */
    (void)opencfw_boot_zero_adapter((uint32_t *)zero_record);
    (void)opencfw_boot_expand_adapter((uint32_t *)itcm_record);
    (void)opencfw_boot_expand_adapter((uint32_t *)initialized_sram_record);
    (void)opencfw_boot_expand_adapter((uint32_t *)zero_sram_record);
}
/* Stock 0x432910 (vector_table_relocate_432910; __low_level_init) */
uint32_t opencfw_boot_vector_base_init(void) {
    *(volatile uint32_t *)(uintptr_t)0xe000ed08=0x410000;
    return 1;
}
