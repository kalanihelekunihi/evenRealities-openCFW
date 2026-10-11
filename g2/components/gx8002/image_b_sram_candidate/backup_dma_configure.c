/* SPDX-License-Identifier: MIT
 * Image-B DMA configuration 0x100049d4. The settings word indices and
 * validation branches follow the retained native function.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_dma_bus_address_100051c4(uint32_t address);
extern void gx8002_image_b_dma_descriptors_100048d0(
    const uint32_t *parameters, uint32_t *descriptors,
    int32_t count, int32_t bytes, uint8_t scale);

static uint32_t native_shift(uint32_t value, uint32_t count)
{
    __asm__ volatile ("lsl %0, %1\n" : "+r"(value) : "r"(count));
    return value;
}

int32_t gx8002_image_b_dma_configure_100049d4(
    uint32_t source, uint32_t destination, int32_t bytes,
    uint32_t channel, const uint32_t *settings)
{
    uint32_t control = settings[6] << 11 | settings[1] << 14 |
        UINT32_C(0x18000001) | settings[0] * 2u | settings[0] << 4;
    if (settings[7] > 1u || settings[2] > 1u) return -1;
    if (settings[7] == 1u) control |= 0x100u;
    if (settings[2] == 1u) control |= 0x400u;
    if (settings[9] > 3u || settings[4] > 3u) return -1;
    control |= settings[9] << 23;
    control |= settings[4] << 25;
    control |= settings[11] << 20;
    uint32_t extra = 0u;
    if (settings[10] > 1u || settings[5] > 1u) return -1;
    if (settings[10] == 1u) extra |= 0x400u;
    if (settings[5] == 1u) extra |= 0x800u;

    volatile uint32_t *state = (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d3e8);
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)state[0];
    uint32_t bit = native_shift(1u, channel);
    registers[0x338u / 4u] = bit;
    registers[0x340u / 4u] = bit;
    registers[0x348u / 4u] = bit;
    registers[0x350u / 4u] = bit;
    registers[0x358u / 4u] = bit;
    uint32_t offset = channel * 0x58u;
    uint32_t parameter[4];
    parameter[0] = gx8002_image_b_dma_bus_address_100051c4(destination);
    registers[offset / 4u] = parameter[0];
    parameter[1] = gx8002_image_b_dma_bus_address_100051c4(source);
    registers[offset / 4u + 2u] = parameter[1];
    registers[offset / 4u + 6u] = control;
    registers[offset / 4u + 16u] = extra;
    registers[offset / 4u + 17u] = settings[8] << 11 | settings[3] << 7 | 2u;
    int32_t chunks = bytes / 0x0fff;
    chunks += (bytes != chunks * 0x0fff);
    if (UINT32_C(0x1a0) < (uint32_t)chunks * 24u) return -1;
    parameter[3] = control;
    uint32_t descriptor_address = state[0xdau + channel];
    uint8_t scale = (uint8_t)native_shift(1u, settings[0]);
    gx8002_image_b_dma_descriptors_100048d0(
        parameter, (uint32_t *)(uintptr_t)descriptor_address, chunks, bytes, scale);
    registers[offset / 4u + 4u] =
        gx8002_image_b_dma_bus_address_100051c4(descriptor_address);
    return 0;
}
