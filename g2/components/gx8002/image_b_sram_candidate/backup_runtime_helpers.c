/* SPDX-License-Identifier: MIT
 * Image-B native 0x100113c4 byte-fill and 0x10004844 IRQ registration.
 * IRQ descriptor base and enable register come from pinned DAT literals
 * 0x10004864/0x10004868, respectively.
 */
#include <stdint.h>

typedef uint32_t __attribute__((may_alias)) gx8002_image_b_word;
extern volatile uint32_t gx8002_image_b_irq_descriptors_200173a8[64];

void gx8002_image_b_zero_100113c4(
    void *destination, uint32_t byte_value, uint32_t bytes)
{
    uint8_t *cursor = (uint8_t *)destination;
    uint8_t value = (uint8_t)byte_value;
    while (bytes != 0u && ((uintptr_t)cursor & 3u) != 0u) {
        *cursor++ = value;
        --bytes;
    }
    uint32_t pattern = UINT32_C(0x01010101) * value;
    while (bytes >= 16u) {
        gx8002_image_b_word *words = (gx8002_image_b_word *)(void *)cursor;
        words[0] = pattern;
        words[1] = pattern;
        words[2] = pattern;
        words[3] = pattern;
        cursor += 16;
        bytes -= 16;
    }
    while (bytes >= 4u) {
        *(gx8002_image_b_word *)(void *)cursor = pattern;
        cursor += 4;
        bytes -= 4;
    }
    while (bytes != 0u) {
        *cursor++ = value;
        --bytes;
    }
}

void gx8002_image_b_request_irq_10004844(
    uint32_t line, int32_t (*handler)(int32_t, void *), uint32_t argument)
{
    if (line >= 32u || handler == 0) return;
    volatile uint32_t *descriptor =
        &gx8002_image_b_irq_descriptors_200173a8[line * 2u];
    descriptor[0] = (uint32_t)(uintptr_t)handler;
    descriptor[1] = argument;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100) = 1u << line;
}
