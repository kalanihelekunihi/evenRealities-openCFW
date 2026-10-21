/* SPDX-License-Identifier: MIT
 * Native image-A XIP DMA descriptor graph: 0x10203828..0x10203a47 and
 * 0x10203c60..0x10203c73. Retained Ghidra bodies, pinned GX8002 DMA
 * layout, and 0x10203a48 literal (0x2002e93c) are the attribution inputs.
 * Hardware/runtime equality and final source data placement remain open.
 */
#include <stdint.h>

extern void gx8002_xip_dma_clear_10203804(uint32_t channel);

uint32_t gx8002_xip_virt_to_dma_10203c60(uint32_t address)
{
    if (address + UINT32_C(0xf0000000) < UINT32_C(0x20000000))
        return address & UINT32_C(0x07ffffff);
    return address;
}

void gx8002_xip_dma_descriptors_10203828(
    const uint32_t *initial, uint32_t *output, int32_t count,
    int32_t length, uint8_t element_bytes)
{
    static const uint16_t stride_table[4] = {0x0fff, 0xf001, 0, 0};
    uint32_t source_step = (uint32_t)element_bytes *
        stride_table[(initial[3] & 0x3ffu) >> 9];
    uint32_t target_step = (uint32_t)element_bytes *
        stride_table[(initial[3] & 0xffu) >> 7];
    int32_t index = 0;
    while (index < count - 1) {
        output[0] = initial[0] + (uint32_t)index * source_step;
        output[1] = initial[1] + (uint32_t)index * target_step;
        output[3] = initial[3];
        output[4] = 0xfffu;
        output[2] = gx8002_xip_virt_to_dma_10203c60(
            (uint32_t)(uintptr_t)(output + 6));
        ++index;
        output += 6;
    }
    output[0] = initial[0] + (uint32_t)index * source_step;
    output[1] = initial[1] + (uint32_t)index * target_step;
    output[3] = initial[3] & UINT32_C(0xe7ffffff);
    int32_t final_length = length % 0xfff;
    if (final_length == 0) final_length = 0xfff;
    output[4] = (uint32_t)final_length;
    output[2] = 0;
}

int32_t gx8002_xip_dma_configure_102038f4(
    uint32_t source, uint32_t target, uint32_t length,
    uint32_t channel, const uint32_t *input)
{
    uint32_t control = (input[6] << 11) | (input[1] << 14) |
        UINT32_C(0x18000001) | (input[0] << 1) | (input[0] << 4);
    if (input[7] > 1u || input[2] > 1u || input[9] > 3u ||
        input[4] > 3u || input[10] > 1u || input[5] > 1u)
        return -1;
    if (input[7]) control |= 0x100u;
    if (input[2]) control |= 0x400u;
    control |= input[9] << 23;
    control |= input[4] << 25;
    control |= input[11] << 20;
    uint32_t mode = (input[10] << 10) | (input[5] << 11);

    gx8002_xip_dma_clear_10203804(channel);
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e93c);
    uint32_t controller = *(volatile uint32_t *)(const void *)state;
    volatile uint8_t *const registers =
        (volatile uint8_t *)(uintptr_t)(controller + channel * 0x58u);
    uint32_t initial[4] = {
        gx8002_xip_virt_to_dma_10203c60(target),
        gx8002_xip_virt_to_dma_10203c60(source), 0, control
    };
    *(volatile uint32_t *)(void *)(registers + 0x00u) = initial[0];
    *(volatile uint32_t *)(void *)(registers + 0x08u) = initial[1];
    *(volatile uint32_t *)(void *)(registers + 0x18u) = control;
    *(volatile uint32_t *)(void *)(registers + 0x40u) = mode;
    *(volatile uint32_t *)(void *)(registers + 0x44u) =
        (input[8] << 11) | (input[3] << 7) | 2u;

    int32_t signed_length = (int32_t)length;
    int32_t count = signed_length / 0xfff;
    if (signed_length != count * 0xfff) ++count;
    if ((uint32_t)count * 0x18u > 0x1a0u) return -1;
    volatile const uint32_t *const state_words =
        (volatile const uint32_t *)(const void *)state;
    uint32_t *const descriptors =
        (uint32_t *)(uintptr_t)state_words[0xda + channel];
    uint32_t width = 1u;
    uint32_t width_shift = input[0] & 0x3fu;
    __asm__ volatile("lsl %0, %1" : "+r"(width) : "r"(width_shift) : "cc");
    gx8002_xip_dma_descriptors_10203828(
        initial, descriptors, count, signed_length, (uint8_t)width);
    *(volatile uint32_t *)(void *)(registers + 0x10u) =
        gx8002_xip_virt_to_dma_10203c60(
            (uint32_t)(uintptr_t)descriptors);
    return 0;
}
