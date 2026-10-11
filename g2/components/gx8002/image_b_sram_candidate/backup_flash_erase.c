/* SPDX-License-Identifier: MIT
 * Image-B 0x1000764c: erase an address range in 4 KiB/64 KiB sectors.
 * The flash descriptor at 0x20016d60 is an independently initialized
 * image-B SRAM object; this body does not manufacture its product values.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length);
extern uint32_t gx8002_image_b_flash_write_10006cb0(
    uint32_t command, const uint8_t *source, uint32_t length);

static void wait_ready(void)
{
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
}

static uint8_t address_byte(uint32_t address, uint32_t shift)
{
    /* Native variable LSR takes a six-bit shift count. */
    shift &= 63u;
    return shift >= 32u ? 0u : (uint8_t)(address >> shift);
}

int32_t gx8002_image_b_flash_erase_1000764c(
    uint32_t address, uint32_t length)
{
    volatile uint8_t *const descriptor =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20016d60);
    uint32_t limit = *(volatile uint32_t *)(const void *)(descriptor + 4u);
    if (address >= limit) return -22;

    uint32_t end = address + length;
    if (end > limit) end = limit;
    uint32_t sector_address = address & ~UINT32_C(0xfff);
    uint32_t remaining = end - sector_address;
    while (remaining != 0u) {
        uint32_t sector_size;
        uint32_t command;
        if ((sector_address & 0x7fffu) == 0u && remaining >= 0x10000u) {
            sector_size = 0x10000u;
            command = 0xd8u;
            remaining -= sector_size;
        } else {
            sector_size = 0x1000u;
            command = 0x20u;
            remaining = remaining < sector_size ? 0u : remaining - sector_size;
        }

        wait_ready();
        (void)gx8002_image_b_flash_write_10006cb0(6u, (const uint8_t *)0, 0u);
        uint32_t address_width = *(volatile uint32_t *)(const void *)(descriptor + 8u);
        uint32_t shift = (address_width + UINT32_C(0x1fffffff)) * 8u;
        descriptor[0x11u] = address_byte(sector_address, shift);
        descriptor[0x12u] = address_byte(sector_address, shift - 8u);
        descriptor[0x13u] = address_byte(sector_address, shift - 16u);
        descriptor[0x14u] = address_byte(sector_address, shift - 24u);
        (void)gx8002_image_b_flash_write_10006cb0(
            command, (const uint8_t *)(const void *)(descriptor + 0x11u), 3u);
        wait_ready();
        sector_address += sector_size;
    }
    return 0;
}

void gx8002_image_b_flash_erase_full_10007f64(void)
{
    volatile const uint32_t *const descriptor =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20016d60);
    (void)gx8002_image_b_flash_erase_1000764c(0u, descriptor[1]);
}
