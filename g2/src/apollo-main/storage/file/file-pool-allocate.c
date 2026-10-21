#include <stdint.h>

/* Pinned TLSF/native 0x4d0722..0x4d0743. The three helper effects
 * retain separate native contracts. */
extern uint32_t g2_tlsf_adjust_request(uint32_t size, uint32_t alignment); /* 0x4cff42 */
extern void *g2_tlsf_find_suitable(void *pool, uint32_t size); /* 0x4d0484 */
extern void *g2_tlsf_prepare_allocation(void *pool, void *block,
                                         uint32_t size); /* 0x4d04e6 */

void *g2_file_pool_allocate(void *pool, uint32_t size) {
    const uint32_t adjusted = g2_tlsf_adjust_request(size, 4u);
    void *const block = g2_tlsf_find_suitable(pool, adjusted);
    return g2_tlsf_prepare_allocation(pool, block, adjusted);
}
