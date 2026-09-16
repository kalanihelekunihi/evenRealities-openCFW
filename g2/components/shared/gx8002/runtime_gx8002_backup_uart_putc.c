/* SPDX-License-Identifier: MIT */
/* Backup console writer: descriptor stride 128, MMIO pointer at offset four. */
#include <stdint.h>
extern unsigned char backup_uart_descriptors[];
void backup_uart_putc(int port, int character)
{
    uintptr_t descriptor = (uintptr_t)backup_uart_descriptors + ((uint32_t)port << 7);
    volatile uint32_t *registers = *(volatile uint32_t **)(descriptor + 4u);
    if (character == 10) {
        while (!(registers[5] & 32u)) {}
        registers[0] = 13;
    }
    while (!(registers[5] & 32u)) {}
    registers[0] = (unsigned char)character;
}
