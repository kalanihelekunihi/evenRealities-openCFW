/* SPDX-License-Identifier: MIT */
/* Image-A 0x16380: nine-argument XIP register configuration.
 * Parameter names describe observed fields; unsupported settings leave SPI
 * disabled, matching the original early-error path. */
#include <stdint.h>
#define REG(a) (*(volatile uint32_t *)(a))
int open_cfw_gx8002_flash_xip_config(unsigned command, unsigned command_bits,
    unsigned command_lines, unsigned address_bits, unsigned address_lines,
    unsigned unused, unsigned mode, unsigned wait_cycles, unsigned data_lines)
{
    (void)unused;
    command_lines >>= 1;
    address_lines >>= 1;
    data_lines >>= 1;
    REG(0xa2000008u) = 0;
    switch (command_bits) {
    case 0: break;
    case 4: command_bits=1; break;
    case 8: command_bits=2; break;
    case 16: command_bits=3; break;
    default: return -1;
    }
    if (command_lines) {
        if (command_lines != data_lines || address_lines != data_lines) return -1;
        address_lines = 2;
    } else if (address_lines) {
        if (address_lines != data_lines) return -1;
        address_lines = 1;
    }
    if (address_bits & 3u) return -1;
    uint32_t control = (wait_cycles << 13) | (3u << 22) |
        ((address_bits >> 2) << 4) | data_lines |
        (command_bits << 9) | (address_lines << 2);
    if (mode == 1) control |= (1u << 12) | (1u << 27);
    REG(0xa2000114u) = 255;
    REG(0xa2000108u) = control;
    REG(0xa200010cu) = 1;
    REG(0xa2000100u) = command;
    REG(0xa2000104u) = command;
    REG(0xa0300090u) = 0;
    REG(0xa2000008u) = 1;
    return 0;
}
