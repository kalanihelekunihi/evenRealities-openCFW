/* SPDX-License-Identifier: MIT
 * Image-B flash status/program helpers 0x10006d34 and 0x10007350.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length);
extern uint32_t gx8002_image_b_flash_write_10006cb0(
    uint32_t command, const uint8_t *source, uint32_t length);

int32_t gx8002_image_b_flash_program_command_10006d34(
    const uint8_t *source, uint32_t length, uint32_t mode)
{
    if (length > 2u) return -1;
    uint32_t command;
    if (mode == 2u) command = 0x31u;
    else if (mode == 3u) command = 0x11u;
    else if (mode == 1u) command = 1u;
    else return -1;
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
    (void)gx8002_image_b_flash_write_10006cb0(6u, (const uint8_t *)0, 0u);
    (void)gx8002_image_b_flash_write_10006cb0(command, source, length);
    return 0;
}

void gx8002_image_b_flash_wait_ready_10007350(void)
{
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
}

uint32_t gx8002_image_b_flash_set_status_bit_10007370(void)
{
    uint8_t status_pair[2];
    uint8_t second_status;
    (void)gx8002_image_b_flash_read_10006c30(5u, &status_pair[0], 1u);
    (void)gx8002_image_b_flash_read_10006c30(0x35u, &second_status, 1u);
    if ((second_status & 2u) == 0u) {
        status_pair[1] = second_status | 2u;
        (void)gx8002_image_b_flash_program_command_10006d34(
            status_pair, 2u, 1u);
        gx8002_image_b_flash_wait_ready_10007350();
    }
    return 0u;
}

uint32_t gx8002_image_b_flash_set_second_status_bit_100073b4(void)
{
    uint8_t status;
    (void)gx8002_image_b_flash_read_10006c30(0x35u, &status, 1u);
    if ((status & 2u) == 0u) {
        status |= 2u;
        (void)gx8002_image_b_flash_program_command_10006d34(&status, 1u, 2u);
        gx8002_image_b_flash_wait_ready_10007350();
    }
    return 0u;
}

uint32_t gx8002_image_b_flash_set_configuration_bit_100073f0(void)
{
    uint8_t status;
    (void)gx8002_image_b_flash_read_10006c30(0x15u, &status, 1u);
    if ((status & 0x10u) == 0u) {
        status |= 0x10u;
        (void)gx8002_image_b_flash_program_command_10006d34(&status, 1u, 3u);
        gx8002_image_b_flash_wait_ready_10007350();
    }
    return 0u;
}

/* The native descriptor lives in image-B SRAM and holds the write callback
 * at +0x18. Its initializer is a separate image-layout obligation. */
typedef uint32_t (*flash_page_write_fn)(uint32_t, const uint8_t *, uint32_t);

uint32_t gx8002_image_b_flash_program_pages_1000742c(
    uint32_t address, const uint8_t *source, uint32_t length)
{
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
    (void)gx8002_image_b_flash_write_10006cb0(6u, (const uint8_t *)0, 0u);

    const volatile uint32_t *const descriptor =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20016d60);
    flash_page_write_fn write_page =
        (flash_page_write_fn)(uintptr_t)descriptor[0x18u / 4u];
    uint32_t first = 0x100u - (address & 0xffu);
    if (((address & 0xffu) + length) <= 0x100u) {
        (void)write_page(address, source, length);
        return 0u;
    }
    (void)write_page(address, source, first);
    for (uint32_t offset = first; offset < length;) {
        uint32_t chunk = length - offset;
        if (chunk > 0x100u) chunk = 0x100u;
        (void)gx8002_image_b_flash_write_10006cb0(
            6u, (const uint8_t *)0, 0u);
        write_page = (flash_page_write_fn)(uintptr_t)descriptor[0x18u / 4u];
        (void)write_page(address + offset, source + offset, chunk);
        offset += chunk;
    }
    return 0u;
}
