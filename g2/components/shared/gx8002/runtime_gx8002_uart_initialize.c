/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_uart_descriptors[2][32];
extern void open_cfw_gx8002_platform_gate(unsigned int, unsigned int);
extern unsigned int open_cfw_gx8002_clock_frequency(unsigned int);
extern int open_cfw_gx8002_uart_configure(volatile uint32_t *);

/* Stock package 0xcabc: snap clocks within 100 Hz of a MHz boundary. */
int open_cfw_gx8002_uart_initialize(uint32_t port, uint32_t baud)
{
    if (port >= 2) return -1;
    open_cfw_gx8002_platform_gate(17 + (port != 0), 1);
    uint32_t clock = open_cfw_gx8002_clock_frequency(16);
    uint32_t remainder = clock % 1000000u;
    if (remainder <= 100) clock -= remainder;
    else if (1000000u - remainder <= 100) clock += 1000000u - remainder;
    volatile uint32_t *descriptor = open_cfw_gx8002_uart_descriptors[port];
    descriptor[3] = clock;
    descriptor[4] = baud;
    return open_cfw_gx8002_uart_configure(descriptor);
}
