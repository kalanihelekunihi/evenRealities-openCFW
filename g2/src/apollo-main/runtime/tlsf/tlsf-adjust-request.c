#include <stdint.h>

extern void g2_file_close_error(const char *message,
                                const char *file, uint32_t line); /* 0x4d09b4 */

/* Native 0x4cfec2..0x4cfeed, including the assertion reporting
 * side effect for a non-power-of-two alignment. */
uint32_t g2_tlsf_align_up(uint32_t size, uint32_t alignment) {
    if ((alignment & (alignment - 1u)) != 0u)
        g2_file_close_error((const char *)(uintptr_t)0x7106e4u,
                            (const char *)(uintptr_t)0x71a23cu, 471u);
    return (size + alignment - 1u) & ~(alignment - 1u);
}

/* Native 0x4cff42..0x4cff6b. Bounds at ROM 0x78f4c4/0x78f4c8
 * are authenticated TLSF constants 12 and 0x40000000. */
uint32_t g2_tlsf_adjust_request(uint32_t size, uint32_t alignment) {
    if (size == 0u)
        return 0u;
    const uint32_t aligned = g2_tlsf_align_up(size, alignment);
    const uint32_t maximum =
        *(volatile const uint32_t *)(uintptr_t)0x78f4c8u;
    if (aligned >= maximum)
        return 0u;
    const uint32_t minimum =
        *(volatile const uint32_t *)(uintptr_t)0x78f4c4u;
    if (minimum < aligned)
        return aligned;
    return *(volatile const uint32_t *)(uintptr_t)0x78f4c4u;
}
