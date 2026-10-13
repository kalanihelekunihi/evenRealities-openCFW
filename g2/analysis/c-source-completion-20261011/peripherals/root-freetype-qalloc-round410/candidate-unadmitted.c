#include <stdint.h>

/* Whole native ft_mem_qalloc body at 0x529176..0x52919c (38 bytes).
 * Pinned FreeType 2.9.1 src/base/ftutil.c supplies the source contract. */
void *audio_uart_ft_mem_qalloc_529176(void *memory, int32_t size, int32_t *error)
{
    void *block = 0;
    int32_t status = 0;
    if (size > 0) {
        const uint8_t *p = (const uint8_t *)memory + 4u;
        uint32_t callback = (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
                            ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
        block = ((void *(*)(void *, int32_t))(uintptr_t)callback)(memory, size);
        if (block == 0)
            status = 64;
    } else if (size < 0) {
        status = 6;
    }
    *error = status;
    return block;
}
