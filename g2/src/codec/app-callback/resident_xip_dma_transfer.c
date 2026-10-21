/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10203b78..0x10203bb9: configure, enable mask,
 * source-owned cache clean, then start. Full DMA descriptor construction
 * is a genuine imported 0x102038f4 C body until reduced separately.
 */
#include <stdint.h>

extern int32_t gx8002_xip_dma_configure_102038f4(
    uint32_t source, uint32_t target, uint32_t length,
    uint32_t channel, const uint32_t *descriptor);
extern void g2_codec_header_sync(void *address, uint32_t bytes);

int32_t gx8002_xip_dma_transfer_10203b78(
    uint32_t source, uint32_t target, uint32_t length,
    uint32_t channel, const uint32_t *descriptor)
{
    int32_t result = gx8002_xip_dma_configure_102038f4(
        source, target, length, channel, descriptor);
    if (result == -1) return result;
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e93c);
    uint32_t register_base =
        *(volatile uint32_t *)(void *)(state + 0u);
    volatile uint8_t *registers =
        (volatile uint8_t *)(uintptr_t)register_base;
    uint32_t mask = UINT32_C(0x101);
    __asm__ volatile("lsl %0, %1" : "+r"(mask) : "r"(channel) : "cc");
    *(volatile uint32_t *)(void *)(registers + 0x310u) = mask;
    uint32_t descriptor_address =
        *(volatile uint32_t *)(void *)(state + 0x368u + channel * 4u);
    g2_codec_header_sync((void *)(uintptr_t)descriptor_address, 0x1a0u);
    register_base = *(volatile uint32_t *)(void *)(state + 0u);
    registers = (volatile uint8_t *)(uintptr_t)register_base;
    *(volatile uint32_t *)(void *)(registers + 0x3a0u) = mask;
    return 0;
}
