/* Two TLSF leaf functions with stock configuration-word addresses. */
#include <stdint.h>
void *g2_tlsf_block_from_ptr(void *pointer) { /* stock 0x4cfe04 */
    uint32_t offset=*(volatile const uint32_t *)(uintptr_t)0x78f4c0u;
    return (void *)((uintptr_t)pointer-offset);
}
int32_t g2_tlsf_block_is_free(void *block) { /* stock 0x4cfdb4 */
    uint32_t value=*(uint32_t *)((uint8_t *)block+4u);
    uint32_t mask=*(volatile const uint32_t *)(uintptr_t)0x78f4b4u;
    return (int32_t)(value&mask);
}
