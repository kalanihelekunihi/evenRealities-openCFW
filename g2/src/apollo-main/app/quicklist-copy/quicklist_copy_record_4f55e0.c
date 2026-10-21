/* Apollo QuickList record conversion 0x4f55e0..0x4f5635. */
#include <stdint.h>

extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */

void audio_quicklist_copy_record_4f55e0(const void *source, void *destination) {
    if (source == 0 || destination == 0)
        return;
    const uint8_t *const src = (const uint8_t *)source;
    uint8_t *const dst = (uint8_t *)destination;
    *(uint32_t *)(void *)(dst + 0x10cu) = *(const uint32_t *)(const void *)src;
    *(uint32_t *)(void *)(dst + 0x110u) = *(const uint32_t *)(const void *)(src + 4u);
    dst[0x121u] = src[8u];
    *(uint32_t *)(void *)(dst + 0x118u) = *(const uint32_t *)(const void *)(src + 16u);
    *(uint32_t *)(void *)(dst + 0x11cu) = *(const uint32_t *)(const void *)(src + 20u);
    dst[0x120u] = src[24u];
    uint16_t length = *(const uint16_t *)(const void *)(src + 0xe2u);
    if (length > 200u)
        length = 200u;
    (void)audio_queue_copy_bytes(dst, src + 25u, length);
    dst[length] = 0u;
}
