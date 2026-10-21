#include <stdint.h>

extern uint32_t g2_tlsf_fls(uint32_t word); /* native 0x4cfd66 */
extern void g2_tlsf_mapping_insert(uint32_t size,
                                   uint32_t *fl, uint32_t *sl); /* 0x4cff6c */
extern uint32_t g2_tlsf_block_size(void *block); /* 0x4cfd70 */
extern void g2_tlsf_remove_free_block(void *pool, void *block,
                                      uint32_t fl, uint32_t sl); /* 0x4d003a */
extern void g2_file_close_error(const char *message,
                                const char *file, uint32_t line);

/* Native 0x4cff9a..0x4cffc1. */
__attribute__((noinline))
void g2_tlsf_mapping_search(uint32_t size, uint32_t *fl, uint32_t *sl) {
    if (size >= 128u) {
        const uint32_t shift = g2_tlsf_fls(size) - 5u;
        size += (1u << shift) - 1u;
    }
    g2_tlsf_mapping_insert(size, fl, sl);
}

static uint32_t first_set(uint32_t bitmap) {
    return bitmap ? (uint32_t)__builtin_ctz(bitmap) : UINT32_MAX;
}

/* Native 0x4cffc2..0x4d0039. Control layout is from pinned TLSF. */
__attribute__((noinline))
void *g2_tlsf_search_suitable_block(void *pool, uint32_t *fl, uint32_t *sl) {
    const uint32_t initial_fl = *fl;
    const uint32_t initial_sl = *sl;
    uint32_t sl_bitmap = *(uint32_t *)((uint8_t *)pool + 20u + initial_fl * 4u)
                       & (UINT32_MAX << (initial_sl & 31u));
    uint32_t chosen_fl = initial_fl;
    if (sl_bitmap == 0u) {
        uint32_t const fl_bitmap = *(uint32_t *)((uint8_t *)pool + 16u)
                                 & (UINT32_MAX << ((initial_fl + 1u) & 31u));
        if (fl_bitmap == 0u)
            return 0;
        chosen_fl = first_set(fl_bitmap);
        *fl = chosen_fl;
        sl_bitmap = *(uint32_t *)((uint8_t *)pool + 20u + chosen_fl * 4u);
    }
    if (sl_bitmap == 0u)
        g2_file_close_error((const char *)(uintptr_t)0x71a278u,
                            (const char *)(uintptr_t)0x71a23cu, 568u);
    const uint32_t chosen_sl = first_set(sl_bitmap);
    *sl = chosen_sl;
    return *(void **)((uint8_t *)pool + 0x74u + chosen_fl * 128u
                      + chosen_sl * 4u);
}

/* Native 0x4d0484..0x4d04e5. */
void *g2_tlsf_find_suitable(void *pool, uint32_t size) {
    uint32_t fl = 0u, sl = 0u;
    void *block = 0;
    if (size != 0u) {
        g2_tlsf_mapping_search(size, &fl, &sl);
        if ((int32_t)fl < 24)
            block = g2_tlsf_search_suitable_block(pool, &fl, &sl);
    }
    if (block != 0) {
        if (g2_tlsf_block_size(block) < size)
            g2_file_close_error((const char *)(uintptr_t)0x7738ccu,
                                (const char *)(uintptr_t)0x71a23cu, 777u);
        g2_tlsf_remove_free_block(pool, block, fl, sl);
    }
    return block;
}
