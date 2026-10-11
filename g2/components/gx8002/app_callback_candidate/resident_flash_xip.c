/* SPDX-License-Identifier: MIT
 * Image-A SRAM flash device/XIP configuration, 0x100242ec and 0x1002436c.
 * MMIO bases and bit positions are from direct native C-SKY instructions.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_flash_command_read_23684(
    uint32_t command, uint8_t *destination, int32_t bytes);
extern uint32_t gx8002_resident_flash_command_write_236dc(
    uint32_t command, const uint8_t *data, int32_t bytes);
extern uint32_t gx8002_resident_flash_wait_ready_2375c(void);
extern uint32_t gx8002_resident_flash_write_enable_2374c(void);

uint32_t gx8002_resident_flash_device_config_242ec(void)
{
    uint8_t config;
    gx8002_resident_flash_command_read_23684(0x15u, &config, 1);
    if ((config & 0x10u) == 0u) {
        config |= 0x10u;
        gx8002_resident_flash_wait_ready_2375c();
        gx8002_resident_flash_write_enable_2374c();
        gx8002_resident_flash_command_write_236dc(0x11u, &config, 1);
        gx8002_resident_flash_wait_ready_2375c();
    }
    return 0u;
}

uint32_t gx8002_resident_xip_initialize_2436c(
    uint32_t command, uint32_t command_width, uint32_t address_width,
    uint32_t dummy_cycles, uint32_t data_width, uint32_t unused,
    uint32_t continuous, uint32_t mode, uint32_t mode_width)
{
    (void)unused;
    volatile uint32_t *const spi =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const xip =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000100);
    volatile uint32_t *const controller =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300080);
    spi[0x08u / 4u] = 0u;
    uint32_t command_mode;
    if (command_width == 0u) command_mode = 0u;
    else if (command_width == 4u) command_mode = 1u;
    else if (command_width == 8u) command_mode = 2u;
    else if (command_width == 16u) command_mode = 3u;
    else return UINT32_MAX;

    uint32_t address_mode;
    uint32_t address_half = address_width >> 1;
    uint32_t data_half = data_width >> 1;
    uint32_t mode_half = mode_width >> 1;
    if (address_half == 0u) {
        if (data_half == 0u) address_mode = 0u;
        else if (data_half == mode_half) address_mode = 1u;
        else return UINT32_MAX;
    } else {
        if (address_half != mode_half || data_half != mode_half)
            return UINT32_MAX;
        address_mode = 2u;
    }
    if ((dummy_cycles & 3u) != 0u) return UINT32_MAX;
    uint32_t config = (mode << 13) | UINT32_C(0xc00000) |
                      ((dummy_cycles >> 2) << 4) | mode_half |
                      (command_mode << 9) | (address_mode << 2);
    if (continuous == 1u) config |= UINT32_C(0x08001000);
    xip[0x14u / 4u] = 0xffu;
    xip[0x08u / 4u] = config;
    xip[0x0cu / 4u] = 1u;
    xip[0] = command;
    xip[0x04u / 4u] = command;
    controller[0x10u / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
    return 0u;
}
