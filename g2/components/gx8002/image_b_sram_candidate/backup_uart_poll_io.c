/* SPDX-License-Identifier: MIT
 * Image-B polled UART byte write/read at 0x100045a0/0x100045d8.
 * Native write translates LF into CR,LF and waits on status bit5 before
 * each write; read waits on bit0 and returns the requested positive count.
 */
#include <stdint.h>

static volatile uint32_t *port_registers(uint32_t port)
{
    volatile uint32_t *record = (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x20016b84) + port * 128u);
    return (volatile uint32_t *)(uintptr_t)record[1];
}

void gx8002_image_b_uart_poll_write_100045a0(uint32_t port, uint32_t value)
{
    volatile uint32_t *registers = port_registers(port);
    if (value == 10u) {
        while ((registers[5] & 32u) == 0u) { }
        registers[0] = 13u;
    }
    while ((registers[5] & 32u) == 0u) { }
    registers[0] = value & 0xffu;
}

int32_t gx8002_image_b_uart_poll_read_100045d8(
    uint32_t port, uint8_t *destination, int32_t count)
{
    if (count <= 0) return 0;
    for (int32_t index = 0; index < count; ++index) {
        volatile uint32_t *registers = port_registers(port);
        while ((registers[5] & 1u) == 0u) { }
        destination[index] = (uint8_t)registers[0];
    }
    return count;
}

int32_t gx8002_image_b_uart_poll_write_buffer_10004614(
    uint32_t port, const uint8_t *source, int32_t count)
{
    if (count <= 0) return 0;
    volatile uint32_t *registers = port_registers(port);
    for (int32_t index = 0; index < count; ++index) {
        uint8_t value = source[index];
        while ((registers[5] & 32u) == 0u) { }
        registers[0] = value;
    }
    return count;
}
