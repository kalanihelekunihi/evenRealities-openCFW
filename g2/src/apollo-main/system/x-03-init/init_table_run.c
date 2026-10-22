/* Prioritised init-function table runner, native 0x5bf0b4..0x5bf0bb
 * (comparator) and 0x5bf0bc..0x5bf103 (runner), literal pool
 * 0x5bf104..0x5bf113. Source file unknown (no log strings); it links between
 * FreeType's ftgzip.c and the LegalRegulatory page. Called once from main()
 * 0x5ce01e (product\s200\app\config\main.c) right after the 200 ms boot delay
 * and before ">>> SYSTEM BOOT START <<<".
 *
 * The table is a linker-collected ROM section of 8-byte {fn, priority}
 * records, 0x6d1e0c..0x6d1ec3 in 2.2.6.10 (23 entries; the first ones are
 * priority 0x64/1/1/1/0 ..., e.g. the board init 0x5cdd14 at priority 0). It is
 * copied (at most 256 records) to RAM, sorted by ascending priority with the
 * IAR DLIB qsort and every non-NULL function is called in order. */
#include <stdint.h>

typedef struct {
    void (*fn)(void);   /* +0x0 */
    int32_t priority;   /* +0x4 */
} g2_init_entry_t;
_Static_assert(sizeof(g2_init_entry_t) == 8u, "init table record");

#define INIT_TABLE_MAX 256u

/* Linker section bounds (IAR __section_begin/__section_end). */
extern const g2_init_entry_t g2_init_table_start_6d1e0c[]; /* ROM 0x6d1e0c */
extern const g2_init_entry_t g2_init_table_end_6d1ec4[];   /* ROM 0x6d1ec4 */
extern g2_init_entry_t g2_init_table_sorted_20066a30[INIT_TABLE_MAX]; /* RAM 0x20066a30 */

extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void audio_uart_ft_qsort_567c4c(void *base, uint32_t count, uint32_t width,
                                       int32_t (*compare)(const void *, const void *));

int32_t init_table_priority_compare_5bf0b4(const void *a, const void *b);
void auto_init_table_run_5bf0bc(void);

int32_t init_table_priority_compare_5bf0b4(const void *a, const void *b)
{
    return ((const g2_init_entry_t *)a)->priority - ((const g2_init_entry_t *)b)->priority;
}

void auto_init_table_run_5bf0bc(void)
{
    uint32_t count = (uint32_t)(((uintptr_t)g2_init_table_end_6d1ec4 -
                                 (uintptr_t)g2_init_table_start_6d1e0c) >> 3);
    uint32_t i;

    if (count >= INIT_TABLE_MAX + 1u)
        count = INIT_TABLE_MAX;
    (void)audio_queue_copy_bytes(g2_init_table_sorted_20066a30, g2_init_table_start_6d1e0c,
                                 count * sizeof(g2_init_entry_t));
    audio_uart_ft_qsort_567c4c(g2_init_table_sorted_20066a30, count, sizeof(g2_init_entry_t),
                               init_table_priority_compare_5bf0b4);
    for (i = 0u; i < count; i++) {
        if (g2_init_table_sorted_20066a30[i].fn != 0)
            g2_init_table_sorted_20066a30[i].fn();
    }
}
